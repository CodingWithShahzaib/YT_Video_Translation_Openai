from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
from pathlib import Path
import sys
sys.path.append('..')
from main import VideoTranslator
import os
from dotenv import load_dotenv

load_dotenv()

import shutil

app = FastAPI()

LATEST_OUTPUT_PATH = None
LATEST_TITLE = None
LATEST_DESCRIPTION = None

@app.get('/translate-latest')
def translate_latest():
    global LATEST_OUTPUT_PATH, LATEST_TITLE, LATEST_DESCRIPTION
    # Get latest short URL
    channel_url = 'https://www.youtube.com/@zackdfilms/shorts'
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlist_items': '1',  # Get first (latest) item
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        latest_video = info['entries'][0]
        video_url = latest_video['url']
        title = latest_video.get('title', 'Translated Video')
        description = latest_video.get('description', '')
    
    # Translate
    translator = VideoTranslator(api_key=os.getenv('OPENAI_API_KEY'))
    output_path = translator.translate_video(
        input_source=video_url,
        target_language='Hindi',
        voice='shimmer',
        tts_provider='openai'
    )
    LATEST_OUTPUT_PATH = output_path
    LATEST_TITLE = title
    LATEST_DESCRIPTION = description
    # Return JSON with download URL, title, and description
    return JSONResponse({
        'download_url': '/download',
        'title': title,
        'description': description
    })


@app.get('/download')
def download():
    global LATEST_OUTPUT_PATH
    if not LATEST_OUTPUT_PATH or not os.path.exists(LATEST_OUTPUT_PATH):
        return JSONResponse({'error': 'No video available. Please call /translate-latest first.'}, status_code=404)
    return FileResponse(
        LATEST_OUTPUT_PATH,
        media_type='video/mp4',
        filename=f'{LATEST_TITLE}.mp4'
    )

@app.get('/clean-output')
def clean_output():
    output_dir = Path('../output').resolve() if not Path('output').is_dir() else Path('output').resolve()
    if not output_dir.exists() or not output_dir.is_dir():
        return JSONResponse({'error': 'Output directory does not exist.'}, status_code=404)
    deleted_files = 0
    for file in output_dir.iterdir():
        try:
            if file.is_file() or file.is_symlink():
                file.unlink()
                deleted_files += 1
            elif file.is_dir():
                shutil.rmtree(file)
                deleted_files += 1
        except Exception as e:
            continue
    return JSONResponse({'status': 'success', 'deleted_files': deleted_files})
