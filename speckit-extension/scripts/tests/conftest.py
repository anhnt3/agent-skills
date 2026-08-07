import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_BRD = REPO_ROOT / "refs" / "5. Tài_liệu_mô_tả_giải_pháp_kỹ_thuật_phần_mềm_Mobifone.docx"


@pytest.fixture(scope="session")
def require_pandoc():
    """Chỉ test nào THẬT SỰ gọi pandoc mới xin fixture này.

    Trước đây fixture là autouse nên máy không có pandoc sẽ bỏ qua TOÀN BỘ test,
    kể cả test thuần đơn vị — CI báo xanh mà không chạy gì.
    """
    if shutil.which("pandoc") is None:
        pytest.skip("Không tìm thấy pandoc trên PATH")


@pytest.fixture(scope="session")
def real_brd(require_pandoc):
    if not REAL_BRD.exists():
        pytest.skip(f"Không có BRD thật tại {REAL_BRD} (thư mục refs/ không được commit)")
    return REAL_BRD
