document.addEventListener('DOMContentLoaded', function() {
    const titleInput = document.querySelector('input[name="title"]');
    const contentInput = document.querySelector('textarea[name="content"]');
    const titleCounter = document.querySelector('#titleCounter span');
    const contentCounter = document.querySelector('#contentCounter span');
    const titleMaxLength = 100;
    const contentMaxLength = 5000;

    function updateCounter(input, counter, maxLength) {
        const remaining = maxLength - input.value.length;
        counter.textContent = remaining;
        
        if (remaining <= 20) {
            counter.parentElement.classList.add('text-danger');
        } else if (remaining <= 50) {
            counter.parentElement.classList.add('text-warning');
            counter.parentElement.classList.remove('text-danger');
        } else {
            counter.parentElement.classList.remove('text-warning', 'text-danger');
        }
    }

    titleInput.addEventListener('input', () => {
        updateCounter(titleInput, titleCounter, titleMaxLength);
    });

    contentInput.addEventListener('input', () => {
        updateCounter(contentInput, contentCounter, contentMaxLength);
        
        // Auto-resize textarea
        contentInput.style.height = 'auto';
        contentInput.style.height = (contentInput.scrollHeight) + 'px';
    });

    // Initialize counters
    updateCounter(titleInput, titleCounter, titleMaxLength);
    updateCounter(contentInput, contentCounter, contentMaxLength);
});

function previewPost() {
    const title = document.querySelector('input[name="title"]').value;
    const content = document.querySelector('textarea[name="content"]').value;
    
    // Update preview content
    document.getElementById('previewTitle').textContent = title;
    document.getElementById('previewContent').textContent = content;
    
    // Show modal
    const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
    previewModal.show();
}

// Form validation
document.querySelector('form').addEventListener('submit', function(e) {
    const title = document.querySelector('input[name="title"]').value.trim();
    const content = document.querySelector('textarea[name="content"]').value.trim();
    let hasError = false;

    if (!title) {
        document.querySelector('input[name="title"]').classList.add('is-invalid');
        hasError = true;
    }

    if (!content) {
        document.querySelector('textarea[name="content"]').classList.add('is-invalid');
        hasError = true;
    }

    if (hasError) {
        e.preventDefault();
    }
});

// Remove invalid class on input
document.querySelectorAll('.form-control').forEach(input => {
    input.addEventListener('input', function() {
        this.classList.remove('is-invalid');
    });
});