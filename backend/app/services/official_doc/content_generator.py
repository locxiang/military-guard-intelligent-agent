"""
分段内容生成器
"""
from typing import Dict, Any, AsyncGenerator, List
import json
import asyncio
from loguru import logger

from app.services.official_doc.structure_config import (
    get_doc_structure,
    get_doc_structure_dict,
    DocSection,
)
from app.services.qwen_service import qwen_service


class ContentGenerator:
    """分段内容生成器"""

    def __init__(self):
        self.qwen = qwen_service

    def get_doc_structure(self, doc_type: str) -> List[Dict[str, Any]]:
        """
        获取公文结构清单

        Args:
            doc_type: 公文类型

        Returns:
            分段结构列表
        """
        return get_doc_structure_dict(doc_type)

    def _build_section_prompt(
        self, doc_type: str, section: DocSection, form_data: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """
        构建单段内容的提示词

        Args:
            doc_type: 公文类型
            section: 分段定义
            form_data: 表单数据
            context: 上下文

        Returns:
            提示词
        """
        # 基础提示词
        base_prompt = f"你是一位专业的军队保卫部门文书写作助手。请根据提供的信息，生成「{section.section_name}」部分的内容。\n\n"

        # 添加表单数据
        if form_data:
            base_prompt += "【表单信息】\n"
            for key, value in form_data.items():
                if value:
                    base_prompt += f"- {key}: {value}\n"
            base_prompt += "\n"

        # 添加已生成的上下文
        if context and context.get("previous_sections"):
            base_prompt += "【已生成的内容】\n"
            for sec_id, sec_content in context["previous_sections"].items():
                if sec_content:
                    base_prompt += f"- {sec_id}: {sec_content}\n"
            base_prompt += "\n"

        # 添加具体要求
        base_prompt += "【要求】\n"
        base_prompt += f"1. 只生成「{section.section_name}」这一部分的内容，不要生成其他部分\n"
        base_prompt += "2. 内容要准确、严谨、条理清晰\n"
        base_prompt += "3. 语言要正式、规范，符合公文写作要求\n"
        base_prompt += "4. 直接输出内容，不要使用代码块包裹，不要添加额外说明\n"
        base_prompt += "\n"
        base_prompt += "请生成内容："

        return base_prompt

    async def generate_section(
        self, doc_type: str, section: DocSection, form_data: Dict[str, Any], previous_sections: Dict[str, str]
    ) -> str:
        """
        生成单段内容

        Args:
            doc_type: 公文类型
            section: 分段定义
            form_data: 表单数据
            previous_sections: 已生成的段落

        Returns:
            生成的内容
        """
        # 优先使用表单数据中已有的内容
        if form_data.get(section.section_id):
            return form_data[section.section_id]

        # 构建提示词
        prompt = self._build_section_prompt(
            doc_type=doc_type,
            section=section,
            form_data=form_data,
            context={"previous_sections": previous_sections},
        )

        # 调用 AI 生成
        result = self.qwen.generate_text(
            prompt=prompt,
            system_prompt="你是一位专业的军队保卫部门文书写作助手。",
            temperature=0.7,
            max_tokens=1000,
        )

        if result.get("success"):
            return result.get("content", "").strip()
        else:
            logger.warning(f"生成段落 {section.section_id} 失败: {result.get('error')}")
            return ""

    async def stream_generate_all(
        self, doc_type: str, form_data: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        流式生成所有段落（SSE 格式）

        Args:
            doc_type: 公文类型
            form_data: 表单数据

        Yields:
            SSE 格式的数据
        """
        sections = get_doc_structure(doc_type)
        if not sections:
            data = {"error": "不支持的公文类型"}
            yield "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"
            return

        previous_sections = {}
        total = len(sections)

        for idx, section in enumerate(sections):
            # 发送段落开始事件
            data = {
                "type": "section_start",
                "section_id": section.section_id,
                "section_name": section.section_name,
                "index": idx + 1,
                "total": total
            }
            yield "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"

            try:
                # 生成段落内容（模拟流式，实际是一次性生成后分段发送）
                content = await self.generate_section(
                    doc_type=doc_type,
                    section=section,
                    form_data=form_data,
                    previous_sections=previous_sections,
                )

                # 保存已生成内容
                previous_sections[section.section_id] = content

                # 模拟流式发送内容
                if content:
                    # 按字符发送，模拟打字机效果
                    chunk_size = 3
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i + chunk_size]
                        data = {
                            "type": "content",
                            "section_id": section.section_id,
                            "content": chunk
                        }
                        yield "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"
                        await asyncio.sleep(0.03)

                # 发送段落完成事件
                data = {
                    "type": "section_complete",
                    "section_id": section.section_id,
                    "content": content
                }
                yield "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"

            except Exception as e:
                logger.error(f"生成段落 {section.section_id} 时发生异常: {str(e)}")
                data = {
                    "type": "error",
                    "section_id": section.section_id,
                    "error": str(e)
                }
                yield "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"

        # 发送全部完成事件
        data = {
            "type": "all_complete",
            "sections": previous_sections
        }
        yield "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"


# 创建全局实例
content_generator = ContentGenerator()
