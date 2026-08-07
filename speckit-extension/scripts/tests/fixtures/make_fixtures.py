"""Sinh docx fixture bằng pandoc. Chạy: python make_fixtures.py"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

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


if __name__ == "__main__":
    build("numbered", NUMBERED)
    build("plain", PLAIN)
    build("bold", BOLD)
    print("OK", file=sys.stderr)
