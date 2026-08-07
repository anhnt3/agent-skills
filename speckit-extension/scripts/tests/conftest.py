import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_BRD = REPO_ROOT / "refs" / "5. Tài_liệu_mô_tả_giải_pháp_kỹ_thuật_phần_mềm_Mobifone.docx"


@pytest.fixture(scope="session")
def real_brd():
    if not REAL_BRD.exists():
        pytest.skip(f"Không có BRD thật tại {REAL_BRD} (thư mục refs/ không được commit)")
    return REAL_BRD


@pytest.fixture(scope="session", autouse=True)
def require_pandoc():
    if shutil.which("pandoc") is None:
        pytest.skip("Không tìm thấy pandoc trên PATH")
