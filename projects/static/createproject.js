document.addEventListener("DOMContentLoaded", function () {

    //client project modal handling(cpmh)
    const projectModalButton = document.querySelector(
    '[data-dialog-target="create-project-modal"]');

    const projectModalBackdrop = document.querySelector(
    '[data-dialog-backdrop="create-project-modal"]');

    const projectModal = document.querySelector(
    '[data-dialog-target="create-project-modal"]');

    //Func to open client project modal
    function openCreateProjectModal() {
        projectModalBackdrop.classList.remove("pointer-events-none", "opacity-0");
        projectModalBackdrop.classList.add("opacity-100", "pointers-events-auto");
    }

    //func to close create project modal
    function closeCreateProjectModal(){
        projectModalBackdrop.classList.remove("opacity-100", "pointers-events-auto");
        projectModalBackdrop.classList.add("pointer-events-none", "opacity-0");
    }

    //click event for opening client create project form modal
    if (projectModalButton) {
        projectModalButton.addEventListener("click", function () {
            openCreateProjectModal();
        });
    }

    //close project modal when clicking outside
    if (
        projectModalBackdrop && 
        projectModalBackdrop.getAttribute("data-dialog-backdrop-close") === "true"
    ){
        projectModalBackdrop.addEventListener("click", function(e) {
            if (e.target === projectModalBackdrop) {
                closeCreateProjectModal();
            }
        });
    }

    //close modal when clicking outside
    document.addEventListener("keydown", function(e) {
        if (e.key === "Escape") {
            closeCreateProjectModal()
        }
    })









});