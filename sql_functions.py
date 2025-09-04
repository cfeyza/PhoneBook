from phonebook_ui import PhoneBookUI
import mysql.connector
import os
from dotenv import load_dotenv

class PhoneBookSQL:
    def __init__(self):
        load_dotenv()  # .env dosyasını yükler
        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        self.cursor = self.conn.cursor()


    def load_data(self):
        """
        Tüm kişiler tablosundaki kayıtları çeker.
        RETURN: Liste şeklinde tüm kayıtlar [(id, ad, soyad, telefon, email, adres, photo, dogum_gunu, grup, aciklama), ...]
        """
        self.cursor.execute("SELECT * FROM contacts")
        return self.cursor.fetchall()
    
    def add_contact(self, ad, soyad, telefon, email, adres, photo_data, dogum_gunu, aciklama, grup_id):
        """
        Yeni bir kişi ekler.
        grup_id: contact_groups tablosundaki id
        """
        self.cursor.execute(
            """INSERT INTO contacts 
            (ad, soyad, telefon, email, adres, photo, dogum_gunu, aciklama, grup_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (ad, soyad, telefon, email, adres, photo_data, dogum_gunu, aciklama, grup_id,)
        )
        self.conn.commit()

    def update_contact(self, contact_id, ad, soyad, telefon, email, adres, photo_data, dogum_gunu, aciklama,grup_id):
        self.cursor.execute(
            """UPDATE contacts 
            SET ad=%s, soyad=%s, telefon=%s, email=%s, adres=%s, photo=%s, dogum_gunu=%s, aciklama=%s, grup_id=%s 
            WHERE id=%s""",
            (ad, soyad, telefon, email, adres, photo_data, dogum_gunu, aciklama, grup_id, contact_id)
        )
        self.conn.commit()

    def delete_contact(self, contact_id):
        """
        Belirtilen ID'ye sahip kişiyi siler.
        PARAMS:
            contact_id (int): Silinecek kişinin ID'si
        """
        self.cursor.execute("DELETE FROM contacts WHERE id=%s", (contact_id,))
        self.conn.commit()

    def search_contact(self, column, keyword):
        """
        Kişi araması yapar (gruplar dahil).
        """
        base_query = """
            SELECT c.id, c.ad, c.soyad, c.telefon, c.email, c.adres, c.photo, 
                c.dogum_gunu, c.aciklama, g.grup_adi, c.grup_id
            FROM contacts c
            LEFT JOIN contact_groups g ON c.grup_id = g.id
        """

        if column == "hepsi":
            query = base_query + """
                WHERE COALESCE(c.ad, '') LIKE %s
                OR COALESCE(c.soyad, '') LIKE %s
                OR COALESCE(c.telefon, '') LIKE %s
                OR COALESCE(c.email, '') LIKE %s
                OR COALESCE(c.adres, '') LIKE %s
                OR COALESCE(c.aciklama, '') LIKE %s
                OR COALESCE(g.grup_adi, '') LIKE %s
            """
            self.cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", 
                                        f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        else:
            # SQL sütun eşleşmesi (alias ekle)
            column_map = {
                "ad": "c.ad",
                "soyad": "c.soyad",
                "telefon": "c.telefon",
                "email": "c.email",
                "adres": "c.adres",
                "aciklama": "c.aciklama",
                "grup": "g.grup_adi"
            }
            col = column_map.get(column, "c.ad")  # default: ad
            query = base_query + f" WHERE COALESCE({col}, '') LIKE %s"
            self.cursor.execute(query, (f"%{keyword}%",))

        return self.cursor.fetchall()


    # === GRUP İŞLEMLERİ ===
    def load_groups(self):
        """Tüm grupları (id, grup_adi) olarak döner"""
        self.cursor.execute("SELECT id, grup_adi FROM contact_groups ORDER BY grup_adi")
        return self.cursor.fetchall()
    """
    def add_group(self, grup_adi):
        #Yeni grup ekle
        self.cursor.execute("INSERT INTO contact_groups (grup_adi) VALUES (%s)", (grup_adi,))
        self.conn.commit()    """
    
    def add_group(self, grup_adi):
        """
        Yeni grup ekler ve eklenen grubun ID'sini döndürür.
        Eğer grup zaten varsa mevcut ID'sini döndürür.
        """
        # Önce grup adı zaten var mı kontrol et
        self.cursor.execute("SELECT id FROM contact_groups WHERE grup_adi = %s", (grup_adi,))
        result = self.cursor.fetchone()
        if result:
            return result[0]  # Mevcut ID

        # Yoksa yeni grup ekle
        self.cursor.execute("INSERT INTO contact_groups (grup_adi) VALUES (%s)", (grup_adi,))
        self.conn.commit()

        return self.cursor.lastrowid  # Eklenen grubun ID'sini döndür
    
    def delete_group(self, grup_id):
        """Grup sil (gruptaki kişilerde grup_id NULL olur)"""
        self.cursor.execute("DELETE FROM contact_groups WHERE id = %s", (grup_id,))
        self.conn.commit()

    def update_group(self, grup_id, yeni_ad):
        """Grup adını güncelle"""
        self.cursor.execute("UPDATE contact_groups SET grup_adi=%s WHERE id=%s", (yeni_ad, grup_id))
        self.conn.commit()
    
    def load_data_with_groups(self):
        self.cursor.execute("""
            SELECT c.id, c.ad, c.soyad, c.telefon, c.email, c.adres, c.photo, c.dogum_gunu, c.aciklama, g.grup_adi, c.grup_id
            FROM contacts c
            LEFT JOIN contact_groups g ON c.grup_id = g.id
        """)
        return self.cursor.fetchall()

    def get_photo(self, contact_id):
        self.cursor.execute("SELECT photo FROM contacts WHERE id = %s", (contact_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]  # BLOB
        return None

    def add_contacts_bulk(self, contacts):
        sql = """
        INSERT INTO contacts 
        (ad, soyad, telefon, email, adres, photo, dogum_gunu, aciklama, grup_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(sql, contacts)
        self.conn.commit()