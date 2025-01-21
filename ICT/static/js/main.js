// ICT/static/js/main.js

// Handle voting
function handleVote(postId, voteType) {
    fetch(`/post/${postId}/vote`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ vote_type: voteType })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update vote count
            document.getElementById(`vote-count-${postId}`).textContent = data.new_count;
            
            // Update button states
            const upvoteBtn = document.getElementById(`upvote-${postId}`);
            const downvoteBtn = document.getElementById(`downvote-${postId}`);
            
            if (voteType === 'up') {
                upvoteBtn.classList.toggle('active');
                downvoteBtn.classList.remove('active');
            } else {
                downvoteBtn.classList.toggle('active');
                upvoteBtn.classList.remove('active');
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Preview image before upload
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('preview').setAttribute('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}

// Confirm delete
function confirmDelete(formId) {
    if (confirm('Are you sure you want to delete this?')) {
        document.getElementById(formId).submit();
    }
    return false;
}

// Auto-resize textarea
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
});