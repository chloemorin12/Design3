from tkinter import Tk
from tkinter import ttk
from Application import *

import importlib
import subprocess
import sys

# Liste des modules nécessaires
modules_required = ["numpy", "pandas", "matplotlib", "scipy", "nidaqmx", "tkinter", "openpyxl", 'time', 'os', 'platform', 'threading', 'subprocess', 'io', 'pyperclip', 'contextlib', 'math']

def check_and_install_modules(modules):
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"{module} est déjà installé.")
        except ImportError:
            print(f"{module} n'est pas installé. Installation en cours...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
            print(f"{module} installé avec succès.")

# Vérification et installation
check_and_install_modules(modules_required)


if __name__ == "__main__":
    app = PowerMeterApp()
    app.mainloop()





