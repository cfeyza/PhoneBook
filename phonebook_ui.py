from PyQt6 import QtWidgets, QtCore, QtGui
import os, sys
from PyQt6.QtWidgets import QApplication

class PhoneBookUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telefon Rehberi")
        self.resize(1000, 720)
        
        if getattr(sys, 'frozen', False):  # PyInstaller exe ise
                base_path = sys._MEIPASS
        else:
                base_path = os.path.dirname(__file__)

                icon_path = os.path.join(base_path, "icon_df.png")
                self.setWindowIcon(QtGui.QIcon(icon_path))

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        self.setStyleSheet("""
        QMainWindow { background-color: #F5FFF0; }
        QLabel, QLineEdit, QTextEdit, QDateEdit, QComboBox {
        font-size: 14px;
        color: #2E3D2F;
        background-color: #FFFFFF;
        border: 1px solid rgba(191,255,0,180);
        border-radius: 5px;
        padding: 4px;
        }
        QPushButton {
        background-color: rgba(191, 255, 0, 150);
        color: #2E3D2F;
        border-radius: 5px;
        padding: 6px 12px;
        font-weight: bold;
        }
        QPushButton:hover { background-color: rgba(191, 255, 0, 180); }
        QPushButton:pressed { background-color: rgba(191, 255, 0, 200); }
        QTableWidget {
        background-color: #FFFFFF;
        color: #2E3D2F;
        /*gridline-color: rgba(191,255,0,150);*/
        gridline-color: rgba(191,255,0,180);  /* Grid çizgileri görünür */
        alternate-background-color: rgba(191,255,0,40); /* Zebra efekti */
        }
        QHeaderView::section {
        background-color: rgba(191,255,0,180);
        color: #2E3D2F;
        padding: 4px;
        border: 1px solid rgba(191,255,0,150);
        }
        QTableWidget::item:selected { background-color: rgba(191,255,0,120); }
        QLabel#photo_preview {
        background-color: #FFFFFF;
        border: 1px solid rgba(191,255,0,180);
        border-radius: 5px;
        }
        """)

        # ==== Form Alanları ====
        form_group = QtWidgets.QGroupBox("Kişi Bilgileri")
        form_layout = QtWidgets.QGridLayout()
        form_group.setLayout(form_layout)

        self.input_ad = QtWidgets.QLineEdit()
        self.input_soyad = QtWidgets.QLineEdit()
        self.input_telefon = QtWidgets.QLineEdit()
        self.input_email = QtWidgets.QLineEdit()
        self.input_adres = QtWidgets.QTextEdit()
        self.input_aciklama = QtWidgets.QTextEdit()
        self.input_dogum_gunu = QtWidgets.QDateEdit()
        self.input_dogum_gunu.setCalendarPopup(True)  # Takvim açılır
        self.input_grup = QtWidgets.QComboBox()

        form_layout.addWidget(QtWidgets.QLabel("Ad:"), 0, 0)
        form_layout.addWidget(self.input_ad, 0, 1)

        form_layout.addWidget(QtWidgets.QLabel("Soyad:"), 0, 2)
        form_layout.addWidget(self.input_soyad, 0, 3)

        form_layout.addWidget(QtWidgets.QLabel("Telefon:"), 1, 0)
        form_layout.addWidget(self.input_telefon, 1, 1)

        form_layout.addWidget(QtWidgets.QLabel("E-Posta:"), 1, 2)
        form_layout.addWidget(self.input_email, 1, 3)

        form_layout.addWidget(QtWidgets.QLabel("Adres:"), 2, 0)
        form_layout.addWidget(self.input_adres, 2, 1)

        form_layout.addWidget(QtWidgets.QLabel("Açıklama:"), 2, 2)
        form_layout.addWidget(self.input_aciklama, 2, 3)
        
        form_layout.addWidget(QtWidgets.QLabel("Doğum Günü:"), 3, 0)
        form_layout.addWidget(self.input_dogum_gunu, 3, 1)

        # === Grup + Buton ===
        grup_layout = QtWidgets.QHBoxLayout()
        grup_layout.addWidget(self.input_grup)
        self.btn_grup_duzenle = QtWidgets.QPushButton("Grup Düzenle")
        grup_layout.addWidget(self.btn_grup_duzenle)

        form_layout.addWidget(QtWidgets.QLabel("Grup:"), 3, 2)
        form_layout.addLayout(grup_layout, 3, 3)


        # ==== Fotoğraf Seçimi ====
        foto_layout = QtWidgets.QVBoxLayout()
        self.btn_foto = QtWidgets.QPushButton("Fotoğraf Seç")
        self.photo_preview = QtWidgets.QLabel("Önizleme")
        self.photo_preview.setFixedSize(120, 120)
        self.photo_preview.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.photo_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.btn_foto_temizle = QtWidgets.QPushButton("Fotoğrafı Kaldır")

        foto_layout.addWidget(self.btn_foto)
        foto_layout.addWidget(self.photo_preview)
        foto_layout.addWidget(self.btn_foto_temizle)
        form_layout.addLayout(foto_layout, 0, 4, 3, 1)

        main_layout.addWidget(form_group)

        # ==== Butonlar ====
        button_layout = QtWidgets.QHBoxLayout()
        self.btn_mail = QtWidgets.QPushButton("Seçili Kişiye Mail Gönder")
        self.btn_ekle = QtWidgets.QPushButton("Kişi Ekle")
        self.btn_guncelle = QtWidgets.QPushButton("Güncelle")
        self.btn_sil = QtWidgets.QPushButton("Sil")
        self.btn_csv = QtWidgets.QPushButton("CSV'ye Aktar")
        self.btn_excel = QtWidgets.QPushButton("Excel'e Aktar")
        self.btn_clear_form = QtWidgets.QPushButton("Formu Temizle")

        button_layout.addWidget(self.btn_mail)
        button_layout.addWidget(self.btn_ekle)
        button_layout.addWidget(self.btn_guncelle)
        button_layout.addWidget(self.btn_sil)
        button_layout.addWidget(self.btn_csv)
        button_layout.addWidget(self.btn_excel)
        button_layout.addWidget(self.btn_clear_form)

        main_layout.addLayout(button_layout)

        # ==== Arama Alanı ====
        search_layout = QtWidgets.QHBoxLayout()
        self.input_arama = QtWidgets.QLineEdit()
        self.input_arama.setPlaceholderText("Ad, soyad, telefon, e-posta veya adres")
        self.combox_arama = QtWidgets.QComboBox()
        self.combox_arama.addItems(["Hepsi","Ad", "Soyad", "Telefon", "E-Posta", "Adres","Grup","Açıklama"])
        self.combox_arama.setGeometry(370, 180, 120, 25)
        self.btn_arama = QtWidgets.QPushButton("Göster")
        self.btn_yenile = QtWidgets.QPushButton("Yenile")

        search_layout.addWidget(self.input_arama)
        search_layout.addWidget(self.combox_arama)
        search_layout.addWidget(self.btn_arama)
        search_layout.addWidget(self.btn_yenile)
        

        main_layout.addLayout(search_layout)

        # ==== Toplu İşlem Butonları ====
        bulk_layout = QtWidgets.QHBoxLayout()
        self.btn_toplu_import = QtWidgets.QPushButton("Toplu İçe Aktar")
        self.btn_toplu_sil = QtWidgets.QPushButton("Toplu Sil")
        bulk_layout.addWidget(self.btn_toplu_import)
        bulk_layout.addWidget(self.btn_toplu_sil)
        main_layout.addLayout(bulk_layout)

        # ==== Tablo ====
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels(["ID", "Ad", "Soyad", "Telefon", "E-Posta", "Adres", "Fotoğraf", "Doğum Günü", "Açıklama", "Grup"])
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        #Tabloda seçim yapılırken tüm satır seçilir. Yani hücreye tıklasan bile tüm satır mavi olur.
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        #self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        #Bu ayar sayesinde kullanıcı birden fazla satırı seçebilir (örn. Shift veya Ctrl tuşlarıyla).
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        #Bu tablo hücrelerinin düzenlenebilir olmadığını belirtir. Kullanıcı çift tıklasa bile içerik değiştirilemez.
        self.table.setColumnHidden(0, True)
        # 0. sütun yani ID gizleniyor. Genelde veritabanı kimliği olarak kullanılır, kullanıcıya gösterilmez ama arka planda tutulur.
        self.table.setColumnHidden(10, True)  # sütun 9 = grup_id # gizli grup_id sütunu
        #self.table.horizontalHeader().setStretchLastSection(True)
        #Tablonun son sütunu (Fotoğraf), pencerenin boş kalan kısmını dolduracak şekilde genişletilir.
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(7, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(8, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(9, QtWidgets.QHeaderView.ResizeMode.Fixed)

        # Zebra efektini aktif etmek için table ayarı:
        self.table.setAlternatingRowColors(True)
        # Satır ve sütun çizgilerini göster
        self.table.setShowGrid(True)

        # Çizgi rengini değiştir
        self.table.setGridStyle(QtCore.Qt.SolidLine)
        
        main_layout.addWidget(self.table)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhoneBookUI()
    window.show()
    sys.exit(app.exec())