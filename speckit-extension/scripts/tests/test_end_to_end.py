import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "brd_import.py"


def _run(*args):
    proc = subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, encoding="utf-8")
    return proc


def test_probe_brd_that_ra_bac_1_va_de_xuat_cap_5(real_brd, tmp_path):
    proc = _run("probe", str(real_brd), "--work", str(tmp_path / "w"))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["tier"] == 1
    assert data["needs_llm"] is False
    assert data["recommend_depth"] == 5
    by_depth = {lv["depth"]: lv for lv in data["levels"]}
    assert by_depth[5]["count"] == 54
    assert by_depth[6]["count"] == 432


def test_split_brd_that_ghep_nguoc_khop_va_ra_115_file_la(real_brd, tmp_path):
    work, dest = tmp_path / "w", tmp_path / "out"
    assert _run("probe", str(real_brd), "--work", str(work)).returncode == 0
    proc = _run("split", "--work", str(work), "--depth", "5", "--dest", str(dest))
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    assert report["roundtrip"] == "OK"
    assert report["media"] == 386
    assert (dest / "brd.manifest.yml").exists()
    assert (dest / "reference.docx").stat().st_size < 1_000_000
    leaves = [p for p in dest.rglob("*.md") if p.name != "_index.md"]
    # 54 node ở đúng cấp cắt + 61 folder không có con đã được gộp thành file.
    assert len(leaves) == 115


def test_split_tu_choi_de_len_thu_muc_da_co_manifest(real_brd, tmp_path):
    work, dest = tmp_path / "w", tmp_path / "out"
    _run("probe", str(real_brd), "--work", str(work))
    _run("split", "--work", str(work), "--depth", "5", "--dest", str(dest))
    proc = _run("split", "--work", str(work), "--depth", "5", "--dest", str(dest))
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    assert report["dest"].endswith("out.new")
    assert "diff" in report


def test_probe_bao_loi_ro_khi_khong_phai_docx(tmp_path):
    bad = tmp_path / "x.txt"
    bad.write_text("không phải docx", encoding="utf-8")
    proc = _run("probe", str(bad), "--work", str(tmp_path / "w"))
    assert proc.returncode == 2
    assert ".docx" in proc.stderr
