"""Sinh docx fixture bằng pandoc. Chạy: python make_fixtures.py"""

import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

# document.xml viết tay tối thiểu — không cần pandoc, không cần các phần
# .rels/[Content_Types].xml khác vì _read() chỉ zipfile.read() thẳng
# "word/document.xml". Dùng để kiểm _is_bold(): đoạn 1 tắt đậm tường minh
# (<w:b w:val="0"/>), đoạn 2 chỉ có bCs (đậm chữ phức hợp, KHÔNG phải w:b
# thường) — cả hai đều KHÔNG được tính là đậm.
BOLD_OFF_XML = (
    '<?xml version="1.0"?>'
    '<w:document><w:body>'
    '<w:p><w:r><w:rPr><w:b w:val="0"/></w:rPr><w:t>tat dam tuong minh</w:t></w:r></w:p>'
    '<w:p><w:r><w:rPr><w:bCs/></w:rPr><w:t>chi co bCs</w:t></w:r></w:p>'
    '</w:body></w:document>'
)

# Dấu \\. là BẮT BUỘC: viết "1. Chương một" trong markdown thì pandoc dựng ra
# DANH SÁCH ĐÁNH SỐ trong docx chứ không phải đoạn văn, và fixture sẽ vô dụng.
NUMBERED = """1\\. Chương một

thân chương một

1.1 Mục một một

thân mục một một

1.2 Mục một hai

thân mục một hai

2\\. Chương hai

thân chương hai

2.1 Mục hai một

thân mục hai một
"""

PLAIN = """chỉ toàn đoạn văn thường

không có tiêu đề nào cả

đoạn thứ ba cũng vậy
"""

BOLD = """**Chương một**

thân chương một

**Chương hai**

thân chương hai

**Chương ba**

thân chương ba

**Chương bốn**

thân chương bốn

**Chương năm**

thân chương năm
"""


def build(name, text):
    src = HERE / (name + ".md")
    src.write_text(text, encoding="utf-8")
    subprocess.run(["pandoc", str(src), "-o", str(HERE / (name + ".docx"))], check=True)
    src.unlink()


def build_raw(name, document_xml):
    """Zip tối thiểu chỉ chứa word/document.xml — đủ cho _read(), không cần pandoc."""
    with zipfile.ZipFile(HERE / (name + ".docx"), "w") as z:
        z.writestr("word/document.xml", document_xml)


if __name__ == "__main__":
    build("numbered", NUMBERED)
    build("plain", PLAIN)
    build("bold", BOLD)
    build_raw("bold_off", BOLD_OFF_XML)
    print("OK", file=sys.stderr)
