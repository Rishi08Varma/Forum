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