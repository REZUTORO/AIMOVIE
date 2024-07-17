from flask import Flask, request, jsonify, render_template, Response
import os
import cv2
import numpy as np
import mysql.connector

app = Flask(__name__, template_folder='site')
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# MySQL接続設定
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'AIMOVIE'
}


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "No image part in the request", 400
    
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # 顔検出処理を追加
    detect_faces(file_path)

    return "Image uploaded successfully", 200

def detect_faces(image_path):
    # Haar Cascadeを使った顔検出
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        roi_color = image[y:y+h, x:x+w]
        person_id = x  # この例では、顔のx座標をperson_idとして使用
        person_folder = os.path.join(UPLOAD_FOLDER, 'person_{}'.format(person_id))
        if not os.path.exists(person_folder):
            os.makedirs(person_folder)
        face_path = os.path.join(person_folder, 'face_{}.jpg'.format(x))
        cv2.imwrite(face_path, roi_color)
        
        # データベース保存
        save_to_db(face_path, person_id)

def save_to_db(file_path, person_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    sql = "INSERT INTO images (file_path, person_id) VALUES (%s, %s)"
    val = (file_path, person_id)
    cursor.execute(sql, val)
    
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/images/<person_id>')
def view_images(person_id):
    person_folder = os.path.join(UPLOAD_FOLDER, 'person_{}'.format(person_id))
    if not os.path.exists(person_folder):
        return "Person not found", 404
    
    images = os.listdir(person_folder)
    image_urls = [os.path.join('/static/', 'uploads', 'person_{}'.format(person_id), image) for image in images]
    
    return jsonify(image_urls)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    cap = cv2.VideoCapture("http://your-esp32-cam-url")  # ESP32-CAMのストリームURL
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/person/<person_id>')
def person_images(person_id):
    return render_template('person.html', person_id=person_id)

if __name__ == '__main__':
    app.run(debug=True)
