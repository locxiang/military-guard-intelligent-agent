"""
GB/T 9704-2012 党政机关公文格式常量
依据 GB/T 33476.2-2016 第2部分：显现
"""
from docx.shared import Cm, Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


class GB9704_2012:
    """GB/T 9704-2012 标准格式常量"""

    # ===========================================================
    # 6 页面设置 (GB/T 33476.2-2016 第6章)
    # ===========================================================

    # 6.1 纸张大小 - A4 纸型：210mm × 297mm
    PAGE_WIDTH = Mm(210)
    PAGE_HEIGHT = Mm(297)

    # 6.2 页面边距
    # 上边距：34.58mm
    # 下边距：32.58mm
    # 左边距：28mm
    # 右边距：26mm
    MARGIN_TOP = Mm(34.58)
    MARGIN_BOTTOM = Mm(32.58)
    MARGIN_LEFT = Mm(28)
    MARGIN_RIGHT = Mm(26)

    # ===========================================================
    # 7 公文要素显现规则
    # ===========================================================

    # 字体名称（使用 Word 中文完整字体名称）
    FONT_XIAOBIAOSONG = "方正小标宋简体"  # 小标宋体（标题用）
    FONT_FANGSONG = "仿宋_GB2312"  # 仿宋
    FONT_KAITI = "楷体_GB2312"  # 楷体（发文机关标志用）
    FONT_HEITI = "黑体"  # 黑体

    # 字号 (pt) - 依据 GB/T 9704-2012
    FONT_SIZE_RED_HEADER = Pt(22)  # 红头字号（小标宋体）
    FONT_SIZE_DOC_NUMBER = Pt(16)  # 发文字号（三号仿宋）
    FONT_SIZE_TITLE = Pt(18)  # 标题（二号小标宋体）
    FONT_SIZE_MAIN_BODY = Pt(16)  # 正文（三号仿宋）
    FONT_SIZE_RECIPIENT = Pt(16)  # 主送机关（三号仿宋）
    FONT_SIZE_FOOTER = Pt(14)  # 版记（四号仿宋）

    # 颜色
    COLOR_RED = RGBColor(255, 0, 0)
    COLOR_BLACK = RGBColor(0, 0, 0)

    # ===========================================================
    # 附录A 行的定义 (GB/T 33476.2-2016 附录A)
    # ===========================================================

    # A.1 行的定义
    # 国标一行 = 三号字高 + 7/8 三号字高 ≈ 10.39mm
    # 三号字高约 5.54mm
    LINE_HEIGHT_MM = Mm(10.39)  # 标准一行高度
    LINE_HEIGHT_HALF = Mm(5.195)  # 半行高度

    # 行距 (基于标准行高)
    LINE_SPACING_MAIN_BODY = 1.0  # 正文单倍行距（标准行高）
    LINE_SPACING_FIXED = Pt(28)  # 正文固定行距 28磅

    # 首行缩进 - 2个三号字
    # 三号字每个字宽约 5.54mm，2字约 11.08mm
    FIRST_LINE_INDENT = Mm(11.08)

    # 对齐方式
    ALIGN_CENTER = WD_ALIGN_PARAGRAPH.CENTER
    ALIGN_LEFT = WD_ALIGN_PARAGRAPH.LEFT
    ALIGN_RIGHT = WD_ALIGN_PARAGRAPH.RIGHT
    ALIGN_JUSTIFY = WD_ALIGN_PARAGRAPH.JUSTIFY

    # ===========================================================
    # 7.1 版头 - 精确间距
    # ===========================================================

    # 发文机关标志上边缘至版心上边缘：37.42mm
    RED_HEADER_TOP_MARGIN = Mm(37.42)

    # 发文字号上边缘至发文机关名称下边缘：2行 (20.78mm)
    DOC_NUMBER_SPACING_AFTER_HEADER = Mm(20.78)

    # 红色分隔线上边缘至发文字号下边缘：4mm
    RED_LINE_SPACING_AFTER_DOC_NUMBER = Mm(4)

    # ===========================================================
    # 7.2 主体 - 精确间距
    # ===========================================================

    # 标题上边缘至红色分隔线：2行 (20.78mm)
    TITLE_SPACING_AFTER_RED_LINE = Mm(20.78)

    # 主送机关上边缘至标题下边缘：1行 (10.39mm)
    RECIPIENT_SPACING_AFTER_TITLE = Mm(10.39)

    # 附件说明上边缘至正文末段下边缘：1行 (10.39mm)
    ATTACHMENT_SPACING_AFTER_BODY = Mm(10.39)

    # 成文日期右缩进：4字
    DATE_RIGHT_INDENT_CHARS = 4

    # 印章顶端距正文：≤10.39mm
    STAMP_MAX_DISTANCE_FROM_BODY = Mm(10.39)

    # 附注上边缘至成文日期下边缘：1行 (10.39mm)
    NOTE_SPACING_AFTER_DATE = Mm(10.39)

    # ===========================================================
    # 7.3 版记
    # ===========================================================

    # 抄送机关："抄送："左缩进 1 字
    COPY_RECIPIENT_LEFT_INDENT = Mm(5.54)  # 1个三号字宽

    # 印发机关左缩进 1 字，印发日期右缩进 1 字
    ISSUER_LEFT_INDENT = Mm(5.54)
    ISSUE_DATE_RIGHT_INDENT = Mm(5.54)

    # ===========================================================
    # 8 页码
    # ===========================================================

    # 版心下边缘至页码中心：4.58mm
    PAGE_NUMBER_CENTER_DISTANCE = Mm(4.58)

    # 单页码：右对齐、右缩进 1 字
    # 双页码：左对齐、左缩进 1 字
    PAGE_NUMBER_SIDE_INDENT = Mm(5.54)

    # ===========================================================
    # 分隔线
    # ===========================================================

    # 红色分隔线宽度
    RED_LINE_WIDTH = Pt(1.5)

    # 版记分隔线宽度（细实线）
    VERSION_LINE_WIDTH = Pt(0.5)

    # ===========================================================
    # 段落间距转换 (twips, 1 twip = 1/20 pt)
    # ===========================================================

    @staticmethod
    def mm_to_twips(mm: float) -> int:
        """
        将毫米转换为 twips

        Args:
            mm: 毫米值

        Returns:
            twips 值
        """
        # 1 inch = 25.4 mm = 1440 twips
        # 1 mm = 1440 / 25.4 ≈ 56.6929 twips
        return int(mm * 56.6929 + 0.5)

    @staticmethod
    def lines_to_mm(lines: float) -> Mm:
        """
        将行数转换为毫米

        Args:
            lines: 行数（如 1, 2, 0.5）

        Returns:
            Mm 对象
        """
        return Mm(lines * 10.39)
