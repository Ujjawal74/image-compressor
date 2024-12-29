from flask import Flask, request, send_file, render_template
from PIL import Image
from io import BytesIO
import os

app = Flask(__name__)

# Ensure the upload folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def compress_image(image, max_size_kb):
    """Compress image to ensure it is under the specified size limit in KB."""
    img_bytes = BytesIO()
    target_size = max_size_kb * 1024  # Convert KB to bytes

    if image.format == 'JPEG':
        quality = 95
        while True:
            img_bytes.seek(0)  # Reset buffer for next save attempt
            img_bytes.truncate()  # Clear previous contents
            image.save(img_bytes, format='JPEG', quality=quality)
            if img_bytes.tell() <= target_size or quality < 10:  # Check size limit or minimum quality
                break
            quality -= 5
    elif image.format == 'PNG':
        # For PNG, we can use a different approach, such as saving with a lower bit depth or using optimization.
        image.save(img_bytes, format='PNG', optimize=True)
        if img_bytes.tell() > target_size:
            # If still larger than target size, reduce dimensions (optional)
            new_size = (int(image.width * 0.9),
                        int(image.height * 0.9))  # Reduce size by 10%
            resized_image = image.resize(new_size, Image.ANTIALIAS)
            img_bytes = BytesIO()
            resized_image.save(img_bytes, format='PNG', optimize=True)

    img_bytes.seek(0)
    return img_bytes


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['img']
        # Get user-defined size limit
        max_size_kb = int(request.form['max_size'])

        if file:
            # Read the image file into a PIL Image
            pil_img = Image.open(file.stream)

            # Compress the image based on user-defined size limit
            compressed_img_bytes = compress_image(pil_img, max_size_kb)

            return send_file(compressed_img_bytes,
                             mimetype='image/jpeg' if pil_img.format == 'JPEG' else 'image/png',
                             as_attachment=True,
                             download_name='compressed_image.' + pil_img.format.lower())

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=False)
