#!/usr/bin/env python3
"""
测试国标公文生成模块
依据 GB/T 9704-2012 和 GB/T 33476.2-2016
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.official_doc.structure_config import (
    get_doc_structure_dict,
    DocType,
)
from app.services.official_doc.formats.gb_t_9704_2012 import GB9704_2012
from app.services.official_doc.builders.request_builder import RequestDocumentBuilder
from app.services.official_doc.builders.report_builder import ReportDocumentBuilder
from app.services.official_doc.builders.notice_builder import NoticeDocumentBuilder
from app.services.official_doc.builders.memo_builder import MemoDocumentBuilder


def test_format_constants():
    """测试国标格式常量"""
    print("=" * 60)
    print("测试 1: 国标格式常量")
    print("=" * 60)

    print(f"页面尺寸: {GB9704_2012.PAGE_WIDTH} x {GB9704_2012.PAGE_HEIGHT}")
    print(f"页边距: 上={GB9704_2012.MARGIN_TOP}, 下={GB9704_2012.MARGIN_BOTTOM}")
    print(f"        左={GB9704_2012.MARGIN_LEFT}, 右={GB9704_2012.MARGIN_RIGHT}")
    print(f"标准行高: {GB9704_2012.LINE_HEIGHT_MM}")
    print(f"字体: 小标宋={GB9704_2012.FONT_XIAOBIAOSONG}, 仿宋={GB9704_2012.FONT_FANGSONG}")
    print("✓ 格式常量测试通过\n")


def test_structure_config():
    """测试公文结构配置"""
    print("=" * 60)
    print("测试 2: 公文结构配置")
    print("=" * 60)

    doc_types = [
        DocType.REQUEST,
        DocType.REPORT,
        DocType.NOTICE,
        DocType.MEMO,
        DocType.MEETING_MINUTES,
    ]

    for doc_type in doc_types:
        structure = get_doc_structure_dict(doc_type)
        print(f"\n【{doc_type}】")
        for sec in structure:
            required = " (必填)" if sec["required"] else ""
            print(f"  - {sec['section_name']} [{sec['section_id']}]{required}")

    print("\n✓ 结构配置测试通过\n")


def test_request_builder():
    """测试请示公文 builder"""
    print("=" * 60)
    print("测试 3: 请示公文 builder")
    print("=" * 60)

    # 测试数据
    content = {
        "title": "关于对张某某涉嫌盗窃一案立案调查的请示",
        "doc_number": "〔2026〕保字第 001 号",
        "recipient": "保卫处：",
        "main_body": "我单位在近期工作中发现，战士张某某（某部三营二连，上等兵）存在涉嫌盗窃同宿舍战友财物的行为。\n\n一、简要情况\n2026年1月24日22时30分许，我连发生一起宿舍财物失窃事件。经初步调查，张某某在案发时间段行为异常，且其个人物品中发现与失窃物品相关的线索。目前已完成初步询问和证据固定。\n\n二、请示事项\n为依法依规办理此案，现拟对张某某涉嫌盗窃一案立案调查。",
        "attachment": "《案件线索登记表》《初步调查情况说明》",
        "sender": "XX单位",
        "date": "2026年1月20日",
        "copies": ["军务科", "保卫科"],
        "issuer": "XX单位办公室",
        "issue_date": "2026年1月20日印发",
    }

    builder = RequestDocumentBuilder()
    doc = builder.build(content)

    # 保存测试文件
    output_path = "/tmp/test_request.docx"
    doc.save(output_path)
    print(f"✓ 请示公文生成成功: {output_path}")

    # 验证段落数量
    print(f"段落数量: {len(doc.paragraphs)}")
    if len(doc.paragraphs) > 0:
        print("前5段预览:")
        for i, p in enumerate(doc.paragraphs[:5]):
            if p.text.strip():
                print(f"  [{i+1}] {p.text[:50]}...")

    print("\n✓ 请示 builder 测试通过\n")


def test_report_builder():
    """测试报告公文 builder"""
    print("=" * 60)
    print("测试 4: 报告公文 builder")
    print("=" * 60)

    content = {
        "title": "关于2026年第一季度安全工作情况的报告",
        "doc_number": "〔2026〕保字第 002 号",
        "recipient": "首长：",
        "situation": "2026年第一季度，我单位认真贯彻落实上级关于安全工作的指示要求，扎实开展各项安全防范工作，确保了部队安全稳定。\n\n一季度共组织安全检查4次，发现隐患问题12起，已全部整改完毕。开展安全教育6次，受教育人数达1200余人次。",
        "problems": "虽然一季度安全形势总体平稳，但仍存在一些薄弱环节：一是个别人员安全意识淡薄，存在麻痹思想；二是部分安全设施老化，需要更新维护；三是应急处置预案演练不够充分。",
        "plan": "下步我们将采取以下措施：一是加强安全教育，提高人员安全意识；二是加大投入，及时更新维护安全设施；三是定期组织应急演练，提高处置能力。",
        "sender": "安全保卫科",
        "date": "2026年4月1日",
    }

    builder = ReportDocumentBuilder()
    doc = builder.build(content)

    output_path = "/tmp/test_report.docx"
    doc.save(output_path)
    print(f"✓ 报告公文生成成功: {output_path}")
    print(f"段落数量: {len(doc.paragraphs)}")
    print("✓ 报告 builder 测试通过\n")


def test_notice_builder():
    """测试通知公文 builder"""
    print("=" * 60)
    print("测试 5: 通知公文 builder")
    print("=" * 60)

    content = {
        "title": "关于开展五一劳动节安全大检查的通知",
        "doc_number": "〔2026〕保字第 003 号",
        "recipient": "各营、连，机关各科室：",
        "main_body": "为切实做好五一劳动节期间的安全工作，确保部队安全稳定，经研究决定，在全单位范围内开展安全大检查。现将有关事项通知如下：\n\n一、检查时间：4月28日至4月30日\n\n二、检查内容：安全制度落实、安全设施运行、重点部位管控等。",
        "requirements": "1. 各单位要高度重视，主官亲自负责；2. 认真排查，建立问题台账；3. 及时整改，确保检查实效。",
        "sender": "安全保卫科",
        "date": "2026年4月20日",
    }

    builder = NoticeDocumentBuilder()
    doc = builder.build(content)

    output_path = "/tmp/test_notice.docx"
    doc.save(output_path)
    print(f"✓ 通知公文生成成功: {output_path}")
    print(f"段落数量: {len(doc.paragraphs)}")
    print("✓ 通知 builder 测试通过\n")


def test_memo_builder():
    """测试函公文 builder"""
    print("=" * 60)
    print("测试 6: 函公文 builder")
    print("=" * 60)

    content = {
        "title": "关于协助调取监控录像的函",
        "doc_number": "〔2026〕保函字第 001 号",
        "recipient": "驻地公安局：",
        "main_body": "我单位近期发生一起财物失窃案件，为协助调查，特向贵局申请调取营区周边路段2026年4月15日至4月20日的监控录像资料。",
        "sender": "XX单位保卫科",
        "date": "2026年4月21日",
    }

    builder = MemoDocumentBuilder()
    doc = builder.build(content)

    output_path = "/tmp/test_memo.docx"
    doc.save(output_path)
    print(f"✓ 函公文生成成功: {output_path}")
    print(f"段落数量: {len(doc.paragraphs)}")
    print("✓ 函 builder 测试通过\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  国标公文生成模块 - 测试套件")
    print("  (依据 GB/T 9704-2012 和 GB/T 33476.2-2016)")
    print("=" * 60 + "\n")

    try:
        test_format_constants()
        test_structure_config()
        test_request_builder()
        test_report_builder()
        test_notice_builder()
        test_memo_builder()

        print("=" * 60)
        print("  所有测试通过! ✓")
        print("  生成的文件位于 /tmp/ 目录")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
