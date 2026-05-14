# app/analyzer.py
# coding:utf-8
import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from windows.view.main_window import MainWindow
from windows.common.config import cfg   # 如果你还在用配置


def setup_dpi():
    """DPI 适配"""
    try:
        if cfg.get(cfg.dpiScale) != "Auto":
            os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
            os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
    except Exception:
        # 如果你后面删了 cfg，这里不会崩
        pass


def main():
    setup_dpi()

    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()