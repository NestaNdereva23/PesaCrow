document.addEventListener("DOMContentLoaded", function () {
  // Get the profile modal elements
  const profileModalButton = document.querySelector(
    '[data-dialog-target="profile-info-modal"]'
  );
  const profileModalBackdrop = document.querySelector(
    '[data-dialog-backdrop="profile-info-modal"]'
  );
  const profileModal = document.querySelector(
    '[data-dialog="profile-info-modal"]'
  );

  //contact modal elements
  const contactModalButton = document.querySelector(
    '[data-dialog-target="contact-modal"]'
  );
  const contactModalBackdrop = document.querySelector(
    '[data-dialog-backdrop="contact-modal"]'
  );
  const contactModal = document.querySelector('[data-dialog="contact-modal"]');

  //mpesa number modal
  const mpesaModalButton = document.querySelector(
    '[data-dialog-target="mpesa-number-modal"]'
  );
  const mpesaModalBackdrop = document.querySelector(
    '[data-dialog-backdrop="mpesa-number-modal"]'
  );
  const mpesaModal = document.querySelector(
    '[data-dialog="mpesa-number-modal"]'
  );

  // Function to open profile modal
  function openProfileModal() {
    profileModalBackdrop.classList.remove("pointer-events-none", "opacity-0");
    profileModalBackdrop.classList.add("opacity-100", "pointer-events-auto");
  }

  // Function to close profile modal
  function closeProfileModal() {
    profileModalBackdrop.classList.remove("opacity-100", "pointer-events-auto");
    profileModalBackdrop.classList.add("pointer-events-none", "opacity-0");
  }

  // func to open contact modal
  function openContactModal() {
    contactModalBackdrop.classList.remove("pointer-events-none", "opacity-0");
    contactModalBackdrop.classList.add("opacity-100", "pointer-events-auto");
  }

  // close contact modal
  function closeContactModal() {
    contactModalBackdrop.classList.remove("opacity-100", "pointer-events-auto");
    contactModalBackdrop.classList.add("pointer-events-none", "opacity-0");
  }

  // func to open mpesa number modal
  function openMpesaModal() {
    mpesaModalBackdrop.classList.remove("pointer-events-none", "opacity-0");
    mpesaModalBackdrop.classList.add("opacity-100", "pointer-events-auto");
  }

  // close mpesa number modal
  function closeMpesaModal() {
    mpesaModalBackdrop.classList.remove("opacity-100", "pointer-events-auto");
    mpesaModalBackdrop.classList.add("pointer-events-none", "opacity-0");
  }

  // Function to close all modals
  function closeAllModals() {
    closeProfileModal();
    closeContactModal();
    closeMpesaModal();
  }

  // Add click event to profile modal button
  if (profileModalButton) {
    profileModalButton.addEventListener("click", function () {
      // Make sure other modals are closed first
      closeContactModal();
      closeMpesaModal();
      //open current modal
      openProfileModal();
    });
  }

  // click event --> contact modal button
  if (contactModalButton) {
    contactModalButton.addEventListener("click", function () {
      // Make sure other modals are closed first
      closeProfileModal();
      // Then open this modal
      openContactModal();
    });
  }

  // click event --> mpesa number modal button
  if (mpesaModalButton) {
    mpesaModalButton.addEventListener("click", function () {
      // Make sure other modals are closed first
      closeProfileModal();
      // Then open this modal
      openMpesaModal();
    });
  }

  // Close profile modal when clicking outside
  if (
    profileModalBackdrop &&
    profileModalBackdrop.getAttribute("data-dialog-backdrop-close") === "true"
  ) {
    profileModalBackdrop.addEventListener("click", function (e) {
      if (e.target === profileModalBackdrop) {
        closeProfileModal();
      }
    });
  }

  // Close contact modal when clicking outside
  if (
    contactModalBackdrop &&
    contactModalBackdrop.getAttribute("data-dialog-backdrop-close") === "true"
  ) {
    contactModalBackdrop.addEventListener("click", function (e) {
      if (e.target === contactModalBackdrop) {
        closeContactModal();
      }
    });
  }

  // Close mpesa number modal when  you clicck outside
  if (
    mpesaModalBackdrop &&
    mpesaModalBackdrop.getAttribute("data-dialog-backdrop-close") === "true"
  ) {
    mpesaModalBackdrop.addEventListener("click", function (e) {
      if (e.target === mpesaModalBackdrop) {
        closeMpesaModal();
      }
    });
  }

  // Close modals with ESC key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeAllModals();
    }
  });
});
