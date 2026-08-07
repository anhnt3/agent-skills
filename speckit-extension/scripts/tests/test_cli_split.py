"""Test cmd_split ở mức CLI, chạy trong tiến trình — không cần pandoc.

Dựng tay thư mục work (probe.json + brd.md) rồi gọi thẳng cmd_split, nhờ vậy kiểm
được các tính chất an toàn (không phá đích, không ghi khi kiểm chứng hỏng) mà không
phải nuốt 72MB docx thật.
"""

import argparse
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import brd_import
from brd.verify import VerifyError

MD = "\n".join([
    "trang bìa",
    "",
    "# Nhóm A",
    "thân A",
    "### Màn 1",
    "thân màn 1",
    "### Màn 2",
    "thân màn 2",
])


def _make_work(tmp_path):
    work = tmp_path / "w"
    work.mkdir()
    (work / "brd.md").write_text(MD, encoding="utf-8", newline="\n")
    (work / "probe.json").write_text(json.dumps({
        "tier": 1, "note": "test", "needs_llm": False, "recommend_depth": 2,
        "levels": [{"depth": 1, "word_level": 1, "count": 1},
                   {"depth": 2, "word_level": 3, "count": 2}],
        "source": {"file": "x.docx", "sha256": "abc", "pandoc": "3.9",
                   "path": str(tmp_path / "x.docx")},
    }, ensure_ascii=False), encoding="utf-8")
    return work


def _args(work, dest, depth=2):
    return argparse.Namespace(work=str(work), dest=str(dest), depth=depth)


@pytest.fixture(autouse=True)
def stub_reference_docx(monkeypatch):
    monkeypatch.setattr(brd_import, "build_reference_docx",
                        lambda src, out: Path(out).write_bytes(b"PK stub"))


def test_dich_khong_co_manifest_van_khong_bi_xoa(tmp_path, capsys):
    work = _make_work(tmp_path)
    dest = tmp_path / "brd"
    dest.mkdir()
    (dest / "ghi-chu.md").write_text("BA gõ tay", encoding="utf-8")

    brd_import.cmd_split(_args(work, dest))

    assert (dest / "ghi-chu.md").read_text(encoding="utf-8") == "BA gõ tay"
    assert not (dest / "brd.manifest.yml").exists()
    report = json.loads(capsys.readouterr().out)
    assert report["dest"].endswith("brd.new")
    assert (tmp_path / "brd.new" / "brd.manifest.yml").is_file()


def test_bao_cao_noi_ro_da_thay_the_thu_muc_new_cu(tmp_path, capsys):
    work = _make_work(tmp_path)
    dest = tmp_path / "brd"
    dest.mkdir()
    (dest / "ghi-chu.md").write_text("BA gõ tay", encoding="utf-8")
    old_new = tmp_path / "brd.new"
    old_new.mkdir()
    (old_new / "cu.md").write_text("lần chạy trước", encoding="utf-8")

    brd_import.cmd_split(_args(work, dest))

    report = json.loads(capsys.readouterr().out)
    assert "replaced_previous_new" in report
    assert not (old_new / "cu.md").exists()


def test_kiem_chung_hong_thi_khong_dong_vao_dich(tmp_path, monkeypatch):
    work = _make_work(tmp_path)
    dest = tmp_path / "brd"

    def boom(*a, **kw):
        raise VerifyError("giả lập lệch byte")

    monkeypatch.setattr(brd_import, "check_roundtrip", boom)
    with pytest.raises(SystemExit) as e:
        brd_import.cmd_split(_args(work, dest))
    assert e.value.code == 2
    assert not dest.exists()
    assert not (tmp_path / "brd.new").exists()


def test_kiem_chung_hong_khong_pha_dich_da_ton_tai(tmp_path, monkeypatch):
    work = _make_work(tmp_path)
    dest = tmp_path / "brd"
    dest.mkdir()
    (dest / "ghi-chu.md").write_text("BA gõ tay", encoding="utf-8")

    def boom(*a, **kw):
        raise VerifyError("giả lập lệch byte")

    monkeypatch.setattr(brd_import, "check_roundtrip", boom)
    with pytest.raises(SystemExit) as e:
        brd_import.cmd_split(_args(work, dest))
    assert e.value.code == 2
    assert [p.name for p in dest.iterdir()] == ["ghi-chu.md"]
    assert not (tmp_path / "brd.new").exists()


def test_thieu_brd_md_thi_bao_loi_tieng_viet_thay_vi_traceback(tmp_path, capsys):
    work = _make_work(tmp_path)
    (work / "brd.md").unlink()
    with pytest.raises(SystemExit) as e:
        brd_import.cmd_split(_args(work, tmp_path / "brd"))
    assert e.value.code == 2
    assert "brd.md" in capsys.readouterr().err


def test_probe_json_hong_thi_bao_loi_tieng_viet(tmp_path, capsys):
    work = _make_work(tmp_path)
    (work / "probe.json").write_text('{"tier": 1', encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        brd_import.cmd_split(_args(work, tmp_path / "brd"))
    assert e.value.code == 2
    assert "probe" in capsys.readouterr().err


def test_probe_needs_llm_thi_huong_dan_chay_lai_voi_outline(tmp_path, capsys):
    work = _make_work(tmp_path)
    (work / "brd.md").unlink()
    (work / "probe.json").write_text(json.dumps({
        "tier": 0, "needs_llm": True, "recommend_depth": None, "levels": [],
        "candidates": [], "note": "", "source": {"file": "x.docx", "sha256": "a",
                                                 "pandoc": "3.9", "path": "x.docx"},
    }), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        brd_import.cmd_split(_args(work, tmp_path / "brd"))
    assert e.value.code == 2
    assert "--outline" in capsys.readouterr().err
