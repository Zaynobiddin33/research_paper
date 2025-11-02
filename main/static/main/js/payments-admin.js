export function openModal(src) {
    const modal = document.getElementById('imageModal');
    const img = document.getElementById('modalImage');
    img.src = src;
    modal.classList.add('active');
}

export function closeModal() {
    document.getElementById('imageModal').classList.remove('active');
}
