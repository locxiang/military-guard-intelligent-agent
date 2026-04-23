#!/usr/bin/env python3
"""
测试分段标题格式
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.official_doc.builders.base import BaseDocumentBuilder
from app.services.official_doc.formats.gb_t_9704_2012 import GB9704_2012


class TestBuilder(BaseDocumentBuilder):
    """测试用的builder"""
    def build(self):
        # 红头（发文机关标志）
        self._add_red_header("中国人民解放军XX单位")

        # 红色分隔线
        self._add_red_line()

        # 标题
        self._add_title("关于测试分段标题的请示")

        # 主送机关
        self._add_recipient("首长：")

        # 添加各种分段标题测试
        test_content = """一、这是有句号的标题。
这是下面的正文内容。

二、这是有冒号的标题：
这是下面的正文内容。

三、这是有分号的标题；
这是下面的正文内容。

四、这是没有标点的标题
这是下面的正文内容。

五、只有序号的标题

下面是正文。

六、这个标题很长很长很长很长很长，超过二十个字了。
这是下面的正文内容。

七、这个标题也非常非常非常非常非常长，已经超过二十个字了。
这是下面的正文内容。

八、这个标题很短。
这是下面的正文内容。
"""
        self._add_main_body(test_content)

        # 妥否，请批示
        self._add_paragraph(
            "妥否，请批示。",
            font_name=GB9704_2012.FONT_FANGSONG,
            font_size=GB9704_2012.FONT_SIZE_MAIN_BODY,
            alignment=GB9704_2012.ALIGN_LEFT,
            first_line_indent=GB9704_2012.FIRST_LINE_INDENT,
            line_spacing_fixed=GB9704_2012.LINE_SPACING_FIXED,
            zero_spacing=True,
        )

        # 发文机关署名和成文日期
        self._add_sender_and_date("XX单位", "2026年4月23日")

        # 添加页码
        self._add_page_numbers()

        return self.doc


def main():
    """测试"""
    print("=" * 60)
    print("  测试分段标题格式")
    print("=" * 60)

    builder = TestBuilder()
    doc = builder.build()

    output_path = "/tmp/test_section_title.docx"
    doc.save(output_path)
    print(f"✓ 测试文件已生成: {output_path}")

    # 输出段落信息
    print(f"\n段落数量: {len(doc.paragraphs)}")
    print("\n段落预览:")
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip():
            # 检查这个段落是否混合了字体
            has_bold = any(run.font.bold for run in para.runs)
            has_normal = any(not run.font.bold for run in para.runs)
            font_info = ""
            if has_bold and has_normal:
                font_info = " [混合字体]"
            elif has_bold:
                font_info = " [黑体]"
            else:
                font_info = " [仿宋]"
            print(f"  [{i+1}] {para.text[:40]}...{font_info}")

    print("\n" + "=" * 60)
    print("  测试完成！")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
