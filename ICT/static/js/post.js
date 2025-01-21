document.addEventListener('DOMContentLoaded', function() {
    const commentTextarea = document.querySelector('textarea[name="content"]');
    const commentCounter = document.querySelector('#commentCounter span');
    const maxLength = 1000;

    if (commentTextarea) {
        function updateCounter() {
            const remaining = maxLength - commentTextarea.value.length;
            commentCounter.textContent = remaining;
            
            if (remaining <= 20) {
                commentCounter.parentElement.classList.add('text-danger');
            } else if (remaining <= 50) {
                commentCounter.parentElement.classList.add('text-warning');
                commentCounter.parentElement.classList.remove('text-danger');
            } else {
                commentCounter.parentElement.classList.remove('text-warning', 'text-danger');
            }
        }

        commentTextarea.addEventListener('input', updateCounter);
        updateCounter();
    }
});

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
            document.getElementById(`vote-count-${postId}`).textContent = data.new_count;
            
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

function editComment(commentId) {
    const commentDiv = document.getElementById(`comment-${commentId}`);
    const content = commentDiv.querySelector('.comment-content').textContent.trim();
    
    document.getElementById('edit-comment-id').value = commentId;
    document.getElementById('edit-comment-content').value = content;
    
    const modal = new bootstrap.Modal(document.getElementById('editCommentModal'));
    modal.show();
}

function updateComment() {
    const commentId = document.getElementById('edit-comment-id').value;
    const content = document.getElementById('edit-comment-content').value;

    fetch(`/comment/${commentId}/update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const commentDiv = document.getElementById(`comment-${commentId}`);
            commentDiv.querySelector('.comment-content').textContent = content;
            
            // Add edited tag if not present
            const metadata = commentDiv.querySelector('.comment-metadata');
            if (!metadata.innerHTML.includes('edited')) {
                const timeSpan = metadata.querySelector('.text-muted');
                timeSpan.innerHTML += ' <span class="edited-tag"><i class="fas fa-edit"></i> edited</span>';
            }
            
            bootstrap.Modal.getInstance(document.getElementById('editCommentModal')).hide();
        }
    })
    .catch(error => console.error('Error:', error));
}

function deleteComment(commentId) {
    if (confirm('Are you sure you want to delete this comment?')) {
        fetch(`/comment/${commentId}/delete`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`comment-${commentId}`).remove();
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function confirmDelete(formId) {
    if (confirm('Are you sure you want to delete this post?')) {
        document.getElementById(formId).submit();
    }
    return false;
}