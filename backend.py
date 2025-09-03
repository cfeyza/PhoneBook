import webbrowser
import pandas as pd

import sys
from PyQt6 import QtWidgets
from phonebook_ui import PhoneBookUI
from sql_functions import PhoneBookSQL
from PyQt6 import QtCore
from PyQt6 import QtGui

from dialogbox import GrupDuzenleDialog

class PhoneBookApp(PhoneBookUI):
    def __init__(self):
        super().__init__()
        self.sql_commands = PhoneBookSQL()

        # Buton bağlantıları
        self.btn_ekle.clicked.connect(self.add_contact)
        self.btn_guncelle.clicked.connect(self.update_contact)
        self.btn_sil.clicked.connect(self.delete_contact)
        self.btn_arama.clicked.connect(self.search_contact)
        self.btn_yenile.clicked.connect(self.refresh_table)
        self.table.cellClicked.connect(self.fill_form_from_table)

        self.btn_toplu_import.clicked.connect(self.bulk_import)
        self.btn_toplu_sil.clicked.connect(self.bulk_delete)


        self.btn_csv.clicked.connect(self.export_csv)
        self.btn_excel.clicked.connect(self.export_excel)
        self.btn_mail.clicked.connect(self.send_email)

        self.btn_foto.clicked.connect(self.select_photo)
        self.btn_foto_temizle.clicked.connect(self.clear_photo)

        self.btn_clear_form.clicked.connect(self.clear_form)

        # === Başlangıçta grupları DB'den yükle ===
        self.load_groups()
        # Butona tıklama
        self.btn_grup_duzenle.clicked.connect(self.grup_duzenle)
        self.input_grup.setCurrentIndex(-1)
        self.load_data()

    def load_data(self):
        """Tablodaki tüm verileri yükler"""
        self.table.setRowCount(0)
        for row_data in self.sql_commands.load_data_with_groups():
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                # Fotoğraf sütunu (örnek: 6. sütun photo)
                if column_number == 6 and data:  # photo sütunu
                    label = QtWidgets.QLabel()
                    pixmap = QtGui.QPixmap()
                    pixmap.loadFromData(data)  # BLOB → QPixmap
                        # Tablo için küçük önizleme (low-res is okay)
                    pixmap_small = pixmap.scaled(60, 60, QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
                                 QtCore.Qt.TransformationMode.SmoothTransformation)
                    label.setPixmap(pixmap_small)
                    label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    self.table.setCellWidget(row_number, column_number, label)
                else:
                    self.table.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

    def add_contact(self):
        """Formdaki bilgileri alıp yeni kişi ekler"""
        ad = self.input_ad.text()
        soyad = self.input_soyad.text()
        telefon = self.input_telefon.text()
        email = self.input_email.text()
        adres = self.input_adres.toPlainText()
        dogum_gunu = self.input_dogum_gunu.date().toPyDate()  # QDate → Python date        
        grup_id = self.input_grup.currentData()  # seçilen grup id
        aciklama = self.input_aciklama.toPlainText()  # Yeni alan
        photo_data = getattr(self, "current_photo_data", None)  # Fotoğraf verisi

        if ad and soyad and telefon:
            self.sql_commands.add_contact(ad, soyad, telefon, email, adres, photo_data, dogum_gunu, aciklama, grup_id)
            self.load_data()
            self.clear_form()
            self.current_photo_data = None  # Form temizlendikten sonra resetle

    def update_contact(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            contact_id = int(self.table.item(selected_row, 0).text())
            ad = self.input_ad.text()
            soyad = self.input_soyad.text()
            telefon = self.input_telefon.text()
            email = self.input_email.text()
            adres = self.input_adres.toPlainText()
            photo_data = getattr(self, "current_photo_data", None)  # Fotoğraf verisi
            dogum_gunu = self.input_dogum_gunu.date().toPyDate()
            aciklama = self.input_aciklama.toPlainText()
            grup_id = self.input_grup.currentData() or None  # önemli: None handle


            self.sql_commands.update_contact(contact_id, ad, soyad, telefon, email, adres, photo_data, dogum_gunu, aciklama, grup_id)
            self.load_data()
            QtWidgets.QMessageBox.information(self, "Başarılı", "Kişi güncellendi.")
            self.clear_form()
            self.current_photo_data = None  # Form temizlendikten sonra resetle

    def delete_contact(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            contact_id = int(self.table.item(selected_row, 0).text())
            self.sql_commands.delete_contact(contact_id)
            self.load_data()
            self.clear_form()

    def search_contact(self):
        keyword = self.input_arama.text()
        column_map = {
            "Hepsi": "hepsi",
            "Ad": "ad",
            "Soyad": "soyad",
            "Telefon": "telefon",
            "E-Posta": "email",
            "Adres": "adres",
            "Grup": "grup",
            "Açıklama": "aciklama"
        }
        selected_field = self.combox_arama.currentText()
        column_name = column_map.get(selected_field, "hepsi")

        self.table.setRowCount(0)
        for row_data in self.sql_commands.search_contact(column_name, keyword):
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                if column_number == 7 and data:  # dogum_gunu
                    data = data.strftime("%Y-%m-%d")
                self.table.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))


    def fill_form_from_table(self, row, column):
        try:
            self.input_ad.setText(self.table.item(row, 1).text())
            self.input_soyad.setText(self.table.item(row, 2).text())
            self.input_telefon.setText(self.table.item(row, 3).text())
            self.input_email.setText(self.table.item(row, 4).text())
            self.input_adres.setPlainText(self.table.item(row, 5).text())

            # FOTOĞRAF
            photo_widget = self.table.cellWidget(row, 6)
            if photo_widget:
                pixmap = photo_widget.pixmap()
                if pixmap and not pixmap.isNull():
                    self.photo_preview.setPixmap(pixmap.scaled(
                        self.photo_preview.width(),
                        self.photo_preview.height(),
                        QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                        QtCore.Qt.TransformationMode.SmoothTransformation
                    ))
                    # DB için orijinal BLOB'u al
                    contact_id = int(self.table.item(row, 0).text())
                    self.current_photo_data = self.sql_commands.get_photo(contact_id)
                else:
                    self.clear_photo()
            else:
                self.clear_photo()

            # Doğum günü
            dogum_item = self.table.item(row, 7)
            if dogum_item and dogum_item.text():
                date = QtCore.QDate.fromString(dogum_item.text(), "yyyy-MM-dd")
                self.input_dogum_gunu.setDate(date if date.isValid() else QtCore.QDate.currentDate())
            else:
                self.input_dogum_gunu.setDate(QtCore.QDate.currentDate())

            # Açıklama
            aciklama_item = self.table.item(row, 8)
            self.input_aciklama.setPlainText(aciklama_item.text() if aciklama_item else "")

            # Grup combobox
            grup_item = self.table.item(row, 10)
            if grup_item and grup_item.text().isdigit():
                grup_id = int(grup_item.text())
                index = self.input_grup.findData(grup_id)
                self.input_grup.setCurrentIndex(index if index >= 0 else -1)
            else:
                self.input_grup.setCurrentIndex(-1)

        except Exception as e:
            print("fill_form_from_table hatası:", e)
            QtWidgets.QMessageBox.warning(self, "Hata", f"Bir hata oluştu: {e}")


    def clear_form(self):
        self.input_ad.clear()
        self.input_soyad.clear()
        self.input_telefon.clear()
        self.input_email.clear()
        self.input_adres.clear()
        self.input_dogum_gunu.setDate(QtCore.QDate.currentDate())
        # Grup combobox sıfırla
        self.input_grup.setCurrentIndex(-1)  # Hiçbir grup seçili olmasın
        self.input_aciklama.clear()
        # Fotoğraf önizleme sıfırla
        self.photo_preview.clear()
        self.photo_preview.setText("Önizleme")
        self.current_photo_data = None
        # Seçili satırı temizle
        self.table.clearSelection()
    
    def export_csv(self):
        """Tablodaki verileri CSV olarak kaydeder."""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "CSV olarak kaydet", "", "CSV Files (*.csv)")
        if not path:
            return

        # Görünür sütunları al
        visible_columns = [col for col in range(self.table.columnCount()) if not self.table.isColumnHidden(col)]

        # Başlıkları al
        headers = []
        for col in visible_columns:
            header_item = self.table.horizontalHeaderItem(col)
            headers.append(header_item.text() if header_item else f"Column {col}")

        # Verileri al
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in visible_columns:
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Pandas DataFrame ve CSV'ye yaz
        try:
            df = pd.DataFrame(data, columns=headers)
            df.to_csv(path, index=False, encoding="utf-8")
            QtWidgets.QMessageBox.information(self, "Başarılı", "CSV dosyası başarıyla kaydedildi!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"CSV kaydedilirken hata oluştu:\n{str(e)}")


    def export_excel(self):
        """Tablodaki verileri Excel olarak kaydeder."""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Excel olarak kaydet", "", "Excel Files (*.xlsx)")
        if not path:
            return

        # Görünür sütunları al
        visible_columns = [col for col in range(self.table.columnCount()) if not self.table.isColumnHidden(col)]

        # Başlıkları al
        headers = []
        for col in visible_columns:
            header_item = self.table.horizontalHeaderItem(col)
            headers.append(header_item.text() if header_item else f"Column {col}")

        # Verileri al
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in visible_columns:
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        # Pandas DataFrame ve Excel'e yaz
        try:
            df = pd.DataFrame(data, columns=headers)
            df.to_excel(path, index=False)
            QtWidgets.QMessageBox.information(self, "Başarılı", "Excel dosyası başarıyla kaydedildi!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Excel kaydedilirken hata oluştu:\n{str(e)}")

        # === E-POSTA GÖNDER ===
    def send_email(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen bir kişi seçin!")
            return
        
        ad = self.table.item(selected_row, 1).text()
        soyad = self.table.item(selected_row, 2).text()
        telefon = self.table.item(selected_row, 3).text()
        email = self.table.item(selected_row, 4).text()
        adres = self.table.item(selected_row, 5).text()

        subject = " "
        body = f""" """

        # URL encode
        import urllib.parse
        subject_encoded = urllib.parse.quote(subject)
        body_encoded = urllib.parse.quote(body)

        mailto_link = f"mailto:{email}?subject={subject_encoded}&body={body_encoded}"

        # Varsayılan mail istemcisini aç
        webbrowser.open(mailto_link)

    # Örnek kullanım (buton click event içinde)
    # self.send_email_button.clicked.connect(lambda: send_email_via_client(ad, soyad, telefon, email, adres))

    def load_groups(self):
        """DB'den grupları combobox'a yükler"""
        self.input_grup.clear() #ComboBox içindeki tüm seçenekleri siler (yani item’ları boşaltır).
                                #Varsayılan olarak tamamen boş bir combobox kalır.
        for grup_id, grup_adi in self.sql_commands.load_groups():
            # itemData = grup_id, yani UI'da görünen ad = grup_adi
            self.input_grup.addItem(grup_adi, grup_id)
   
    def grup_duzenle(self):
        gruplar = self.sql_commands.load_groups()
        dialog = GrupDuzenleDialog(gruplar, self)
        if dialog.exec():
            # Güncellenen grupları DB'ye yansıt
            yeni_gruplar = dialog.get_gruplar()
            self.sync_groups(yeni_gruplar)
            self.load_groups()

    def sync_groups(self, yeni_gruplar):
        """UI'dan gelen grup listesi ile DB'yi senkronize et"""
        mevcut_gruplar = {gid: ad for gid, ad in self.sql_commands.load_groups()}

        mevcut_adlar = set(mevcut_gruplar.values())
        yeni_adlar = set(yeni_gruplar)

        # 1. Silinenler
        for gid, ad in mevcut_gruplar.items():
            if ad not in yeni_adlar:
                self.sql_commands.delete_group(gid)

        # 2. Yeni eklenenler
        for ad in yeni_gruplar:
            if ad not in mevcut_adlar:
                self.sql_commands.add_group(ad)

        # 3. Güncellenenler (adı değişmiş)
        # Mevcut ve yeni listeleri sıralı tutup indeks bazlı eşleme yapılabilir
        for gid, eski_ad in mevcut_gruplar.items():
            if eski_ad not in yeni_adlar:
                # Yeni ad listesinden hangi ad bu gid'e karşılık geliyor?
                for yeni_ad in yeni_gruplar:
                    if yeni_ad not in mevcut_adlar:
                        self.sql_commands.update_group(gid, yeni_ad)
                        mevcut_adlar.add(yeni_ad)  # tekrar güncelleme olmasın
                        break
        

    #FOTOĞRAF FONKSİYONLARI#########################
    def select_photo(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Fotoğraf Seç", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            # Önizleme
            pixmap = QtGui.QPixmap(file_path)
            pixmap = pixmap.scaled(self.photo_preview.width(), self.photo_preview.height())
            self.photo_preview.setPixmap(pixmap)

            # Fotoğrafı database için hazırla (base64 veya blob)
            with open(file_path, "rb") as f:
                self.current_photo_data = f.read()  # SQL fonksiyonuna gönderilecek

    def clear_photo(self):
        self.photo_preview.clear()
        self.photo_preview.setText("Önizleme")
        self.current_photo_data = None  # SQL'e None olarak gönder
        
    # === Toplu İçe Aktar ===
    def bulk_import(self):
        def safe_str(value):
            return str(value).strip() if pd.notna(value) else ""
        """CSV veya Excel dosyasından toplu veri import eder"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Dosya Seç", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        if not file_path:
            return

        try:
            # Dosya tipi kontrolü
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # Her satır için kişi ekle
            for _, row in df.iterrows():
                ad = safe_str(row.get("Ad"))
                soyad = safe_str(row.get("Soyad"))
                telefon = safe_str(row.get("Telefon"))
                email = safe_str(row.get("E-Posta"))
                adres = safe_str(row.get("Adres"))
                aciklama = safe_str(row.get("Açıklama"))
                grup_adi = safe_str(row.get("Grup"))
                dogum_gunu = row.get("Doğum Günü", None)

                # Grup yoksa ekle, varsa ID'sini al
                grup_id = None
                if grup_adi:
                    grup_id = self.sql_commands.add_group(grup_adi)

                # Dogum günü kontrolü
                if pd.isna(dogum_gunu):
                    dogum_gunu = None
                elif isinstance(dogum_gunu, str):
                    dogum_gunu = pd.to_datetime(dogum_gunu).date()
                elif isinstance(dogum_gunu, pd.Timestamp):
                    dogum_gunu = dogum_gunu.date()

                # Kişiyi ekle
                if ad and soyad and telefon:
                    self.sql_commands.add_contact(
                        ad, soyad, telefon, email, adres, None, dogum_gunu, aciklama, grup_id
                    )

            # Tabloları yeniden yükle
            self.load_data()
            QtWidgets.QMessageBox.information(self, "Başarılı", "Toplu import tamamlandı!")
            self.load_groups()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Toplu import sırasında hata oluştu:\n{str(e)}")

    # === Toplu Sil ===
    def bulk_delete(self):
        """Seçili satırları topluca siler"""
        selected_rows = set([index.row() for index in self.table.selectedIndexes()])
        if not selected_rows:
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen silinecek satırları seçin!")
            return

        confirm = QtWidgets.QMessageBox.question(
            self, "Onay", f"{len(selected_rows)} kişi silinsin mi?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            for row in sorted(selected_rows, reverse=True):
                contact_id = int(self.table.item(row, 0).text())
                self.sql_commands.delete_contact(contact_id)

            self.load_data()
            QtWidgets.QMessageBox.information(self, "Başarılı", "Seçili kişiler silindi.")

    def refresh_table(self):
        """Tüm kayıtları tekrar yükler ve tabloya doldurur"""
        self.table.setRowCount(0)
        self.input_arama.clear()

        for row_data in self.sql_commands.load_data_with_groups():
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                if column_number == 6 and data:  # photo
                    label = QtWidgets.QLabel()
                    pixmap = QtGui.QPixmap()
                    pixmap.loadFromData(data)
                    pixmap_small = pixmap.scaled(60, 60,
                                                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                QtCore.Qt.TransformationMode.SmoothTransformation)
                    label.setPixmap(pixmap_small)
                    label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    self.table.setCellWidget(row_number, column_number, label)
                elif column_number == 7 and data:  # dogum_gunu
                    data = data.strftime("%Y-%m-%d")
                    self.table.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
                else:
                    self.table.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

        # ---- EVENT FILTER ----
        self.table.viewport().installEventFilter(self)  # tablo içi boş alan tıklaması için

        # ---- CELL CLICKED TOGGLE ----
        self.table.cellClicked.connect(self.on_cell_clicked)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PhoneBookApp()
    window.show()
    sys.exit(app.exec())