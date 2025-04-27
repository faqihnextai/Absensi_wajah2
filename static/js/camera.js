// Ambil elemen video, canvas, tombol
const videoElement = document.getElementById('video');
const canvasElement = document.getElementById('canvas');
const captureButton = document.getElementById('captureButton');
const photoForm = document.getElementById('photo-form');
const photoInput = document.getElementById('photo');

// Start kamera
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElement.srcObject = stream;
    } catch (err) {
        console.error("Error accessing camera:", err);
        alert("Could not access the camera.");
    }
}

// Fungsi capture gambar
captureButton.addEventListener('click', () => {
    const context = canvasElement.getContext('2d');
    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

    // Konversi canvas ke blob
    canvasElement.toBlob((blob) => {
        const file = new File([blob], "photo.jpg", { type: 'image/jpeg' });

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        photoInput.files = dataTransfer.files;

        photoForm.submit();
    }, 'image/jpeg');
});

// Mulai kamera saat halaman load
window.onload = startCamera;
