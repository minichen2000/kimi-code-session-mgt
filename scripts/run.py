"""Development entry point for the Kimi Code Session Manager GUI."""

import sys
from pathlib import Path

# Add src to path so the package can be imported without installation.
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from kimi_code_session_manager.gui import main  # noqa: E402

if __name__ == "__main__":
    main()
