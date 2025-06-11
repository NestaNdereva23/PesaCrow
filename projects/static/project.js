document.addEventListener("DOMContentLoaded", function () {
  const modalBackdrop = document.querySelector("[data-dialog-backdrop='edit-milestone-modal']");
  const modalContainer = document.querySelector("[data-dialog='edit-milestone-modal']");
  

  // Function to open modal
  window.openMilestoneModal = function() {
    modalBackdrop.classList.remove("pointer-events-none", "opacity-0");
    modalBackdrop.classList.add("opacity-100", "pointer-events-auto");
  };

  
  // Function to close modal
  window.closeMilestoneModal = function() {
    modalBackdrop.classList.add("pointer-events-none", "opacity-0");
    modalBackdrop.classList.remove("opacity-100", "pointer-events-auto");
  };
  
  // Close modal on backdrop click
  if (modalBackdrop.getAttribute("data-dialog-backdrop-close") === "true") {
    modalBackdrop.addEventListener("click", function (e) {
      if (e.target === modalBackdrop) {
        closeMilestoneModal();
      }
    });
  }
  
  // Close modal on Escape key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeMilestoneModal();
    }
  });
  
  // Setup HTMX events
  document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === "edit-milestone-modal") {
      openMilestoneModal();
    }
  });
});