from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import re

from flask import Flask, render_template, request, send_from_directory
from youtube_transcript_api import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)


BASE_DIR = Path(__file__).resolve().parent
TRANSCRIPTIONS_DIR = BASE_DIR / "transcriptions"
TRANSCRIPTIONS_DIR.mkdir(exist_ok=True)

app = Flask(__name__)


def format_datetime(value: float) -> str:
    return datetime.fromtimestamp(value).strftime("%d/%m/%Y %H:%M")


def extract_video_id(video_url: str) -> str | None:
    parsed_url = urlparse(video_url.strip())
    host = parsed_url.netloc.lower().replace("www.", "")

    if host == "youtu.be":
        candidate = parsed_url.path.strip("/")
        return candidate or None

    if host in {"youtube.com", "m.youtube.com"}:
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query).get("v", [None])[0]

        path_parts = [part for part in parsed_url.path.split("/") if part]
        if len(path_parts) >= 2 and path_parts[0] in {"shorts", "embed", "live"}:
            return path_parts[1]

    raw_input_match = re.fullmatch(r"[A-Za-z0-9_-]{11}", video_url.strip())
    if raw_input_match:
        return raw_input_match.group(0)

    generic_match = re.search(r"(?:v=|/)([A-Za-z0-9_-]{11})(?:[?&/]|$)", video_url)
    if generic_match:
        return generic_match.group(1)

    return None


def fetch_transcript_text(video_id: str) -> tuple[str, str]:
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id, languages=["fr", "en"])
    text = "\n".join(snippet.text.strip() for snippet in transcript if snippet.text.strip())

    if not text:
        raise ValueError("La transcription recuperee est vide.")

    return text, transcript.language


def build_transcript_stats(video_id: str, transcript_text: str) -> dict[str, str | int]:
    non_empty_lines = [line for line in transcript_text.splitlines() if line.strip()]
    return {
        "video_id": video_id,
        "character_count": len(transcript_text),
        "word_count": len(transcript_text.split()),
        "line_count": len(non_empty_lines),
    }


def list_recent_transcriptions(limit: int = 6) -> list[dict[str, str]]:
    recent_files = sorted(
        TRANSCRIPTIONS_DIR.glob("transcript-*.txt"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:limit]

    history: list[dict[str, str]] = []
    for file_path in recent_files:
        file_stats = file_path.stat()
        history.append(
            {
                "file_name": file_path.name,
                "modified_at": format_datetime(file_stats.st_mtime),
                "size": f"{max(file_stats.st_size / 1024, 0.1):.1f} Ko",
            }
        )

    return history


def save_transcript(
    video_id: str,
    transcript_text: str,
    source_url: str,
    detected_language: str,
) -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = f"transcript-{video_id}-{timestamp}.txt"
    output_path = TRANSCRIPTIONS_DIR / file_name

    content = "\n".join(
        [
            f"Video ID: {video_id}",
            f"Source: {source_url}",
            f"Langue: {detected_language}",
            f"Genere le: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "",
            transcript_text,
        ]
    )
    output_path.write_text(content, encoding="utf-8")
    return file_name


@app.route("/", methods=["GET", "POST"])
def index():
    context = {
        "transcript_text": None,
        "transcript_stats": None,
        "error_message": None,
        "saved_file": None,
        "submitted_url": "",
        "detected_language": None,
        "recent_transcriptions": list_recent_transcriptions(),
    }

    if request.method == "POST":
        submitted_url = request.form.get("youtube_url", "").strip()
        context["submitted_url"] = submitted_url

        if not submitted_url:
            context["error_message"] = "Veuillez coller un lien YouTube ou un identifiant de video."
            return render_template("index.html", **context)

        video_id = extract_video_id(submitted_url)
        if not video_id:
            context["error_message"] = "Le lien fourni ne ressemble pas a une URL YouTube valide."
            return render_template("index.html", **context)

        try:
            transcript_text, detected_language = fetch_transcript_text(video_id)
            saved_file = save_transcript(video_id, transcript_text, submitted_url, detected_language)
            context.update(
                {
                    "transcript_text": transcript_text,
                    "transcript_stats": build_transcript_stats(video_id, transcript_text),
                    "saved_file": saved_file,
                    "detected_language": detected_language,
                    "recent_transcriptions": list_recent_transcriptions(),
                }
            )
        except NoTranscriptFound:
            context["error_message"] = (
                "Aucune transcription compatible n'a ete trouvee pour cette video. "
                "Essayez une autre video avec sous-titres disponibles."
            )
        except TranscriptsDisabled:
            context["error_message"] = "Les sous-titres sont desactives pour cette video."
        except CouldNotRetrieveTranscript as error:
            context["error_message"] = f"Impossible de recuperer la transcription: {error}"
        except Exception as error:
            context["error_message"] = f"Erreur inattendue: {error}"

    return render_template("index.html", **context)


@app.route("/downloads/<path:file_name>")
def download_transcript(file_name: str):
    return send_from_directory(TRANSCRIPTIONS_DIR, file_name, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)