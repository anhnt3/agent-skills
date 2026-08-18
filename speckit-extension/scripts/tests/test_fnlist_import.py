import argparse
import json
import sys
from pathlib import Path

import pytest

import fnlist_import as fi

SCRIPT = Path(__file__).resolve().parents[1] / "fnlist_import.py"


def write_csv(tmp_path, rows, name="fnlist.csv"):
    import csv
    p = tmp_path / name
    with open(p, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    return p


SAMPLE = [
    ["STT", "Tên chức năng", "Mô tả"],
    ["1", "Quản lý đơn hàng", ""],
    ["1.1", "Danh sách đơn", "Xem, tìm kiếm đơn"],
    ["1.2", "Tạo đơn mới", ""],
    ["2", "Quản lý khách hàng", ""],
]

MAPPING = {"first_data_row": 1,
           "columns": {"name": 1, "description": 2},
           "hierarchy": {"mode": "outline", "column": 0}}


def test_cell_str_normalises_numbers_and_none():
    assert fi.cell_str(None) == ""
    assert fi.cell_str(3.0) == "3"
    assert fi.cell_str(3.5) == "3.5"
    assert fi.cell_str("  x  ") == "x"


def test_read_grid_csv_returns_single_sheet(tmp_path):
    grids = fi.read_grid(write_csv(tmp_path, SAMPLE))
    assert list(grids) == ["fnlist"]
    assert len(grids["fnlist"]) == 5


def test_inspect_prints_shape_and_head(tmp_path, capsys):
    p = write_csv(tmp_path, SAMPLE)
    fi.cmd_inspect(argparse.Namespace(path=str(p), sheet=None, max_rows=3,
                                      max_cols=10, first_data_row=1))
    sheet = json.loads(capsys.readouterr().out)["sheets"][0]
    assert sheet["name"] == "fnlist"
    assert sheet["rows"] == 5
    assert len(sheet["head"]) == 3


def test_inspect_reports_hierarchy_candidates(tmp_path, capsys):
    p = write_csv(tmp_path, SAMPLE)
    fi.cmd_inspect(argparse.Namespace(path=str(p), sheet=None, max_rows=8,
                                      max_cols=12, first_data_row=1))
    sheet = json.loads(capsys.readouterr().out)["sheets"][0]
    top = sheet["hierarchy_candidates"][0]
    assert top["mode"] == "outline"
    assert top["column"] == 0
    assert "evidence" in top


def test_markdown_rendering_is_gone():
    """functions.md không còn tồn tại trong đường ống — mọi hàm render bảng
    markdown phải biến mất, không để lại đường quay về âm thầm."""
    for name in ("render_markdown", "parse_functions_md", "escape_cell",
                 "diff_rows", "build_rows", "HEADER"):
        assert not hasattr(fi, name), f"{name} còn sót lại trong fnlist_import"


def run_write(tmp_path, rows=None, mapping=None, out_name="functions.json",
              system="DMS", date="2026-08-11"):
    src = write_csv(tmp_path, rows or SAMPLE)
    out = tmp_path / out_name
    mp = tmp_path / "map.json"
    mp.write_text(json.dumps(mapping or MAPPING), encoding="utf-8")
    fi.cmd_write(argparse.Namespace(
        path=str(src), mapping=str(mp), out=str(out),
        system=system, date=date, sheet="fnlist"))
    return out


def test_write_creates_json_tree(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["schema_version"] == 1
    assert doc["system"] == "DMS"
    assert doc["source"]["sheet"] == "fnlist"
    assert doc["updated"] == "2026-08-11"
    assert [f["id"] for f in doc["functions"]] == ["FN-01", "FN-02"]
    kids = doc["functions"][0]["children"]
    assert [k["id"] for k in kids] == ["FN-01-01", "FN-01-02"]
    assert kids[0]["description"] == "Xem, tìm kiếm đơn"


def test_write_omits_pending_status_and_extra_keys(tmp_path, capsys):
    doc = json.loads(run_write(tmp_path).read_text(encoding="utf-8"))
    capsys.readouterr()
    node = doc["functions"][0]
    assert set(node) == {"id", "name", "description", "children"}


def test_write_report_counts_written_and_skipped(tmp_path, capsys):
    rows = SAMPLE + [["3", "", ""]]
    run_write(tmp_path, rows=rows)
    report = json.loads(capsys.readouterr().out)
    assert report["written"] == 4
    assert report["skipped"][0]["reason"] == "ô tên chức năng trống"
    assert report["retired"] == []
    assert "diff" not in report          # lần ghi đầu thì không có gì để so


def test_write_second_run_keeps_ids_status_and_reports_diff(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    doc = json.loads(out.read_text(encoding="utf-8"))
    doc["functions"][0]["children"][0]["status"] = "intel"
    out.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")

    rows = SAMPLE[:3] + [["1.2", "Tạo đơn nháp", ""]] + SAMPLE[3:]
    run_write(tmp_path, rows=rows)
    report = json.loads(capsys.readouterr().out)
    doc2 = json.loads(out.read_text(encoding="utf-8"))

    kids = {k["name"]: k for k in doc2["functions"][0]["children"]}
    assert kids["Danh sách đơn"]["id"] == "FN-01-01"
    assert kids["Danh sách đơn"]["status"] == "intel"    # tiến độ không bị xoá
    assert kids["Tạo đơn mới"]["id"] == "FN-01-02"       # KHÔNG bị dịch số
    assert kids["Tạo đơn nháp"]["id"] == "FN-01-03"      # chèn giữa, số cuối
    assert any(d["loai"] == "thêm" and d["ten"] == "Tạo đơn nháp"
               for d in report["diff"])


GRID_WITH_CONTENT = [
    ["STT", "Tên chức năng", "Mô tả", "Mức quan trọng"],
    ["1", "Quản lý đơn hàng", "", ""],
    ["1.1", "Danh sách đơn", "", ""],
    ["uc001", "Xem đơn", "Xem chi tiết đơn", "Cao"],
    ["uc002", "Tìm đơn", "Tìm theo mã", ""],
    ["1.2", "Tạo đơn mới", "Điền form tạo đơn", ""],
]

MAPPING_ABSORB = {"first_data_row": 1,
                  "columns": {"name": 1, "description": 2, "importance": 3},
                  "hierarchy": {"mode": "outline", "column": 0,
                                "unmatched_rows": "absorb"}}


def test_write_reports_written_use_cases_separately(tmp_path, capsys):
    out = run_write(tmp_path, rows=GRID_WITH_CONTENT, mapping=MAPPING_ABSORB)
    report = json.loads(capsys.readouterr().out)
    assert report["written"] == 3            # FN-01, FN-01-01, FN-01-02
    assert report["written_use_cases"] == 2   # 2 use-case gộp trong FN-01-01
    doc = json.loads(out.read_text(encoding="utf-8"))
    la = doc["functions"][0]["children"][0]
    assert la["use_cases"][0]["importance"] == "Cao"
    assert "importance" not in la["use_cases"][1]


def test_write_records_retired_ids_across_runs(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    run_write(tmp_path, rows=[r for r in SAMPLE if r[1] != "Tạo đơn mới"])
    report = json.loads(capsys.readouterr().out)
    assert report["retired"] == ["FN-01-02"]
    assert json.loads(out.read_text(encoding="utf-8"))["retired_ids"] == ["FN-01-02"]


def test_write_refuses_empty_result(tmp_path):
    rows = [["STT", "Tên chức năng", "Mô tả"]]
    with pytest.raises(SystemExit) as e:
        run_write(tmp_path, rows=rows)
    assert "không lấy được" in str(e.value).lower()


def test_write_reports_level_jump_as_clean_exit(tmp_path):
    rows = [["STT", "Tên chức năng", "Mô tả"],
            ["1", "Quản lý đơn hàng", ""],
            ["1.1.1", "Lọc trạng thái", ""]]
    with pytest.raises(SystemExit) as e:
        run_write(tmp_path, rows=rows)
    assert "nhảy" in str(e.value)


def test_write_leaves_old_file_untouched_on_failure(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    before = out.read_text(encoding="utf-8")
    bad = [["STT", "Tên chức năng", "Mô tả"],
           ["1", "Quản lý đơn hàng", ""],
           ["1.1.1", "Lọc trạng thái", ""]]
    with pytest.raises(SystemExit):
        run_write(tmp_path, rows=bad)
    assert out.read_text(encoding="utf-8") == before


def test_cli_write_survives_default_windows_console_encoding(tmp_path):
    """Regression: subprocess trên Windows mặc định stdout cp1252, không phải
    UTF-8 — in báo cáo tiếng Việt (json.dumps ensure_ascii=False) từng crash
    UnicodeEncodeError. Không truyền PYTHONIOENCODING để bài test này thật sự
    đi qua đường mặc định, không phải đường đã được env ưu ái."""
    import os
    import subprocess
    src = write_csv(tmp_path, SAMPLE + [["3", "", ""]])
    out = tmp_path / "functions.json"
    mp = tmp_path / "map.json"
    mp.write_text(json.dumps(MAPPING), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "PYTHONIOENCODING"}
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "write", str(src), "--mapping", str(mp),
         "--out", str(out), "--system", "DMS", "--date", "2026-08-11",
         "--sheet", "fnlist"],
        capture_output=True, text=True, encoding="utf-8", env=env)
    assert p.returncode == 0, p.stderr
    assert "ô tên chức năng trống" in p.stdout
    assert "Quản lý đơn hàng" in out.read_text(encoding="utf-8")


def test_update_sets_status(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    fi.cmd_update(argparse.Namespace(file=str(out), set=["FN-01-01=intel"]))
    report = json.loads(capsys.readouterr().out)
    assert report["updated"] == [{"id": "FN-01-01", "cu": "pending", "moi": "intel"}]
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["functions"][0]["children"][0]["status"] == "intel"


def test_update_accepts_multiple_ids(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    fi.cmd_update(argparse.Namespace(
        file=str(out), set=["FN-01-01=intel", "FN-01-02=srs"]))
    capsys.readouterr()
    kids = json.loads(out.read_text(encoding="utf-8"))["functions"][0]["children"]
    assert [k.get("status") for k in kids] == ["intel", "srs"]


def test_update_back_to_pending_removes_key(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    fi.cmd_update(argparse.Namespace(file=str(out), set=["FN-01-01=intel"]))
    fi.cmd_update(argparse.Namespace(file=str(out), set=["FN-01-01=pending"]))
    capsys.readouterr()
    node = json.loads(out.read_text(encoding="utf-8"))["functions"][0]["children"][0]
    assert "status" not in node


def test_update_rejects_unknown_id_without_writing(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    before = out.read_text(encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        fi.cmd_update(argparse.Namespace(
            file=str(out), set=["FN-01-01=intel", "FN-99=intel"]))
    assert "FN-99" in str(e.value)
    assert out.read_text(encoding="utf-8") == before   # không ghi một phần


def test_update_rejects_unknown_status(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    with pytest.raises(SystemExit) as e:
        fi.cmd_update(argparse.Namespace(file=str(out), set=["FN-01-01=xong"]))
    assert "xong" in str(e.value)


def test_update_rejects_malformed_set(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    with pytest.raises(SystemExit):
        fi.cmd_update(argparse.Namespace(file=str(out), set=["FN-01-01"]))


def test_update_on_missing_file_stops(tmp_path):
    with pytest.raises(SystemExit) as e:
        fi.cmd_update(argparse.Namespace(
            file=str(tmp_path / "khong-co.json"), set=["FN-01=intel"]))
    assert "khong-co.json" in str(e.value)


def test_cli_update_end_to_end(tmp_path, capsys):
    import subprocess
    out = run_write(tmp_path)
    capsys.readouterr()
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "update", "--file", str(out),
         "--set", "FN-02=srs"],
        capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stderr
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["functions"][1]["status"] == "srs"
