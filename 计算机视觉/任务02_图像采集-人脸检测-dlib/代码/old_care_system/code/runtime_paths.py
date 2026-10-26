from __future__ import annotations

import sys
from pathlib import Path

from PIL import ImageFont


CODE_DIR = Path(__file__).resolve().parent
OLD_CARE_ROOT = CODE_DIR.parent
PROJECT_ROOT = OLD_CARE_ROOT.parent

MODELS_DIR = OLD_CARE_ROOT / "models"
INFO_DIR = OLD_CARE_ROOT / "info"
IMAGES_DIR = OLD_CARE_ROOT / "images"
PLOTS_DIR = OLD_CARE_ROOT / "plots"
AUDIOS_DIR = OLD_CARE_ROOT / "audios"
SUPERVISION_DIR = OLD_CARE_ROOT / "supervision"
TEST_VIDEOS_DIR = IMAGES_DIR / "tests" / "videos"

PYTHON_EXECUTABLE = sys.executable


def ensure_directory(path: Path | str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_font(font_size: int):
    candidate_fonts = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for font_path in candidate_fonts:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), font_size)
    return ImageFont.load_default()
