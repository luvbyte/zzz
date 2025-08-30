import os
from pathlib import Path

from zzz.config import ZZZ_PATH

LOG_DIR = Path(os.getenv("ZZZ_LOG_DIR", ZZZ_PATH / ".logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)


