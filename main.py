import sys
from PyQt6 import QtWidgets
from backend import PhoneBookApp  # backend.py'den sınıfı import ediyoruz

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PhoneBookApp()
    window.show()
    sys.exit(app.exec())