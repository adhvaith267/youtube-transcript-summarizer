import json
import logging

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    Response,
    stream_with_context,
)

from yt_dlp import YoutubeDL

from services.youtube import (
    get_video_id,
    fetch_transcript,
)

from services.gemini import generate_summary_stream


main_routes = Blueprint("main", __name__)


@main_routes.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@main_routes.route("/get_transcripts", methods=["POST"])
def get_transcripts():
    """
    Fetch available transcripts and metadata for a YouTube video.
    """
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "URL is required."}), 400

    video_id = get_video_id(data["url"])
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL or ID."}), 400

    full_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(full_url, download=False)

        title = info.get("title", "No title found")
        thumbnail_url = info.get("thumbnail")
        subtitles = info.get("subtitles", {})

        if not subtitles:
            return jsonify({"error": "No subtitles found for this video."}), 404

        available_transcripts = []
        for lang_code, sub_info in subtitles.items():
            if (
                sub_info
                and isinstance(sub_info, list)
                and sub_info[0].get("url")
            ):
                available_transcripts.append(
                    {
                        "language": lang_code,
                        "language_code": lang_code,
                    }
                )

        if not available_transcripts:
            return jsonify(
                {"error": "No valid transcript URLs found."}
            ), 404

        return jsonify(
            {
                "video_id": video_id,
                "title": title,
                "thumbnail_url": thumbnail_url,
                "available_transcripts": available_transcripts,
            }
        )

    except Exception as e:
        logging.exception("Error fetching video metadata")
        return jsonify({"error": str(e)}), 500


@main_routes.route("/transcript", methods=["POST"])
def get_full_transcript():
    """
    Fetch the full transcript text for a selected language.
    """
    data = request.get_json()
    if not data or "url" not in data or "language_code" not in data:
        return jsonify(
            {"error": "URL and language_code are required."}
        ), 400

    video_id = get_video_id(data["url"])
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL or ID."}), 400

    full_url = f"https://www.youtube.com/watch?v={video_id}"
    transcript_text = fetch_transcript(
        full_url, data["language_code"]
    )

    if transcript_text:
        return jsonify({"transcript": transcript_text})

    return jsonify(
        {
            "error": f"Could not retrieve transcript for language '{data['language_code']}'."
        }
    ), 404


@main_routes.route("/summarize_stream", methods=["POST"])
def summarize_stream():
    """
    Generate and stream a summary from transcript text using Gemini.
    """
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify(
            {"error": "Text for summarization is required."}
        ), 400

    text = data["text"]

    # IMPORTANT: Use human-readable language names
    summary_language = data.get("summary_language", "English")

    def generate():
        try:
            for chunk in generate_summary_stream(
                text, summary_language
            ):
                yield json.dumps(
                    {"summary_chunk": chunk}
                ) + "\n"
        except Exception as e:
            logging.exception("Streaming summary failed")
            yield json.dumps(
                {"error": str(e)}
            ) + "\n"

    return Response(
        stream_with_context(generate()),
        mimetype="application/x-json-stream",
    )
