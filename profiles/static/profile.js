document.addEventListener('DOMContentLoaded', function() {
  // Get the button and modal elements
  const modalButton = document.querySelector('[data-dialog-target="sign-in-modal"]');
  const modalBackdrop = document.querySelector('[data-dialog-backdrop="sign-in-modal"]');
  const modal = document.querySelector('[data-dialog="sign-in-modal"]');

  // Function to open modal
  function openModal() {
    modalBackdrop.classList.remove('pointer-events-none', 'opacity-0');
    modalBackdrop.classList.add('opacity-100', 'pointer-events-auto');
  }

  // Function to close modal
  function closeModal() {
    modalBackdrop.classList.remove('opacity-100', 'pointer-events-auto');
    modalBackdrop.classList.add('pointer-events-none', 'opacity-0');
  }

  // Add click event to button to open modal
  modalButton.addEventListener('click', openModal);

  // Close modal when clicking outside (if backdrop-close is enabled)
  if (modalBackdrop.getAttribute('data-dialog-backdrop-close') === 'true') {
    modalBackdrop.addEventListener('click', function(e) {
      if (e.target === modalBackdrop) {
        closeModal();
      }
    });
  }

  // Optional: Add ESC key to close modal
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && !modalBackdrop.classList.contains('opacity-0')) {
      closeModal();
    }
  });
});