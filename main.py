#!/usr/bin/env python3
"""
Code Tools ++
Explorador de archivos profesional con analisis de codigo
"""

from gui import MainWindow
from core.startup_preloader import run_app_with_preload


def main():
    """Funcion principal"""
    run_app_with_preload(MainWindow)


if __name__ == "__main__":
    main()
