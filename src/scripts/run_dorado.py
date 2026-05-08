import subprocess
import os
import sys
import threading
from pathlib import Path

class DoradoRunner:
    def __init__(self, project_root:Path, model:str="hac"):
        self.root = project_root
        self.bin_path = self.root / "bin" / "dorado"
        self.lib_path = self.root / "lib" / "dorado"
        self.model = model

        if not self.bin_path.exists():
            raise FileNotFoundError(f"Dorado binary not found at {self.bin_path}")