"""
通义千问（Qwen）AI 模型服务
"""
import dashscope
from dashscope import Generation
from typing import Optional, Dict, Any, AsyncGenerator
from loguru import logger
import json
import asyncio

from app.core.config import settings


class QwenService:
    """通义千问服务类"""
    
    def __init__(self):
        """初始化服务"""
        self._api_key_configured = False
        if settings.DASHSCOPE_API_KEY:
            try:
                dashscope.api_key = settings.DASHSCOPE_API_KEY
                self._api_key_configured = True
            except Exception as e:
                logger.warning(f"配置 DASHSCOPE_API_KEY 失败: {str(e)}")
        else:
            logger.warning("DASHSCOPE_API_KEY 未配置，AI 功能将不可用")
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        生成文本内容
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            model: 模型名称（默认使用配置中的模型）
            temperature: 温度参数，控制随机性（0-1）
            max_tokens: 最大生成token数
            stream: 是否流式输出
        
        Returns:
            包含生成结果的字典
        """
        if not self._api_key_configured or not settings.DASHSCOPE_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY 未配置，请检查环境变量配置")
        
        model = model or settings.QWEN_MODEL
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = Generation.call(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                result_format='message'
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                return {
                    "success": True,
                    "content": content,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            else:
                logger.error(f"千问模型调用失败: {response.message}")
                return {
                    "success": False,
                    "error": response.message,
                    "code": response.status_code
                }
        except Exception as e:
            logger.error(f"调用千问模型时发生异常: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_document(
        self,
        doc_type: str,
        context: Dict[str, Any],
        template_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成文档内容
        
        Args:
            doc_type: 文档类型（如：案件卷宗、请示、汇报、工作总结等）
            context: 上下文信息（案件信息、表单数据等）
            template_hint: 模板提示（可选）
        
        Returns:
            包含生成文档内容的字典
        """
        # 构建系统提示词
        system_prompt = self._build_system_prompt(doc_type, template_hint)
        
        # 构建用户提示词
        user_prompt = self._build_user_prompt(doc_type, context)
        
        # 调用模型生成
        result = self.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        return result
    
    async def generate_document_stream(
        self,
        doc_type: str,
        context: Dict[str, Any],
        template_hint: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式生成文档内容（SSE格式）
        
        Args:
            doc_type: 文档类型
            context: 上下文信息
            template_hint: 模板提示（可选）
        
        Yields:
            SSE格式的数据块
        """
        if not self._api_key_configured or not settings.DASHSCOPE_API_KEY:
            yield f"data: {json.dumps({'error': 'DASHSCOPE_API_KEY 未配置'})}\n\n"
            return
        
        model = settings.QWEN_MODEL
        
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt(doc_type, template_hint)
            
            # 构建用户提示词
            user_prompt = self._build_user_prompt(doc_type, context)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})
            
            # 调用流式生成API
            # stream=True 时返回的是 generator，需要设置 incremental_output=True 获得增量输出
            responses = Generation.call(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000,
                stream=True,
                incremental_output=True,  # 增量输出，只返回新增内容
                result_format='message'
            )
            
            # 遍历流式响应（responses 是一个 generator）
            for response in responses:
                # 使用 asyncio.sleep(0) 让出控制权，避免阻塞
                await asyncio.sleep(0)
                
                # 检查响应状态
                if response.status_code == 200:
                    # 获取输出内容
                    if hasattr(response, 'output') and response.output:
                        if hasattr(response.output, 'choices') and response.output.choices:
                            choice = response.output.choices[0]
                            
                            # 获取增量内容
                            content = ''
                            
                            # 从 message.content 获取内容（增量输出模式）
                            if hasattr(choice, 'message'):
                                message = choice.message
                                if isinstance(message, dict):
                                    content = message.get('content', '')
                                elif hasattr(message, 'content'):
                                    content = message.content
                            
                            # 如果 choice 是字典类型
                            if not content and isinstance(choice, dict):
                                if 'message' in choice:
                                    msg = choice['message']
                                    if isinstance(msg, dict):
                                        content = msg.get('content', '')
                            
                            if content:
                                # 发送SSE格式的数据
                                yield f"data: {json.dumps({'content': content})}\n\n"
                else:
                    # 处理错误
                    error_msg = getattr(response, 'message', '生成失败')
                    error_code = getattr(response, 'code', '')
                    logger.error(f"千问模型流式调用失败: {error_msg} (code: {error_code})")
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                    break
            
            # 发送完成信号
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"流式生成文档时发生异常: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    def _build_system_prompt(self, doc_type: str, template_hint: Optional[str] = None) -> str:
        """构建系统提示词"""
        base_prompt = f"""你是一位专业的军事保卫部门文书写作助手。你的任务是帮助用户生成规范的{doc_type}文档。

要求：
1. 文档格式要符合军事机关公文规范
2. 内容要准确、严谨、条理清晰
3. 语言要正式、规范，符合公文写作要求
4. 必须严格以用户提供的案件/表单信息为基础生成内容，文书中的时间、人员、单位、经过、调查情况等只能使用用户给出的信息，不得编造或泛化
5. 使用 Markdown 格式输出文档内容
6. 直接输出 Markdown 内容，不要使用代码块包裹（不要使用 ```markdown 或 ```html 等）
7. 使用标准 Markdown 语法：标题用 #，段落用空行分隔，列表用 - 或 1.，加粗用 **，斜体用 *

"""
        if template_hint:
            base_prompt += f"模板说明：{template_hint}\n\n"
        
        base_prompt += "请根据用户提供的信息，生成规范的 Markdown 格式文档内容。"
        
        return base_prompt
    
    def _build_user_prompt(self, doc_type: str, context: Dict[str, Any]) -> str:
        """构建用户提示词"""
        prompt_parts = [f"请生成一份{doc_type}，具体要求如下：\n"]
        
        # 案件类文书：立案报告、调查报告、讯问笔录提纲、案件处理意见、案件卷宗等，均以第一步填写的案件信息为基础
        case_doc_types = [
            "立案报告", "调查报告", "讯问笔录提纲", "案件处理意见",
            "案件卷宗", "案件报告", "案件总结"
        ]
        if doc_type in case_doc_types:
            prompt_parts.append("\n【以下为第一步填写的案件线索信息，必须作为生成内容的唯一依据】\n")
            if context.get("caseInfo"):
                case_info = context["caseInfo"]
                prompt_parts.append("案件信息：\n")
                prompt_parts.append(f"- 案发时间：{case_info.get('incidentTime', '未提供')}\n")
                prompt_parts.append(f"- 案件类型：{case_info.get('caseType', '未提供')}\n")
                prompt_parts.append(f"- 涉案人员姓名：{case_info.get('personName', '未提供')}\n")
                prompt_parts.append(f"- 所属单位：{case_info.get('department', '未提供')}\n")
                if case_info.get('gender'):
                    prompt_parts.append(f"- 性别：{case_info.get('gender')}\n")
                if case_info.get('position'):
                    prompt_parts.append(f"- 职务/职级：{case_info.get('position')}\n")
                if case_info.get('enlistmentTime'):
                    prompt_parts.append(f"- 入伍时间：{case_info.get('enlistmentTime')}\n")
                if case_info.get('incidentProcess'):
                    prompt_parts.append(f"- 事发经过：{case_info.get('incidentProcess')}\n")
                if case_info.get('investigation'):
                    prompt_parts.append(f"- 初步调查情况：{case_info.get('investigation')}\n")
            else:
                prompt_parts.append("（未提供案件信息）\n")
            
            if context.get("relatedCases"):
                prompt_parts.append("\n参考/关联案件：\n")
                for case in context["relatedCases"]:
                    prompt_parts.append(f"- {case.get('caseNo', '')}：{case.get('caseName', '') or case.get('title', '')}\n")
            
            prompt_parts.append("\n【生成要求】必须严格以上述案件信息为基础生成本文书。文书中的时间、人员、单位、经过、调查情况等均只能使用上述内容，不得编造或使用泛化表述；若某项未提供则用“待补充”等表述，不要虚构。\n")
        
        elif doc_type in ["请示", "汇报", "通知", "函"]:
            prompt_parts.append("公文信息：\n")
            form_data = context.get("formData", {})
            if form_data.get("recipient"):
                prompt_parts.append(f"- 主送机关/收文对象：{form_data.get('recipient')}\n")
            if form_data.get("subject"):
                prompt_parts.append(f"- 主题：{form_data.get('subject')}\n")
            if form_data.get("content"):
                prompt_parts.append(f"- 内容：{form_data.get('content')}\n")
            if form_data.get("situation"):
                prompt_parts.append(f"- 工作情况：{form_data.get('situation')}\n")
            if form_data.get("problems"):
                prompt_parts.append(f"- 存在问题：{form_data.get('problems')}\n")
            if form_data.get("plan"):
                prompt_parts.append(f"- 下步计划：{form_data.get('plan')}\n")
            
            if context.get("selectedCase"):
                prompt_parts.append(f"\n关联案件：{context.get('selectedCase', {}).get('caseNo', '')}\n")
        
        elif doc_type in ["工作总结", "统计分析报告", "形势分析报告"]:
            prompt_parts.append("报告信息：\n")
            form_data = context.get("formData", {})
            if form_data.get("title"):
                prompt_parts.append(f"- 报告标题：{form_data.get('title')}\n")
            
            statistics = context.get("statistics", {})
            if statistics:
                prompt_parts.append(f"- 案件总数：{statistics.get('totalCases', 0)}件\n")
                prompt_parts.append(f"- 已办结：{statistics.get('completedCases', 0)}件\n")
                prompt_parts.append(f"- 待处理：{statistics.get('pendingCases', 0)}件\n")
                prompt_parts.append(f"- 办结率：{statistics.get('completionRate', 0)}%\n")
                
                if statistics.get("caseTypeDistribution"):
                    prompt_parts.append("\n案件类型分布：\n")
                    for item in statistics["caseTypeDistribution"]:
                        prompt_parts.append(f"- {item.get('name', '')}：{item.get('count', 0)}件，占比{item.get('percentage', 0)}%\n")
            
            if form_data.get("highlights"):
                prompt_parts.append(f"\n工作亮点：{form_data.get('highlights')}\n")
            if form_data.get("problems"):
                prompt_parts.append(f"\n存在问题：{form_data.get('problems')}\n")
            if form_data.get("plans"):
                prompt_parts.append(f"\n下步计划：{form_data.get('plans')}\n")
        
        elif doc_type == "会议纪要":
            # 会议纪要：根据会议录音转写稿或会议随记，整理成标准会议报告
            prompt_parts.append("\n【以下为会议录音转写内容或会议随记，请据此整理成规范的会议纪要】\n\n")
            meeting_transcript = context.get("meetingTranscript") or context.get("meeting_notes") or ""
            if meeting_transcript:
                prompt_parts.append("会议原始内容：\n")
                prompt_parts.append(meeting_transcript)
                prompt_parts.append("\n\n")
            if context.get("meetingTitle"):
                prompt_parts.append(f"会议主题：{context.get('meetingTitle')}\n")
            if context.get("meetingTime"):
                prompt_parts.append(f"会议时间：{context.get('meetingTime')}\n")
            prompt_parts.append("\n【生成要求】请将上述内容整理成标准会议纪要，结构需包含：一、会议基本信息（时间、地点、参会人员、主持等）；二、会议议题与讨论内容；三、议定事项或决议；四、待办与分工（如有）。内容必须严格基于上述原始内容，不得编造；若信息不全可标注“待补充”。\n")
        
        prompt_parts.append("\n请生成完整的文档内容，使用 Markdown 格式，包含适当的标题、段落、列表等格式。")
        prompt_parts.append("\n重要要求：")
        prompt_parts.append("\n1. 直接输出 Markdown 格式的内容，不要使用代码块包裹（不要使用 ```markdown 或 ```html 等）")
        prompt_parts.append("\n2. 使用标准的 Markdown 语法：标题用 #，段落用空行分隔，列表用 - 或 1.，加粗用 **，斜体用 *")
        prompt_parts.append("\n3. 确保格式规范，便于阅读和编辑")
        
        return "".join(prompt_parts)

    def review_document_content(self, document_text: str) -> Dict[str, Any]:
        """
        对公文内容进行审查：错别字、用词不当、不符合政府/部队公文写法，给出修改意见。

        Args:
            document_text: 从 docx 中提取的全文内容

        Returns:
            包含 issues 列表和 summary 的字典；若调用失败则返回 success=False 及 error。
        """
        if not self._api_key_configured or not settings.DASHSCOPE_API_KEY:
            return {"success": False, "error": "DASHSCOPE_API_KEY 未配置，请检查环境变量配置"}

        system_prompt = """你是一位熟悉政府机关与部队公文写作规范的审稿专家。你的任务是对给定的公文正文进行审查，找出以下三类问题并给出修改意见：

1. **错别字**：明显的错字、别字。
2. **用词不当**：词语搭配不当、歧义、口语化、不够严谨或正式的表述。
3. **公文规范**：不符合政府/部队公文写法的表述，例如：语气不够庄重、结构不规范、称谓或结尾用语不当、缺少必要要素等。

请仅根据原文内容进行审查，不要编造原文中不存在的句子。输出必须为合法的 JSON，且不要用 markdown 代码块包裹。
输出格式如下（不要包含其他说明文字）：
{
  "issues": [
    {
      "type": "错别字|用词不当|公文规范",
      "location": "简要位置说明，如：第2段 / 开头部分",
      "original": "有问题的原文片段（尽量简短）",
      "suggestion": "修改建议或推荐表述",
      "reason": "简要说明为何需要修改"
    }
  ],
  "summary": "对整篇文档的总体评价或审查说明（一两句话即可）"
}

若未发现任何问题，issues 可为空数组 []，summary 中说明“未发现明显问题”或类似表述。"""

        user_prompt = f"""请对以下公文正文进行审查，找出错别字、用词不当、不符合政府/部队公文写法的地方，并按上述 JSON 格式输出修改意见。

--- 公文正文 ---
{document_text[:12000] if len(document_text) > 12000 else document_text}
--- 正文结束 ---"""

        try:
            result = self.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=4000
            )
            if not result.get("success"):
                return result
            content = result.get("content", "").strip()
            # 去掉可能的 markdown 代码块包裹
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines)
            data = json.loads(content)
            issues = data.get("issues") if isinstance(data.get("issues"), list) else []
            summary = data.get("summary") or ""
            return {
                "success": True,
                "issues": issues,
                "summary": summary,
            }
        except json.JSONDecodeError as e:
            raw = content[:500] if content else ""
            logger.warning(f"内容审查返回非 JSON: {e}, raw={raw[:200]}")
            return {
                "success": False,
                "error": "审查结果解析失败，请重试",
                "raw": raw,
            }
        except Exception as e:
            logger.error(f"内容审查异常: {str(e)}")
            return {"success": False, "error": str(e)}

    async def review_document_content_stream(
        self, document_text: str
    ) -> AsyncGenerator[str, None]:
        """
        流式审查公文内容，以 Markdown 格式输出修改建议（SSE 格式）。

        Args:
            document_text: 从 docx 中提取的全文内容

        Yields:
            SSE 格式的数据块：data: {"content": "..."} 或 data: {"done": true} / data: {"error": "..."}
        """
        if not self._api_key_configured or not settings.DASHSCOPE_API_KEY:
            yield f"data: {json.dumps({'error': 'DASHSCOPE_API_KEY 未配置'})}\n\n"
            return

        system_prompt = """你是一位熟悉政府机关与部队公文写作规范的审稿专家。请对给定的公文正文进行审查，找出以下三类问题并给出修改意见：

1. **错别字**：明显的错字、别字。
2. **用词不当**：词语搭配不当、歧义、口语化、不够严谨或正式的表述。
3. **公文规范**：不符合政府/部队公文写法的表述，例如：语气不够庄重、结构不规范、称谓或结尾用语不当等。

请**仅使用 Markdown 格式**输出，不要使用代码块包裹。结构要求如下：
- 先用二级标题写：## 总体评价，下面一段话概括整篇文档的审查结论。
- 再用二级标题写：## 问题与修改建议，下面用列表或小标题逐条列出，每条包含：**类型**（错别字/用词不当/公文规范）、**原文**、**建议修改**、**说明**。
若未发现任何问题，在总体评价中说明“未发现明显问题”即可，可省略“问题与修改建议”部分。

直接输出 Markdown 内容，不要输出 ```markdown 等标记。"""

        user_prompt = f"""请对以下公文正文进行审查，按上述 Markdown 格式输出修改建议。

--- 公文正文 ---
{document_text[:12000] if len(document_text) > 12000 else document_text}
--- 正文结束 ---"""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            responses = Generation.call(
                model=settings.QWEN_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=4000,
                stream=True,
                incremental_output=True,
                result_format='message'
            )
            for response in responses:
                await asyncio.sleep(0)
                if response.status_code == 200 and getattr(response, 'output', None):
                    choices = getattr(response.output, 'choices', None) or []
                    if choices:
                        choice = choices[0]
                        content = ''
                        msg = getattr(choice, 'message', None)
                        if isinstance(msg, dict):
                            content = msg.get('content', '')
                        elif hasattr(msg, 'content'):
                            content = msg.content or ''
                        if isinstance(choice, dict) and not content:
                            msg = choice.get('message', {})
                            content = msg.get('content', '') if isinstance(msg, dict) else ''
                        if content:
                            yield f"data: {json.dumps({'content': content})}\n\n"
                else:
                    error_msg = getattr(response, 'message', '生成失败')
                    logger.error(f"内容审查流式调用失败: {error_msg}")
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                    return
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error(f"内容审查流式异常: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"


# 创建全局服务实例
qwen_service = QwenService()
