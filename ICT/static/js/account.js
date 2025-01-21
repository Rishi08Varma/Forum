document.addEventListener('DOMContentLoaded', function() {
    // Profile Picture Preview
    function previewImage(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('preview').src = e.target.result;
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
    window.previewImage = previewImage;

    // Bio Character Counter
    const bioTextarea = document.querySelector('textarea[name="bio"]');
    const bioCounter = document.querySelector('#bioCounter span');
    const maxLength = 500;

    if (bioTextarea && bioCounter) {
        function updateCounter() {
            const remaining = maxLength - bioTextarea.value.length;
            bioCounter.textContent = remaining;
            bioCounter.style.color = remaining < 50 ? 'red' : '';
        }

        bioTextarea.addEventListener('input', updateCounter);
        updateCounter(); // Initial count
    }

    // Account Deletion Confirmation
    const confirmInput = document.getElementById('confirmUsername');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    const usernameToMatch = document.getElementById('usernameToMatch').textContent;

    if (confirmInput && confirmBtn) {
        confirmInput.addEventListener('input', function() {
            // Enable the button only if the input matches the username exactly
            confirmBtn.disabled = this.value !== usernameToMatch;
        });

        // Reset the confirmation input when the modal is closed
        const deleteModal = document.getElementById('deleteAccountModal');
        if (deleteModal) {
            deleteModal.addEventListener('hidden.bs.modal', function() {
                confirmInput.value = '';
                confirmBtn.disabled = true;
            });
        }
    }
});