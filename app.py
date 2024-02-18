from flask import Flask, render_template, request, redirect
from PIL import Image
import io
import base64
from ImageDatabase import ImageDatabase

app = Flask(__name__)
global id
global image
global flag_no_images_left_to_draw
flag_no_images_left_to_draw = False

db = ImageDatabase("image_database.db")
# get new image to display on the canvas
id, image = db.get_original_image_from_database_that_has_no_drawn_image_yet()
if id is None and image is None:
    flag_no_images_left_to_draw = True

@app.route("/")
def index():
    global image
    global id
    global flag_no_images_left_to_draw

    if db.row_exists(id) is False:
        id, image = db.get_original_image_from_database_that_has_no_drawn_image_yet()
    if id is None and image is None:
        flag_no_images_left_to_draw = True

    if flag_no_images_left_to_draw:
        return redirect("/manageDatabase")
    return render_template("index.html", background_image=base64.b64encode(image).decode('utf-8'))

@app.route("/process_image", methods=["POST"])
def process_image():
    global id
    global image
    # Get the image data from the form
    image_data = request.form.get("image_data")
    # Convert the data URL to a PIL Image
    image = Image.open(io.BytesIO(base64.b64decode(image_data.split(',')[1])))

    # Save the image as a PNG without the background
    output = io.BytesIO()
    image.save(output, format="PNG")
    drawn_image = output.getvalue()

    # Add the drawn image to the database
    db.add_drawn_image(id, drawn_image)
    # get new image to display on the canvas
    id, image = db.get_original_image_from_database_that_has_no_drawn_image_yet()
    if id is None and image is None:
        return redirect("/manageDatabase")
    return redirect("/")

@app.route("/manageDatabase")
def manageDatabase():
    entries = db.get_all_entries()
    modified_entries = []  # Create a new list for modified entries
    for entry in entries:
        entry_id = entry[0]
        original_image_data = base64.b64encode(entry[1]).decode('utf-8') if entry[1] else None
        drawn_image_data = base64.b64encode(entry[2]).decode('utf-8') if entry[2] else None
        modified_entries.append((entry_id, original_image_data, drawn_image_data))
    return render_template("manageDatabase.html", entries=modified_entries)

@app.route('/upload', methods=['POST'])
def upload_images():
    global flag_no_images_left_to_draw
    global image
    global id

    if 'images' not in request.files:
        # Handle the case where no files were selected
        return redirect(request.referrer)
    uploaded_files = request.files.getlist('images')

    if not uploaded_files or uploaded_files[0].filename == '':
        return redirect(request.referrer)

    for file in uploaded_files:
        image_data = file.read()
        db.add_original_image(image_data)

    flag_no_images_left_to_draw = False
    id, image = db.get_original_image_from_database_that_has_no_drawn_image_yet()
    return redirect(request.referrer)

@app.route("/deleteEntry/<int:id>", methods=["POST"])
def deleteEntry(id):
    db.deleteEntry(id)
    return redirect(request.referrer)

@app.route("/deleteEntryDrawing/<int:id>", methods=["POST"])
def deleteEntryDrawing(id):
    db.deleteEntryDrawing(id)
    return redirect(request.referrer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5213, debug=False)
