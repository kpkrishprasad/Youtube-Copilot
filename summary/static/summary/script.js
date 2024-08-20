function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.getElementById('summaryForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const youtubeLink = document.getElementById('youtube_link').value;
    const csrftoken = getCookie('csrftoken');

    // Show loading indicator
    document.getElementById('loading').style.display = 'block';

    fetch('/get_summary/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: new URLSearchParams({
            'youtube_link': youtubeLink
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.summary) {
            document.getElementById('summaryText').innerText = data.summary;
            document.getElementById('summaryContainer').style.display = 'block';
        } else {
            alert('Error: ' + data.error);
        }
        // Hide loading indicator
        document.getElementById('loading').style.display = 'none';
    })
    .catch(error => {
        alert('Failed to fetch summary.');
        // Hide loading indicator
        document.getElementById('loading').style.display = 'none';
    });
});
