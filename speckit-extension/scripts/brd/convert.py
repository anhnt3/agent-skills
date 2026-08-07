"""Gọi pandoc và dựng reference.docx rút gọn từ file BRD gốc."""

import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

PANDOC_MISSING = (
    "Không tìm thấy pandoc trên PATH. Cài đặt:\n"
    "  Windows: winget install --id JohnMacFarlane.Pandoc\n"
    "  macOS:   brew install pandoc\n"
    "  Linux:   sudo apt install pandoc\n"
    "Yêu cầu pandoc >= 3.0."
)

# Body rỗng cho reference.docx: giữ nguyên styles.xml/theme/header/footer của
# tài liệu gốc, vứt toàn bộ nội dung và ảnh.
_EMPTY_BODY = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:body><w:p/><w:sectPr/></w:body></w:document>"
)


class ConvertError(Exception):
    pass


def check_pandoc():
    if shutil.which("pandoc") is None:
        raise ConvertError(PANDOC_MISSING)
    out = subprocess.run(["pandoc", "--version"], capture_output=True, text=True).stdout
    m = re.search(r"pandoc\s+(\d+\.\d+[^\s]*)", out)
    if not m:
        raise ConvertError("Không đọc được version của pandoc: " + out.splitlines()[0])
    if int(m.group(1).split(".")[0]) < 3:
        raise ConvertError(f"Cần pandoc >= 3.0, đang có {m.group(1)}.")
    return m.group(1)


def run_pandoc(docx, workdir, lua_filter=None, metadata=None):
    """docx -> workdir/brd.md, ảnh tách vào workdir/media/media/."""
    docx, workdir = Path(docx), Path(workdir)
    if not docx.is_file():
        raise ConvertError(f"Không thấy file: {docx}")
    check_pandoc()
    workdir.mkdir(parents=True, exist_ok=True)
    md_path = workdir / "brd.md"
    src_fmt = "docx+styles" if lua_filter else "docx"
    cmd = ["pandoc", str(docx.resolve()), "-f", src_fmt, "-t", "markdown",
           "--extract-media=./media", "-o", "brd.md"]
    if lua_filter:
        cmd += [f"--lua-filter={Path(lua_filter).resolve()}"]
    if metadata:
        # --metadata-file chứ không phải -M: -M chỉ truyền được chuỗi phẳng,
        # còn filter cần cả một danh sách bản ghi {text, level}.
        (workdir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        cmd += ["--metadata-file=metadata.json"]
    proc = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ConvertError(f"pandoc thất bại (mã {proc.returncode}):\n{proc.stderr}")
    return md_path


def build_reference_docx(docx, dest):
    """Bản sao docx gốc: bỏ word/media/, thay document.xml bằng body rỗng.

    Giữ styles.xml/theme/header/footer để brd-export sau này xuất đúng trình bày.
    72MB -> ~36KB trên BRD Mobifone.
    """
    docx, dest = Path(docx), Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(docx) as zin, zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename.startswith("word/media/"):
                continue
            data = _EMPTY_BODY.encode("utf-8") if item.filename == "word/document.xml" \
                else zin.read(item.filename)
            zout.writestr(item, data)
    return dest
