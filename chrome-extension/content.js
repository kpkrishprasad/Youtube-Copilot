// Content script that runs on YouTube pages
// This can be used to add a summary button directly on YouTube videos

console.log('YouTube Copilot extension loaded');

// Function to add a summary button to the YouTube page
function addSummaryButton() {
    // Check if we're on a video page
    if (!window.location.href.includes('youtube.com/watch')) {
        return;
    }

    // Check if button already exists
    if (document.getElementById('yt-copilot-btn')) {
        return;
    }

    // Wait for YouTube's UI to load
    const checkElement = setInterval(() => {
        const menuBar = document.querySelector('#top-level-buttons-computed');
        
        if (menuBar) {
            clearInterval(checkElement);
            
            // Create button container
            const buttonContainer = document.createElement('div');
            buttonContainer.id = 'yt-copilot-btn';
            buttonContainer.style.cssText = `
                display: inline-flex;
                align-items: center;
                margin-left: 8px;
            `;

            // Create the button
            const button = document.createElement('button');
            button.innerHTML = '✨ Get Summary';
            button.style.cssText = `
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 18px;
                font-weight: 500;
                font-size: 14px;
                cursor: pointer;
                transition: transform 0.2s;
            `;

            button.addEventListener('mouseenter', () => {
                button.style.transform = 'scale(1.05)';
            });

            button.addEventListener('mouseleave', () => {
                button.style.transform = 'scale(1)';
            });

            button.addEventListener('click', () => {
                // Open the extension popup by sending a message
                const videoUrl = window.location.href;
                chrome.runtime.sendMessage({
                    action: 'openPopup',
                    url: videoUrl
                });
            });

            buttonContainer.appendChild(button);
            menuBar.appendChild(buttonContainer);
        }
    }, 500);

    // Clear interval after 10 seconds if element not found
    setTimeout(() => clearInterval(checkElement), 10000);
}

// Run when page loads
addSummaryButton();

// Run when YouTube dynamically changes pages (SPA navigation)
let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        addSummaryButton();
    }
}).observe(document, { subtree: true, childList: true });

