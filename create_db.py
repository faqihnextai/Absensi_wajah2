import sqlite3

# Connect ke database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Buat tabel users
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nama_lengkap TEXT NOT NULL,
        nama_class_model TEXT NOT NULL
    )
''')

# Buat tabel absensi
c.execute('''
    CREATE TABLE IF NOT EXISTS absensi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        tanggal DATE NOT NULL,
        waktu TIME NOT NULL,
        path_foto TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

# Simpan dan tutup koneksi
conn.commit()
conn.close()

print("Database dan tabel berhasil dibuat!")
