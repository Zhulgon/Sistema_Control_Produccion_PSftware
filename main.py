from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    target = (
        root
        / "Patrones"
        / "CODIGO"
        / "UI_MES_Software_Pro.py"
    )
    target_dir = str(target.parent)
    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
