import os
from PIL import Image
from io import BytesIO
import sqlite3

class ImageDownloader:
    def __init__(self, db_path, output_directory):
        self.db_path = db_path
        self.output_directory = output_directory
        self.create_output_directory()

    def create_output_directory(self):
        os.makedirs(self.output_directory, exist_ok=True)

    def download_images(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Fetch entries where both original_image and drawn_image are not null
        cursor.execute("SELECT id, original_image, drawn_image FROM images WHERE original_image IS NOT NULL AND drawn_image IS NOT NULL")
        rows = cursor.fetchall()

        for row in rows:
            image_id, original_image, drawn_image = row[0], row[1], row[2]

            # Convert the binary data to PIL Images
            original_pil_image = Image.open(BytesIO(original_image))
            drawn_pil_image = Image.open(BytesIO(drawn_image))

            # Save the images as PNG
            original_output_path = os.path.join(self.output_directory, f"image_{image_id}_original.jpg")
            drawn_output_path = os.path.join(self.output_directory, f"image_{image_id}_drawn.jpg")

            original_pil_image.save(original_output_path, format="PNG")
            drawn_pil_image.save(drawn_output_path, format="PNG")

        print(f"All images downloaded and saved to {self.output_directory}")

if __name__ == "__main__":
    db_path = "image_database.db"  # Replace with your actual database path
    output_directory = "images"  # Choose the output directory

    downloader = ImageDownloader(db_path, output_directory)
    downloader.download_images()
