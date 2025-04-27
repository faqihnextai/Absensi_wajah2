# Gunakan image dasar yang sudah memiliki Python 3.10
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file ke dalam container
COPY . /app/

# Set environment variable agar Flask tahu bahwa ini aplikasi produksi
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port yang akan digunakan Flask
EXPOSE 5000

# Jalankan aplikasi
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
