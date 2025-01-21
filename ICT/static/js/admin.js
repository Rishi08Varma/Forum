document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // User search functionality
    const userSearch = document.getElementById('userSearch');
    if (userSearch) {
        userSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('tbody tr');
            
            tableRows.forEach(row => {
                const username = row.querySelector('td:first-child').textContent.toLowerCase();
                const email = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                row.style.display = (username.includes(searchTerm) || email.includes(searchTerm)) ? '' : 'none';
            });
        });
    }

    // Delete User Confirmation
    const deleteModals = document.querySelectorAll('[id^="deleteUserModal-"]');
    deleteModals.forEach(modal => {
        const confirmInput = modal.querySelector('.confirm-delete');
        const deleteBtn = modal.querySelector('.delete-user-btn');

        if (confirmInput && deleteBtn) {
            // Handle input changes
            confirmInput.addEventListener('input', function() {
                // Enable button only if input exactly matches "DELETE"
                deleteBtn.disabled = this.value !== 'DELETE';
            });

            // Reset modal when closed
            modal.addEventListener('hidden.bs.modal', function() {
                confirmInput.value = '';
                deleteBtn.disabled = true;
            });
        }
    });

    // Update timestamp
    const timestamp = document.querySelector('.admin-header small.text-muted');
    if (timestamp) {
        // Update timestamp every minute
        function updateTimestamp() {
            const now = new Date();
            const formattedDate = now.getUTCFullYear() + '-' + 
                                String(now.getUTCMonth() + 1).padStart(2, '0') + '-' + 
                                String(now.getUTCDate()).padStart(2, '0') + ' ' + 
                                String(now.getUTCHours()).padStart(2, '0') + ':' + 
                                String(now.getUTCMinutes()).padStart(2, '0') + ':' + 
                                String(now.getUTCSeconds()).padStart(2, '0');
            timestamp.textContent = 'Last Updated: ' + formattedDate;
        }
        updateTimestamp();
        setInterval(updateTimestamp, 60000); // Update every minute
    }

    // Add animation to statistics
    const statNumbers = document.querySelectorAll('.stat-details h3');
    statNumbers.forEach(stat => {
        const finalNumber = parseInt(stat.textContent);
        if (!isNaN(finalNumber)) {
            let currentNumber = 0;
            const duration = 1000; // 1 second animation
            const increment = finalNumber / (duration / 16); // 60fps
            
            function updateNumber() {
                currentNumber = Math.min(currentNumber + increment, finalNumber);
                stat.textContent = Math.round(currentNumber);
                
                if (currentNumber < finalNumber) {
                    requestAnimationFrame(updateNumber);
                }
            }
            
            updateNumber();
        }
    });

    // Add hover effect to table rows
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = '#f8f9fa';
            row.style.transition = 'background-color 0.3s ease';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = '';
        });
    });

    // Add copy functionality for email addresses
    const emailCells = document.querySelectorAll('td:nth-child(2)');
    emailCells.forEach(cell => {
        cell.style.cursor = 'pointer';
        cell.title = 'Click to copy email';
        cell.addEventListener('click', function() {
            const email = this.textContent;
            navigator.clipboard.writeText(email).then(() => {
                // Show temporary success message
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                setTimeout(() => {
                    this.textContent = originalText;
                }, 1000);
            }).catch(err => {
                console.error('Failed to copy email:', err);
            });
        });
    });

    // Add smooth fade-in animation for content
    document.querySelector('.container').style.opacity = '0';
    setTimeout(() => {
        document.querySelector('.container').style.transition = 'opacity 0.5s ease';
        document.querySelector('.container').style.opacity = '1';
    }, 100);

    // Console log for debugging
    console.log('Admin panel initialized successfully');
    console.log('Current user:', 'Rishi08Varma');
    console.log('Last updated:', new Date().toUTCString());
});

// Prevent form resubmission on page refresh
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}