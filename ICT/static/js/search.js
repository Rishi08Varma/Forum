document.addEventListener('DOMContentLoaded', function() {
    // Auto-submit form when changing filters
    document.querySelectorAll('input[name="type"]').forEach(radio => {
        radio.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });

    // Highlight search terms in results
    const query = new URLSearchParams(window.location.search).get('q');
    if (query) {
        const terms = query.toLowerCase().split(' ').filter(term => term.length > 2);
        
        // Function to highlight text
        function highlightText(element, terms) {
            const text = element.textContent;
            let highlighted = text;
            
            terms.forEach(term => {
                const regex = new RegExp(`(${term})`, 'gi');
                highlighted = highlighted.replace(regex, '<span class="highlight">$1</span>');
            });
            
            if (highlighted !== text) {
                element.innerHTML = highlighted;
            }
        }

        // Highlight text in post titles and content
        document.querySelectorAll('.post-result h5 a').forEach(element => {
            highlightText(element, terms);
        });
        document.querySelectorAll('.result-preview').forEach(element => {
            highlightText(element, terms);
        });

        // Highlight text in comments
        document.querySelectorAll('.result-content').forEach(element => {
            highlightText(element, terms);
        });

        // Highlight text in usernames
        document.querySelectorAll('.user-info h5 a').forEach(element => {
            highlightText(element, terms);
        });
    }

    // Handle form submission
    document.querySelector('.search-form').addEventListener('submit', function(e) {
        const query = this.querySelector('input[name="q"]').value.trim();
        if (!query) {
            e.preventDefault();
            this.querySelector('input[name="q"]').classList.add('is-invalid');
        }
    });

    // Remove invalid class on input
    document.querySelector('input[name="q"]').addEventListener('input', function() {
        this.classList.remove('is-invalid');
    });

    // Update URL without page reload when using filters
    document.querySelectorAll('input[name="type"]').forEach(radio => {
        radio.addEventListener('change', function(e) {
            e.preventDefault();
            const searchParams = new URLSearchParams(window.location.search);
            searchParams.set('type', this.value);
            searchParams.set('page', '1'); // Reset to first page when changing filters
            window.history.pushState({}, '', `${window.location.pathname}?${searchParams.toString()}`);
            // Then submit the form
            this.closest('form').submit();
        });
    });
});