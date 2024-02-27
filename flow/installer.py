import os
from pathlib import Path
import subprocess
import sys
import logging
import traceback

def install(fsm_content, requirements_content, path="."):
    fsm_path = Path(path) / "fsm.py"
    requirements_path = Path(path) / "requirements.txt"
    fsm_path.write_text(fsm_content)
    requirements_path.write_text(requirements_content)

    venv_path = Path(path) / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

    pip_path = venv_path / ("bin" if os.name != "nt" else "Scripts") / "pip"
    subprocess.run([str(pip_path), "install", "-r", str(requirements_path)], check=True)