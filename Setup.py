import sys
from cx_Freeze import setup, Executable

setup(
    name="License Plate Recognition",
    version="3.1",
    description="Automatic Licence Plate Recognition System",
    executables=[Executable("Main.py", base="Win32GUI")])
