// Add this script to your dashboardone.html file to fix navigation links

// Execute when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get all navigation links in the sidebar
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    
    // Add click event listener to each link
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            // Get the text of the link
            const linkText = this.querySelector('.nav-text').textContent.trim().toLowerCase();
            
            // Define the correct URLs for each link
            const urls = {
                'dashboard': '/dashboard/',
                'subjects': '/subjects/',
                'schedule': '/schedule/',
                'tasks': '/tasks/',
                'progress': '/progress/',
                'insights': '/insights/',
                'peer comparison': '/peer-comparison/',
                'settings': '/settings/',
                'logout': '/logout/'
            };
            
            // If this link text is in our map
            if (urls[linkText]) {
                // Navigate to the correct URL
                window.location.href = urls[linkText];
                
                // Prevent default to ensure our navigation takes precedence
                event.preventDefault();
                
                // Log for debugging
                console.log(`Navigating to: ${urls[linkText]}`);
            }
        });
    });
    
    // Log that the script has been loaded
    console.log('Navigation fix script loaded');
});