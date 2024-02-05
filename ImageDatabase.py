import sqlite3
import random

class ImageDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS images (id INTEGER PRIMARY KEY, original_image BLOB NOT NULL, drawn_image BLOB)")

    def add_drawn_image(self, image_id, drawn_image):
        self.cursor.execute("UPDATE images SET drawn_image=? WHERE id=?", (sqlite3.Binary(drawn_image), image_id))
        self.conn.commit()

    def add_original_image(self, image):
        self.cursor.execute("INSERT INTO images (original_image) VALUES (?)", (sqlite3.Binary(image),))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_original_image_with_filename(self, filename):
        with open(filename, 'rb') as f:
            original_image = f.read()
        self.cursor.execute("INSERT INTO images (original_image) VALUES (?)", (sqlite3.Binary(original_image),))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_original_image(self, image_id):
        self.cursor.execute("SELECT original_image FROM images WHERE id=?", (image_id,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row[1]
    
    def deleteEntry(self, image_id):
        self.cursor.execute("DELETE FROM images WHERE id=?", (image_id,))
        self.conn.commit()

    def deleteEntryDrawing(self, image_id):
        self.cursor.execute("UPDATE images SET drawn_image=NULL WHERE id=?", (image_id,))
        self.conn.commit()
    
    def get_drawn_image(self, image_id):
        self.cursor.execute("SELECT drawn_image FROM images WHERE id=?", (image_id,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row[2]
    
    def get_original_image_from_database_that_has_no_drawn_image_yet(self):
        self.cursor.execute("SELECT id, original_image FROM images WHERE drawn_image IS NULL")
        rows = self.cursor.fetchall()
        if not rows:
            return None, None
        row = random.choice(rows)
        return row[0], row[1]
    
    def get_all_entries(self):
        self.cursor.execute("SELECT * FROM images")
        rows = self.cursor.fetchall()
        return rows
    
    def close(self):
        self.conn.close()

    def row_exists(self, image_id):
        self.cursor.execute("SELECT COUNT(*) FROM images WHERE id=?", (image_id,))
        count = self.cursor.fetchone()[0]
        return count > 0
