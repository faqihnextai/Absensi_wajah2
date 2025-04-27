from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_session import Session
from tensorflow.keras.models import load_model
import cv2
import numpy as np
import os
import datetime
import sqlite3

# Setup Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Biar session aman
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
bcrypt = Bcrypt(app)

# Load the trained model
model = load_model('model/keras_model.h5')

# Route untuk login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']
        
        # Cek user di database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT id, username, password FROM users WHERE username=?', (username,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user[2], password_input):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('home'))
        else:
            return "Login failed! Please check your credentials."
    
    return render_template('login.html')

# Route untuk logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Route Home (butuh login)
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# Route Scan Absent (butuh login)
@app.route('/scan-absent', methods=['GET', 'POST'])
def scan_absent():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # .... (lanjut isi scan)
    return render_template('scan.html')

# Route Submit Absent (butuh login)
@app.route('/submit-absent', methods=['POST'])
def submit_absent():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if 'photo' not in request.files:
        return "No photo uploaded", 400

    photo = request.files['photo']
    if photo.filename == '':
        return "No selected file", 400

    # Save photo
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{session['username']}_{timestamp}.jpg"
    save_dir = 'static/uploads/absensi'
    os.makedirs(save_dir, exist_ok=True)  # Pastikan folder ada
    save_path = os.path.join(save_dir, filename)
    photo.save(save_path)

    # Load photo for prediction
    img = cv2.imread(save_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224))
    img_array = np.array(img_resized) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Predict
    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction, axis=1)[0]

    # Mapping predicted class to user_id
    class_to_user_id = {
        0: 1,
        1: 2,
        2: 3,
        3: 4,
    }
    user_id = class_to_user_id.get(predicted_class)

    if user_id is None:
        return "Wajah tidak dikenali.", 400

    # Simpan absensi
    try:
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            tanggal = datetime.date.today()
            waktu = datetime.datetime.now().strftime("%H:%M:%S")
            relative_path = f'uploads/absensi/{filename}'  # supaya gampang diakses di HTML

            c.execute('INSERT INTO absensi (user_id, tanggal, waktu, path_foto) VALUES (?, ?, ?, ?)',
                      (user_id, tanggal, waktu, relative_path))
            conn.commit()

        result_message = "Absensi berhasil dilakukan!"

    except sqlite3.Error as e:
        result_message = f"Database error: {str(e)}"

    # Tampilkan hasilnya
    predicted_name = session['username']  # atau bisa mapping sendiri kalau mau lebih real
    return render_template('hasil_capture.html', 
                           image_path=relative_path, 
                           predicted_name=predicted_name,
                           result_message=result_message)

@app.route('/admin')
def admin_dashboard():
    # Mengecek apakah user sudah login
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Mendapatkan filter dari query string jika ada
    username_filter = request.args.get('username')
    tanggal_filter = request.args.get('tanggal')

    # Membuka koneksi database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Ambil semua user
    c.execute('SELECT id, username FROM users')
    users = c.fetchall()

    # Query absensi dengan filter
    query = '''
        SELECT absensi.id, users.username, absensi.tanggal, absensi.waktu, absensi.path_foto 
        FROM absensi
        JOIN users ON absensi.user_id = users.id
    '''
    filters = []
    params = []

    # Menambahkan filter jika ada
    if username_filter:
        filters.append('users.username = ?')
        params.append(username_filter)

    if tanggal_filter:
        filters.append('absensi.tanggal = ?')
        params.append(tanggal_filter)

    if filters:
        query += ' WHERE ' + ' AND '.join(filters)

    query += ' ORDER BY absensi.tanggal DESC, absensi.waktu DESC'

    # Menjalankan query
    c.execute(query, params)
    absensi = c.fetchall()

    # Menutup koneksi database setelah query selesai
    conn.close()

    # Mengirim data ke template
    return render_template('admin.html', users=users, absensi=absensi)


if __name__ == '__main__':
    app.run(debug=True)
