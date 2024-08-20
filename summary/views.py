from django.shortcuts import render
from django.http import JsonResponse
from .extract_caption import *
import os

def index(request):
    return render(request, 'summary/index.html')




def get_summary(request):
    if request.method == 'POST':
        youtube_link = request.POST.get('youtube_link')
        captions = extract_caption(youtube_link)
        summary = create_summary_gpt(captions)
        timestamps = create_timestamps(captions)

        return JsonResponse({'summary': summary + '\n' + '\n' + timestamps})
    return JsonResponse({'error': 'Invalid request'}, status=400)


