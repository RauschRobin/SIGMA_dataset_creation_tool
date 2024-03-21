from PIL import Image
import os
import pillow_heif
from PIL import Image, ExifTags

def downscale_img(img_obj, size=(512, 512)):
    # Open the image file
    img = img_obj.copy()

    width, height = img.size

    # Determine the new dimensions while preserving aspect ratio
    if width < height:
        new_width = size[0]
        new_height = int(height * (new_width / width))
    else:
        new_height = size[1]
        new_width = int(width * (new_height / height))

    new_size = (new_width, new_height)

    # Resize the image
    img.thumbnail(new_size, Image.LANCZOS)

    # Create a new image with the target size and paste the resized image onto it
    final_img = Image.new("RGB", size)
    # Calculate the position to paste the resized image at the center
    position = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
    final_img.paste(img, position)

    return final_img

def convert_heic_to_jpg(heic_path):
    """
    Convert HEIC image to JPG and replace the original HEIC file.

    Parameters:
    - heic_path: Path to the HEIC image file.
    """
    # Register HEIF opener with Pillow
    pillow_heif.register_heif_opener()

    # Open HEIC image

    img = Image.open(heic_path)

    # Convert and save as JPG
    jpg_path = heic_path.replace(".heic", ".jpg")
    img.convert('RGB').save(jpg_path, format='JPEG')

    print(f"Converted {heic_path}")

    # Remove the original HEIC file
    os.remove(heic_path)

    return jpg_path

def crop_images(folder_path, output_folder, size=(512, 512)): # tested
    """
    Crop all images inside a folder to the specified size. 
    Crops to the specific number of pixels from the middle.

    Parameters:
    - folder_path: Path to the folder containing images.
    - output_folder: Path to the folder where cropped images will be saved.
    - size: Tuple representing the target size of the cropped images (width, height).
    """
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get a list of files in the folder
    files = os.listdir(folder_path)

    # Process each file in the folder
    loop_counter = 0
    for file_name in files:
        print(loop_counter)
        # Check if the file format is HEIC
        if os.path.splitext(file_name)[1].lower() == ".heic":
            print(f"File format is HEIC {folder_path}{file_name}")
            file_name = convert_heic_to_jpg(f"{folder_path}{file_name}")
            file_name.replace(folder_path, "")

        # Check if the file is an image (you may want to add more image extensions)
        if file_name.endswith('.jpg') or file_name.endswith('.png') or file_name.endswith('.jpeg') or file_name.endswith('.JPG'):
            try:
                print(file_name)

                # Open the image file
                input_file_path = os.path.join(folder_path, file_name)
                img = Image.open(input_file_path)

                img = downscale_img(img)

                # Crop the image to the specified size
                width, height = img.size
                left = (width - size[0]) / 2
                top = (height - size[1]) / 2
                right = (width + size[0]) / 2
                bottom = (height + size[1]) / 2
                img_cropped = img.crop((left, top, right, bottom))

                # Save the cropped image to the output folder
                output_file_path = os.path.join(output_folder, file_name)
                img_cropped.save(output_file_path)

                print(f"{file_name} cropped successfully.")
            except Exception as e:
                print(f"Error cropping {file_name}: {str(e)}")
        loop_counter += 1

# Example usage
if __name__ == "__main__":
    input_folder = "raw"
    output_folder = "images_512x512/"

    crop_images(input_folder, output_folder)
