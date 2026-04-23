"""
公文结构配置 - 定义各类公文的分段结构
"""
from typing import List, Dict
from enum import Enum


class DocType(str, Enum):
    """公文类型枚举"""
    REQUEST = "request"  # 请示
    REPORT = "report"  # 报告/汇报
    NOTICE = "notice"  # 通知
    MEMO = "memo"  # 函
    MEETING_MINUTES = "meeting_minutes"  # 会议纪要


class DocSection:
    """公文分段定义"""

    def __init__(self, section_id: str, section_name: str, required: bool = True):
        self.section_id = section_id
        self.section_name = section_name
        self.required = required


# 请示结构
REQUEST_STRUCTURE: List[DocSection] = [
    DocSection("title", "公文标题"),
    DocSection("doc_number", "发文字号", required=False),
    DocSection("recipient", "主送机关"),
    DocSection("main_body", "正文"),
    DocSection("attachment", "附件说明", required=False),
    DocSection("sender", "发文机关"),
    DocSection("date", "成文日期"),
]

# 报告结构
REPORT_STRUCTURE: List[DocSection] = [
    DocSection("title", "公文标题"),
    DocSection("doc_number", "发文字号", required=False),
    DocSection("recipient", "主送机关"),
    DocSection("main_body", "正文"),
    DocSection("sender", "发文机关"),
    DocSection("date", "成文日期"),
]

# 通知结构
NOTICE_STRUCTURE: List[DocSection] = [
    DocSection("title", "公文标题"),
    DocSection("doc_number", "发文字号", required=False),
    DocSection("recipient", "主送机关"),
    DocSection("main_body", "正文"),
    DocSection("requirements", "执行要求", required=False),
    DocSection("sender", "发文机关"),
    DocSection("date", "成文日期"),
]

# 函结构
MEMO_STRUCTURE: List[DocSection] = [
    DocSection("title", "公文标题"),
    DocSection("doc_number", "发文字号", required=False),
    DocSection("recipient", "收文单位"),
    DocSection("main_body", "正文"),
    DocSection("sender", "发文机关"),
    DocSection("date", "成文日期"),
]

# 会议纪要结构
MEETING_MINUTES_STRUCTURE: List[DocSection] = [
    DocSection("title", "会议纪要标题"),
    DocSection("meeting_info", "会议基本信息"),
    DocSection("topics", "会议议题"),
    DocSection("discussion", "讨论内容"),
    DocSection("decisions", "议定事项"),
    DocSection("tasks", "待办分工", required=False),
]

# 结构映射
DOC_STRUCTURES: Dict[str, List[DocSection]] = {
    DocType.REQUEST: REQUEST_STRUCTURE,
    DocType.REPORT: REPORT_STRUCTURE,
    DocType.NOTICE: NOTICE_STRUCTURE,
    DocType.MEMO: MEMO_STRUCTURE,
    DocType.MEETING_MINUTES: MEETING_MINUTES_STRUCTURE,
}


def get_doc_structure(doc_type: str) -> List[DocSection]:
    """
    获取指定公文类型的结构定义

    Args:
        doc_type: 公文类型

    Returns:
        分段结构列表
    """
    return DOC_STRUCTURES.get(doc_type, [])


def get_doc_structure_dict(doc_type: str) -> List[Dict[str, any]]:
    """
    获取指定公文类型的结构定义（字典格式，用于 API 响应）

    Args:
        doc_type: 公文类型

    Returns:
        分段结构字典列表
    """
    sections = get_doc_structure(doc_type)
    return [
        {
            "section_id": s.section_id,
            "section_name": s.section_name,
            "required": s.required,
        }
        for s in sections
    ]
