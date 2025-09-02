from PyQt6 import QtWidgets
import sys

gruplar = [(1, "Aile"), (2, "Arkadaşlar"), (3, "İş")]

class GrupDuzenleDialog(QtWidgets.QDialog):
    def __init__(self, gruplar, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grupları Düzenle")
        self.resize(400, 300)

        layout = QtWidgets.QVBoxLayout(self)

        # Liste alanı (sadece adları gösterelim)
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.addItems([ad for (_id, ad) in gruplar])
        layout.addWidget(self.list_widget)

        # Ekle / Sil butonları
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_ekle = QtWidgets.QPushButton("Yeni Grup Ekle")
        self.btn_sil = QtWidgets.QPushButton("Seçiliyi Sil")
        self.btn_guncelle = QtWidgets.QPushButton("Güncelle")
        btn_layout.addWidget(self.btn_ekle)
        btn_layout.addWidget(self.btn_sil)
        btn_layout.addWidget(self.btn_guncelle)
        layout.addLayout(btn_layout)

        # Tamam / İptal butonları
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(buttons)

        # Sinyaller
        self.btn_ekle.clicked.connect(self.grup_ekle)
        self.btn_sil.clicked.connect(self.grup_sil)
        self.btn_guncelle.clicked.connect(self.grup_adi_duzenle)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def grup_adi_duzenle(self):
        item = self.list_widget.currentItem()
        if item:
            text, ok = QtWidgets.QInputDialog.getText(self, "Yeni Grup İsmi", "Grup adı:")
            if ok and text.strip():
                if text.strip() in [self.list_widget.item(i).text() for i in range(self.list_widget.count())]:
                    QtWidgets.QMessageBox.warning(self, "Hata", "Bu grup adı zaten mevcut!")
                else:
                    item.setText(text.strip())


    def grup_ekle(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Yeni Grup", "Grup adı:")
        if ok and text.strip():
            self.list_widget.addItem(text.strip())
        """QInputDialog.getText(...) → küçük bir popup pencere açar ve kullanıcıdan yeni grup adı ister.

text → kullanıcının girdiği yazı

ok → kullanıcı “Tamam” dedi mi (True) yoksa “İptal” mi (False)

if ok and text.strip(): → boş değilse ve onaylandıysa:

text.strip() → başındaki ve sonundaki boşlukları temizler

self.list_widget.addItem(text.strip()) → listeye yeni bir satır olarak ekler

Örnek: Kullanıcı “Hobiler” yazıp “Tamam” derse → listede yeni satır olarak gözükür."""    

    def grup_sil(self):
        item = self.list_widget.currentItem()
        if item:
            self.list_widget.takeItem(self.list_widget.row(item))
        """self.list_widget.currentItem() → listede seçili olan satırı alır.

Eğer hiçbir şey seçili değilse None döner.

self.list_widget.takeItem(self.list_widget.row(item)) →

self.list_widget.row(item) → seçili satırın indeksini verir (0,1,2...)

takeItem(indeks) → o satırı listeden siler

Örnek: Kullanıcı “İş” satırını seçip “Seçiliyi Sil” derse → o satır listeden kaybolur."""

    def get_gruplar(self):
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
    """self.list_widget.count() → listedeki satır sayısı

self.list_widget.item(i) → i’inci satırdaki QListWidgetItem nesnesini döner

.text() → o satırdaki grup adı

Sonuç olarak listeyi Python listesi olarak döndürür."""
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GrupDuzenleDialog(gruplar)
    window.show()
    sys.exit(app.exec())