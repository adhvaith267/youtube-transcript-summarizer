import json
import logging
from flask import Blueprint, request, jsonify, render_template, Response, stream_with_context
from yt_dlp import YoutubeDL
import requests

from services.youtube import get_video_id, fetch_transcript, _parse_vtt_transcript, _parse_json3_transcript
from services.gemini import generate_summary_stream

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@main_routes.route('/get_transcripts', methods=['POST'])
def get_transcripts():
    """
    API endpoint to find available transcripts for a YouTube video.
    This endpoint fetches all video metadata at once for efficiency.
    """
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required.'}), 400

    video_id = get_video_id(data['url'])
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL or ID.'}), 400

    full_url = f'https://www.youtube.com/watch?v={video_id}'
    
    try:
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'quiet': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(full_url, download=False)

        title = info.get('title', 'No title found')
        thumbnail_url = info.get('thumbnail')
        subtitles = info.get('subtitles', {})

        if not subtitles:
            return jsonify({'error': 'No subtitles found for this video.'}), 404

        available_transcripts = []
        for lang_code, sub_info in subtitles.items():
            if sub_info and isinstance(sub_info, list) and sub_info[0].get('url'):
                available_transcripts.append({
                    'language': lang_code, 
                    'language_code': lang_code
                })
        
        if not available_transcripts:
            return jsonify({'error': 'Could not find any valid transcript URLs.'}), 404

        return jsonify({
            'video_id': video_id,
            'title': title,
            'thumbnail_url': thumbnail_url,
            'available_transcripts': available_transcripts
        })

    except Exception as e:
        logging.error(f"Error fetching video details for {full_url}: {e}")
        return jsonify({'error': f'An error occurred: {e}'}), 500

@main_routes.route('/transcript', methods=['POST'])
def get_full_transcript():
    """API endpoint to fetch the full text of a specific transcript."""
    data = request.get_json()
    if not data or 'url' not in data or 'language_code' not in data:
        return jsonify({'error': 'URL and language_code are required.'}), 400

    video_id = get_video_id(data['url'])
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL or ID.'}), 400

    full_url = f'https://www.youtube.com/watch?v={video_id}'
    transcript_text = fetch_transcript(full_url, data['language_code'])

    if transcript_text:
        return jsonify({'transcript': transcript_text})
    
    return jsonify({'error': f"Could not retrieve transcript for language '{data['language_code']}'."}), 404

@main_routes.route('/summarize_stream', methods=['POST'])
def summarize_stream():
    """API endpoint to generate and stream a summary from transcript text."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Text for summarization is required.'}), 400

    text = data['text']
    # Default to English if no language is provided
    summary_language = data.get('summary_language', 'en')

    def generate():
        for chunk in generate_summary_stream(text, summary_language):
            yield f"{json.dumps({'summary_chunk': chunk})}\n"

    return Response(stream_with_context(generate()), mimetype='application/x-json-stream') 