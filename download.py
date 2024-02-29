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

    def invert_image_colors(self, pil_image):
        # Ensure the image has an 'RGBA' mode
        pil_image = pil_image.convert('RGBA')

        # Invert the colors for non-transparent pixels
        inverted_data = []
        for r, g, b, a in pil_image.getdata():
            if a == 0:  # If the pixel is fully transparent, keep it transparent
                inverted_data.append((r, g, b, a))
            else:  # Otherwise, invert the colors
                inverted_data.append((255 - r, 255 - g, 255 - b, a))

        # Create a new image with the inverted data
        inverted_img = Image.new('RGBA', pil_image.size)
        inverted_img.putdata(inverted_data)

        # Convert the image to 'RGB' mode before returning (flattening transparency)
        return inverted_img.convert('RGB')

    def download_images(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, original_image, drawn_image FROM images WHERE original_image IS NOT NULL AND drawn_image IS NOT NULL")
        rows = cursor.fetchall()

        for row in rows:
            image_id, original_image, drawn_image = row[0], row[1], row[2]

            original_pil_image = Image.open(BytesIO(original_image))
            drawn_pil_image = Image.open(BytesIO(drawn_image))

            # Invert colors of drawn image
            inverted_drawn_image = self.invert_image_colors(drawn_pil_image)

            original_output_path = os.path.join(self.output_directory, f"image_{image_id}_original.jpg")
            drawn_output_path = os.path.join(self.output_directory, f"image_{image_id}_drawn.jpg")

            original_pil_image.save(original_output_path, format="JPEG")
            inverted_drawn_image.save(drawn_output_path, format="JPEG")

        print(f"All images downloaded and saved to {self.output_directory}")

if __name__ == "__main__":
    db_path = "image_database.db"  # Replace with your actual database path
    output_directory = "images"  # Choose the output directory

    downloader = ImageDownloader(db_path, output_directory)
    downloader.download_images()
