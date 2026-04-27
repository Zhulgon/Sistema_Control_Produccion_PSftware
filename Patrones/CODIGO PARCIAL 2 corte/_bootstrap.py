"""
Utilidad comun para ejecutar tests individuales desde src/test.
"""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_src_path() -> None:
    src_dir = Path(__file__).resolve().parent.parent
    src_str = str(src_dir)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
