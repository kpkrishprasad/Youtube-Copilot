const API_URL = 'http://127.0.0.1:8000/get_summary/';
const QA_URL = 'http://127.0.0.1:8000/ask_question/';
const RESEARCH_URL = 'http://127.0.0.1:8000/youtube_research/';

let currentVideoUrl = '';
let currentVideoId = '';

const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

// Extract video ID from YouTube URL
function extractVideoId(url) {
    const regex = /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

// Load cached data for current video
async function loadCachedData() {
    const youtubeLink = document.getElementById('youtube_link').value.trim();
    if (!youtubeLink) return;
    
    const videoId = extractVideoId(youtubeLink);
    if (!videoId) return;
    
    currentVideoId = videoId;
    currentVideoUrl = youtubeLink;
    
    // Get cached data from chrome.storage
    chrome.storage.local.get(['videoCache'], (result) => {
        const cache = result.videoCache || {};
        const cachedVideo = cache[videoId];
        
        if (cachedVideo && cachedVideo.expiresAt > Date.now()) {
            // Cache is valid, restore data
            console.log('Loading cached data for video:', videoId);
            restoreCachedData(cachedVideo);
        } else if (cachedVideo) {
            // Cache expired, remove it
            delete cache[videoId];
            chrome.storage.local.set({ videoCache: cache });
        }
    });
}

// Restore cached data to UI
function restoreCachedData(cachedVideo) {
    // Display summary and timestamps
    document.getElementById('summaryOnlyText').textContent = cachedVideo.summary || '';
    document.getElementById('timestampsOnlyText').textContent = cachedVideo.timestamps || '';
    
    // Restore Q&A chat history
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '';
    if (cachedVideo.chatHistory && cachedVideo.chatHistory.length > 0) {
        cachedVideo.chatHistory.forEach(msg => {
            addChatMessage(msg.text, msg.type);
        });
    }
    
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
}

// Save data to cache
function saveToCache(videoId, summary, timestamps, chatHistory) {
    chrome.storage.local.get(['videoCache'], (result) => {
        const cache = result.videoCache || {};
        
        cache[videoId] = {
            summary: summary,
            timestamps: timestamps,
            chatHistory: chatHistory,
            timestamp: Date.now(),
            expiresAt: Date.now() + CACHE_DURATION
        };
        
        chrome.storage.local.set({ videoCache: cache }, () => {
            console.log('Cached data for video:', videoId);
        });
    });
}

// Update chat history in cache
function updateChatHistoryInCache() {
    if (!currentVideoId) return;
    
    // Get current chat messages
    const chatMessages = document.getElementById('chatMessages');
    const messages = Array.from(chatMessages.children).map(msg => ({
        text: msg.textContent,
        type: msg.className.replace('chat-message ', '')
    })).filter(msg => msg.type !== 'loading'); // Exclude loading messages
    
    chrome.storage.local.get(['videoCache'], (result) => {
        const cache = result.videoCache || {};
        if (cache[currentVideoId]) {
            cache[currentVideoId].chatHistory = messages;
            chrome.storage.local.set({ videoCache: cache });
        }
    });
}

// Auto-fill URL if on YouTube page and load cached data
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const currentTab = tabs[0];
    if (currentTab.url && currentTab.url.includes('youtube.com/watch')) {
        document.getElementById('youtube_link').value = currentTab.url;
        loadCachedData();
    }
});

// Load cached data when URL input changes
document.getElementById('youtube_link').addEventListener('input', () => {
    loadCachedData();
});

// Load cached research data on popup open
chrome.storage.local.get(['lastResearchQuery'], (result) => {
    if (result.lastResearchQuery) {
        document.getElementById('researchQuery').value = result.lastResearchQuery;
        loadCachedResearch();
    }
});

// Handle summary button click
document.getElementById('getSummaryBtn').addEventListener('click', async () => {
    const youtubeLink = document.getElementById('youtube_link').value.trim();
    
    if (!youtubeLink) {
        showError('Please enter a YouTube URL');
        return;
    }

    if (!youtubeLink.includes('youtube.com') && !youtubeLink.includes('youtu.be')) {
        showError('Please enter a valid YouTube URL');
        return;
    }

    await getSummary(youtubeLink);
});

// Allow Enter key to submit
document.getElementById('youtube_link').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('getSummaryBtn').click();
    }
});

async function getSummary(youtubeLink) {
    // Show loading, hide previous results
    document.getElementById('loading').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorContainer').style.display = 'none';

    try {
        const formData = new URLSearchParams();
        formData.append('youtube_link', youtubeLink);

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        document.getElementById('loading').style.display = 'none';

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.summary) {
            // Split the response into summary and timestamps
            const fullText = data.summary;
            const parts = fullText.split('\n\n');
            
            // First part is summary, second part is timestamps
            let summaryText = '';
            let timestampsText = '';
            
            if (parts.length >= 2) {
                // Find where timestamps start (usually after "Summary" section)
                const combinedText = fullText;
                const timestampMarkers = ['0:', '1:', '2:', '3:', '4:', '5:', '6:', '7:', '8:', '9:'];
                
                // Find first timestamp
                let splitIndex = -1;
                for (let marker of timestampMarkers) {
                    const index = combinedText.indexOf('\n' + marker);
                    if (index !== -1 && (splitIndex === -1 || index < splitIndex)) {
                        splitIndex = index;
                    }
                }
                
                if (splitIndex !== -1) {
                    summaryText = combinedText.substring(0, splitIndex).trim();
                    timestampsText = combinedText.substring(splitIndex).trim();
                } else {
                    summaryText = fullText;
                    timestampsText = 'No timestamps available';
                }
            } else {
                summaryText = fullText;
                timestampsText = 'No timestamps available';
            }
            
            // Display in separate tabs
            document.getElementById('summaryOnlyText').textContent = summaryText;
            document.getElementById('timestampsOnlyText').textContent = timestampsText;
            
            // Show results section and store video URL
            currentVideoUrl = youtubeLink;
            currentVideoId = extractVideoId(youtubeLink);
            document.getElementById('resultsSection').style.display = 'block';
            
            // Clear old chat history for new analysis
            document.getElementById('chatMessages').innerHTML = '';
            
            // Save to cache
            if (currentVideoId) {
                saveToCache(currentVideoId, summaryText, timestampsText, []);
            }
        } else if (data.error) {
            showError(data.error);
        } else {
            showError('No summary returned from server');
        }

    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        console.error('Error:', error);
        showError(`Failed to fetch summary: ${error.message}`);
    }
}

function showError(message) {
    document.getElementById('errorText').textContent = message;
    document.getElementById('errorContainer').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
}

// Q&A Functionality
document.getElementById('askBtn').addEventListener('click', async () => {
    await askQuestion();
});

document.getElementById('questionInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        askQuestion();
    }
});

async function askQuestion() {
    const question = document.getElementById('questionInput').value.trim();
    
    if (!question) {
        return;
    }
    
    if (!currentVideoUrl) {
        addChatMessage('Please generate a summary first!', 'error');
        return;
    }
    
    // Add user question to chat
    addChatMessage(question, 'user');
    document.getElementById('questionInput').value = '';
    
    // Show loading indicator
    addChatMessage('Thinking...', 'loading');
    
    try {
        const formData = new URLSearchParams();
        formData.append('youtube_link', currentVideoUrl);
        formData.append('question', question);
        
        const response = await fetch(QA_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        // Remove loading message
        removeLoadingMessage();
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.answer) {
            addChatMessage(data.answer, 'bot');
            // Update cache with new chat message
            updateChatHistoryInCache();
        } else if (data.error) {
            addChatMessage(`Error: ${data.error}`, 'error');
        } else {
            addChatMessage('No answer returned from server', 'error');
        }
        
    } catch (error) {
        removeLoadingMessage();
        console.error('Error:', error);
        addChatMessage(`Failed to get answer: ${error.message}`, 'error');
    }
}

function addChatMessage(message, type) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoadingMessage() {
    const chatMessages = document.getElementById('chatMessages');
    const loadingMessages = chatMessages.querySelectorAll('.chat-message.loading');
    loadingMessages.forEach(msg => msg.remove());
}

// Main Tab Switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.getAttribute('data-tab');
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab pane
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Load cached research when switching to research tab
    if (tabName === 'research') {
        loadCachedResearch();
    }
}

// Sub-tab Switching
document.querySelectorAll('.sub-tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const subTabName = button.getAttribute('data-subtab');
        switchSubTab(subTabName);
    });
});

function switchSubTab(subTabName) {
    // Hide all sub-tab panes
    document.querySelectorAll('.sub-tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Remove active class from all sub-tab buttons
    document.querySelectorAll('.sub-tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected sub-tab pane
    document.getElementById(subTabName).classList.add('active');
    
    // Add active class to clicked button
    document.querySelector(`[data-subtab="${subTabName}"]`).classList.add('active');
}

// YouTube Research Functionality
document.getElementById('researchBtn').addEventListener('click', async () => {
    await doResearch();
});

document.getElementById('researchQuery').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        doResearch();
    }
});

async function doResearch() {
    const query = document.getElementById('researchQuery').value.trim();
    
    if (!query) {
        showResearchError('Please enter a research topic');
        return;
    }
    
    // Show loading
    document.getElementById('researchLoading').style.display = 'block';
    document.getElementById('researchResults').style.display = 'none';
    document.getElementById('researchError').style.display = 'none';
    
    try {
        const formData = new URLSearchParams();
        formData.append('query', query);
        
        const response = await fetch(RESEARCH_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        document.getElementById('researchLoading').style.display = 'none';
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            showResearchError(data.error);
            return;
        }
        
        // Display results
        document.getElementById('searchQuery').textContent = data.search_query;
        document.getElementById('guideContent').textContent = data.guide;
        
        // Display videos
        const videosList = document.getElementById('videosList');
        videosList.innerHTML = '';
        
        data.videos.forEach((video, index) => {
            const videoDiv = document.createElement('div');
            videoDiv.className = 'video-item';
            videoDiv.innerHTML = `
                <a href="${video.url}" target="_blank">${index + 1}. ${video.title}</a>
            `;
            videosList.appendChild(videoDiv);
        });
        
        document.getElementById('researchResults').style.display = 'block';
        
        // Save research to cache and remember query
        saveResearchToCache(query, data.search_query, data.guide, data.videos);
        chrome.storage.local.set({ lastResearchQuery: query });
        
    } catch (error) {
        document.getElementById('researchLoading').style.display = 'none';
        console.error('Research error:', error);
        showResearchError(`Failed to research topic: ${error.message}`);
    }
}

function showResearchError(message) {
    document.getElementById('researchErrorText').textContent = message;
    document.getElementById('researchError').style.display = 'block';
    document.getElementById('researchResults').style.display = 'none';
}

// Research caching functions
function saveResearchToCache(query, searchQuery, guide, videos) {
    chrome.storage.local.get(['researchCache'], (result) => {
        const cache = result.researchCache || {};
        
        cache[query] = {
            searchQuery: searchQuery,
            guide: guide,
            videos: videos,
            timestamp: Date.now(),
            expiresAt: Date.now() + CACHE_DURATION
        };
        
        chrome.storage.local.set({ researchCache: cache }, () => {
            console.log('Cached research data for query:', query);
        });
    });
}

function loadCachedResearch() {
    const query = document.getElementById('researchQuery').value.trim();
    if (!query) return;
    
    chrome.storage.local.get(['researchCache'], (result) => {
        const cache = result.researchCache || {};
        const cachedResearch = cache[query];
        
        if (cachedResearch && cachedResearch.expiresAt > Date.now()) {
            // Cache is valid, restore data
            console.log('Loading cached research data for query:', query);
            restoreCachedResearch(cachedResearch);
        } else if (cachedResearch) {
            // Cache expired, remove it
            delete cache[query];
            chrome.storage.local.set({ researchCache: cache });
        }
    });
}

function restoreCachedResearch(cachedResearch) {
    document.getElementById('searchQuery').textContent = cachedResearch.searchQuery;
    document.getElementById('guideContent').textContent = cachedResearch.guide;
    
    // Display videos
    const videosList = document.getElementById('videosList');
    videosList.innerHTML = '';
    
    cachedResearch.videos.forEach((video, index) => {
        const videoDiv = document.createElement('div');
        videoDiv.className = 'video-item';
        videoDiv.innerHTML = `
            <a href="${video.url}" target="_blank">${index + 1}. ${video.title}</a>
        `;
        videosList.appendChild(videoDiv);
    });
    
    document.getElementById('researchResults').style.display = 'block';
}

// Load cached research when query input changes
document.getElementById('researchQuery').addEventListener('input', () => {
    loadCachedResearch();
});


// Email functionality
const EMAIL_SUMMARY_URL = 'http://127.0.0.1:8000/email_summary/';
const EMAIL_RESEARCH_URL = 'http://127.0.0.1:8000/email_research/';

let currentEmailType = null; // 'summary' or 'research'
let currentResearchData = null;

// Load saved email on popup load
chrome.storage.local.get(['savedEmail'], (result) => {
    if (result.savedEmail) {
        document.getElementById('emailInput').value = result.savedEmail;
        document.getElementById('rememberEmail').checked = true;
    }
});

// Email Summary Button
document.getElementById('emailSummaryBtn').addEventListener('click', () => {
    currentEmailType = 'summary';
    document.getElementById('emailModal').style.display = 'flex';
    document.getElementById('emailStatus').textContent = '';
    document.getElementById('emailStatus').className = 'email-status';
});

// Email Research Button
document.getElementById('emailResearchBtn').addEventListener('click', () => {
    currentEmailType = 'research';
    document.getElementById('emailModal').style.display = 'flex';
    document.getElementById('emailStatus').textContent = '';
    document.getElementById('emailStatus').className = 'email-status';
});

// Close modal
document.querySelector('.close-modal').addEventListener('click', () => {
    document.getElementById('emailModal').style.display = 'none';
});

// Close modal when clicking outside
document.getElementById('emailModal').addEventListener('click', (e) => {
    if (e.target.id === 'emailModal') {
        document.getElementById('emailModal').style.display = 'none';
    }
});

// Send Email Button
document.getElementById('sendEmailBtn').addEventListener('click', async () => {
    const email = document.getElementById('emailInput').value.trim();
    const rememberEmail = document.getElementById('rememberEmail').checked;
    const statusEl = document.getElementById('emailStatus');
    const sendBtn = document.getElementById('sendEmailBtn');
    
    if (!email) {
        statusEl.textContent = 'Please enter an email address';
        statusEl.className = 'email-status error';
        return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        statusEl.textContent = 'Please enter a valid email address';
        statusEl.className = 'email-status error';
        return;
    }
    
    // Save email if remember is checked
    if (rememberEmail) {
        chrome.storage.local.set({ savedEmail: email });
    } else {
        chrome.storage.local.remove('savedEmail');
    }
    
    // Disable button and show loading
    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending...';
    statusEl.textContent = '';
    
    try {
        if (currentEmailType === 'summary') {
            await sendSummaryEmail(email);
        } else if (currentEmailType === 'research') {
            await sendResearchEmail(email);
        }
        
        statusEl.textContent = '✅ Email sent successfully!';
        statusEl.className = 'email-status success';
        
        // Close modal after 2 seconds
        setTimeout(() => {
            document.getElementById('emailModal').style.display = 'none';
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send Email';
        }, 2000);
        
    } catch (error) {
        statusEl.textContent = `Error: ${error.message}`;
        statusEl.className = 'email-status error';
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send Email';
    }
});

async function sendSummaryEmail(email) {
    const summary = document.getElementById('summaryOnlyText').textContent;
    const timestamps = document.getElementById('timestampsOnlyText').textContent;
    
    // Get chat history
    const chatMessages = document.getElementById('chatMessages');
    const chatHistory = Array.from(chatMessages.children)
        .filter(msg => !msg.classList.contains('loading'))
        .map(msg => ({
            text: msg.textContent,
            type: msg.className.includes('user') ? 'user' : 'bot'
        }));
    
    const formData = new URLSearchParams();
    formData.append('email', email);
    formData.append('video_url', currentVideoUrl);
    formData.append('summary', summary);
    formData.append('timestamps', timestamps);
    formData.append('chat_history', JSON.stringify(chatHistory));
    
    const response = await fetch(EMAIL_SUMMARY_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    });
    
    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to send email');
    }
}

async function sendResearchEmail(email) {
    const query = document.getElementById('researchQuery').value;
    const searchQuery = document.getElementById('searchQuery').textContent;
    const guide = document.getElementById('guideContent').textContent;
    
    // Get videos list
    const videosList = document.getElementById('videosList');
    const videos = Array.from(videosList.querySelectorAll('.video-item')).map(item => {
        const link = item.querySelector('a');
        return {
            title: link.textContent.substring(link.textContent.indexOf('. ') + 2),
            url: link.href
        };
    });
    
    const formData = new URLSearchParams();
    formData.append('email', email);
    formData.append('query', query);
    formData.append('search_query', searchQuery);
    formData.append('guide', guide);
    formData.append('videos', JSON.stringify(videos));
    
    const response = await fetch(EMAIL_RESEARCH_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    });
    
    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to send email');
    }
}
