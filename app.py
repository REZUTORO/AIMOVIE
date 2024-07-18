from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
CAT_FOLDER = 'cats'
NOT_CAT_FOLDER = 'not_cats'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CAT_FOLDER'] = CAT_FOLDER
app.config['NOT_CAT_FOLDER'] = NOT_CAT_FOLDER

model = load_model('cat_detector.h5')  # モデルファイルの読み込み

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_cat(file_path):
    img = Image.open(file_path).resize((150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    prediction = model.predict(img_array)
    return prediction[0][0] > 0.5  # モデルの出力に応じて調整

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return redirect(request.url)
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                if is_cat(file_path):
                    os.rename(file_path, os.path.join(app.config['CAT_FOLDER'], filename))
                else:
                    os.rename(file_path, os.path.join(app.config['NOT_CAT_FOLDER'], filename))
        return redirect(url_for('upload_file'))
    cat_files = os.listdir(app.config['CAT_FOLDER'])
    not_cat_files = os.listdir(app.config['NOT_CAT_FOLDER'])
    return render_template('upload.html', cat_files=cat_files, not_cat_files=not_cat_files)

if __name__ == '__main__':
    app.run(debug=True)
