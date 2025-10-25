from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
import google.generativeai as genai
import os
import re
import requests
import json


def convert_link_video_id(url):
    """Extract 11-character video ID from YouTube URL"""
    reg_exp = r'^.*((youtu\.be\/)|(v\/)|(/u/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*'
    match = re.match(reg_exp, url)
    return match.group(7) if match and len(match.group(7)) == 11 else False


def extract_caption(url):
    """Extract video transcript using URLToText API and format as timestamp dict"""
    video_id = convert_link_video_id(url)
    
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    # Load API key from environment
    api_token = os.getenv('URLTOTEXT_API_KEY')
    
    if not api_token:
        raise ValueError("URLTOTEXT_API_KEY not set in .env file")
    
    # Configure API request
    headers = {
        'Authorization': f'Token {api_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "url": url,
        "output_format": "text",
        "extract_main_content": True,
        "render_javascript": True
    }
    
    try:
        # Call URLToText API to extract transcript
        response = requests.post(
            'https://urltotext.com/api/v1/urltotext/',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"URLToText API error: {response.status_code} - {response.text}")
        
        data = response.json()
        content = data['data'].get('content', '')
        credits_used = float(data.get('credits_used', 0))
        
        # Track API credit usage locally (for monitoring)
        try:
            tracker_path = './credits_tracker.json'
            if os.path.exists(tracker_path):
                with open(tracker_path, 'r') as f:
                    tracker = json.load(f)
                tracker['total_used'] = tracker.get('total_used', 0) + credits_used
                remaining = tracker.get('initial_balance', 0.02) - tracker['total_used']
                with open(tracker_path, 'w') as f:
                    json.dump(tracker, f)
                print(f"[URLToText API] Credits used: {credits_used:.5f} | Estimated remaining: {remaining:.5f}")
            else:
                print(f"[URLToText API] Credits used: {credits_used}")
        except:
            print(f"[URLToText API] Credits used: {credits_used}")
        
        if not content:
            raise ValueError("No content extracted from video")
        
        # Convert raw text into timestamp-based structure
        # URLToText doesn't provide timestamps, so we estimate them
        sentences = content.split('. ')
        
        new_transcript = {}
        time_offset = 0
        
        # Estimate timestamps based on average speaking rate (150 words/min)
        for sentence in sentences:
            if sentence.strip():
                word_count = len(sentence.split())
                duration = (word_count / 150) * 60  # Convert to seconds
                
                timestamp = f"{int(time_offset // 60)}:{int(time_offset % 60):02d}"
                new_transcript[timestamp] = sentence.strip()
                time_offset += duration
        
        return new_transcript
        
    except Exception as e:
        raise Exception(f"Failed to extract captions: {str(e)}")



def create_summary(transcript):
    """LEGACY: Create summary using HuggingFace model (not currently used)"""
    summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6",
        revision="a4f8f3e"
    )
    text_transcript = list(transcript.values())[:100]
    full_text = " ".join(text_transcript)

    summary = summarizer(full_text, max_length=225, min_length=175, do_sample=False)
    summary_text = summary[0]['summary_text']
    punctuated_summary = ' '.join(sent_tokenize(summary_text))

    return punctuated_summary


def create_timestamps(transcript):
    """Generate key timestamps with labels using Gemini AI"""
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Load timestamp prompt template
    with open('./summary/prompt.txt', 'r') as prompt_file:
        prompt = prompt_file.read()

    # Format transcript for Gemini
    combined_dict_text = '\n'.join([f"{key} {value}" for key, value in transcript.items()])
    final_prompt = prompt + '\n\n' + combined_dict_text

    # Generate timestamps with Gemini
    response = model.generate_content(final_prompt)
    timestamp = response.text

    return timestamp

def create_summary_gpt(transcript):
    """Generate concise video summary using Gemini AI"""
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Load summary prompt template
    with open('./summary/summary-prompt.txt', 'r') as prompt_file:
        prompt = prompt_file.read()

    # Format transcript for Gemini
    combined_dict_text = '\n'.join([f"{key} {value}" for key, value in transcript.items()])
    final_prompt = prompt + '\n\n' + combined_dict_text

    # Generate summary with Gemini
    response = model.generate_content(final_prompt)
    summary = response.text

    return summary

