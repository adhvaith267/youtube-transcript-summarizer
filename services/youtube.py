import logging
import json
from urllib.parse import urlparse, parse_qs
import requests
from yt_dlp import YoutubeDL

def get_video_id(url_or_id: str) -> str | None:
    """
    Extracts a YouTube video ID from a URL or returns the input if it's already a valid ID.

    Args:
        url_or_id: The YouTube URL or a video ID string.

    Returns:
        The 11-character video ID, or None if not found.
    """
    if len(url_or_id) == 11 and url_or_id.replace("-", "").isalnum():
        return url_or_id
    
    parsed_url = urlparse(url_or_id)
    if 'youtube.com' in parsed_url.hostname:
        qs = parse_qs(parsed_url.query)
        return qs.get('v', [None])[0]
    elif 'youtu.be' in parsed_url.hostname:
        return parsed_url.path.lstrip('/')
    
    return None

def fetch_transcript(video_url: str, language_code: str = 'en') -> str | None:
    """
    Fetches the transcript for a given YouTube video URL using yt-dlp.

    This function prioritizes fetching the VTT format and includes a fallback
    to parse JSON3 format if VTT is not available.

    Args:
        video_url: The full URL of the YouTube video.
        language_code: The language code for the desired transcript (e.g., 'en', 'es').

    Returns:
        A string containing the formatted transcript text, or None if no transcript
        could be fetched or processed.
    """
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'subtitleslangs': [language_code],
        'subtitlesformat': 'vtt/json3',
        'quiet': True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            requested_subs = info.get('requested_subtitles')
            if not requested_subs:
                logging.warning(f"No subtitles found for language '{language_code}'")
                return None

            subtitle_url = requested_subs[language_code]['url']
            response = requests.get(subtitle_url)
            response.raise_for_status()
            
            content = response.text
            
            # If content is JSON3, convert to plain text
            if content.lstrip().startswith('{'):
                return _parse_json3_transcript(content)
            
            # Otherwise, treat as VTT and clean it
            return _parse_vtt_transcript(content)

    except Exception as e:
        logging.error(f"yt-dlp error fetching transcript for {video_url}: {e}")
        return None

def _parse_vtt_transcript(content: str) -> str:
    """Parses a VTT-formatted transcript into a clean string."""
    lines = content.splitlines()
    text_lines = [
        line.strip() for line in lines 
        if line.strip() and '-->' not in line and not line.startswith(('WEBVTT', 'NOTE', 'Kind:', 'Language:'))
    ]
    return ' '.join(text_lines)

def _parse_json3_transcript(content: str) -> str | None:
    """Parses a JSON3-formatted transcript into a clean string."""
    try:
        data = json.loads(content)
        events = data.get('events', [])
        text_lines = []
        for event in events:
            for segment in event.get('segs', []):
                text_lines.append(segment.get('utf8', ''))
        return ' '.join(text_lines)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON3 subtitles: {e}")
        return None 