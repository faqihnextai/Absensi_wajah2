from flask_bcrypt import Bcrypt
import sqlite3

bcrypt = Bcrypt()

# Connect ke database
conn = sqlite3.connect('../../database.db')
c = conn.cursor()

# Data user
username = 'agil'
password = 'agil123'
nama_lengkap = 'Admin Website'
nama_class_model = 'admin'

# Hash password
hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

# Insert user
c.execute('INSERT INTO users (username, password, nama_lengkap, nama_class_model) VALUES (?, ?, ?, ?)',
          (username, hashed_password, nama_lengkap, nama_class_model))

conn.commit()
conn.close()

print("User admin berhasil ditambahkan!")
