from flask import Flask, render_template, send_from_directory, request, redirect, url_for
import os

app = Flask(__name__)

CAT_FOLDER = 'cats'
NOT_CAT_FOLDER = 'not_cats'

@app.route('/cats')
def list_cats():
    files = os.listdir(CAT_FOLDER)
    return render_template('manage.html', files=files, folder=CAT_FOLDER, type='cats')

@app.route('/not_cats')
def list_not_cats():
    files = os.listdir(NOT_CAT_FOLDER)
    return render_template('manage.html', files=files, folder=NOT_CAT_FOLDER, type='not_cats')

@app.route('/delete/<folder>/<filename>')
def delete_file(folder, filename):
    file_path = os.path.join(folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for(f'list_{folder}'))

@app.route('/<folder>/<filename>')
def uploaded_file(folder, filename):
    return send_from_directory(folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
