from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
from openai import OpenAI
import re

def convert_link_video_id(url):
    reg_exp = r'^.*((youtu\.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*'
    match = re.match(reg_exp, url)
    return match.group(7) if match and len(match.group(7)) == 11 else False


def extract_caption(url):
    video_id = convert_link_video_id(url)
    transcript = YouTubeTranscriptApi.get_transcript(video_id) 

    new_transcript = {}
    for item in transcript:
        timestamp = f"{int(item['start'] // 60)}:{int(item['start'] % 60):02d}"
        new_transcript[timestamp] = item['text']

    return new_transcript


    
def create_summary(transcript):
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

    client = OpenAI()

    with open('./summary/prompt.txt', 'r') as prompt_file:
        prompt = prompt_file.read()

    combined_dict_text = '\n'.join([f"{key} {value}" for key, value in transcript.items()])
    final_prompt = prompt + '\n\n' + combined_dict_text

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": final_prompt}
        ]
    )

    timestamp = completion.choices[0].message.content

    return timestamp

def create_summary_gpt(transcript):
    client = OpenAI()

    with open('./summary/summary-prompt.txt', 'r') as prompt_file:
        prompt = prompt_file.read()

    combined_dict_text = '\n'.join([f"{key} {value}" for key, value in transcript.items()])
    final_prompt = prompt + '\n\n' + combined_dict_text

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": final_prompt}
        ]
    )

    summary = completion.choices[0].message.content

    return summary


video_id = '8DmqNhCDtDY'


# with open('summary.txt', 'w') as file:
#     for i in range(0, len(summary), 100):
#         file.write(summary[i:i+100] + '\n')