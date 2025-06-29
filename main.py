#!/usr/bin/env python3
"""
English to Hindi Video Translator

This script converts English language videos to Hindi by:
1. Downloading YouTube videos (if URL provided) using yt-dlp
2. Extracting audio from the input video using FFmpeg
3. Transcribing the English audio using OpenAI Whisper
4. Translating the English text to Hindi using OpenAI
5. Converting the Hindi text to speech using OpenAI TTS
6. Replacing the original audio with the new Hindi audio using FFmpeg

Requirements:
- OpenAI API key (set as OPENAI_API_KEY environment variable or in .env file)
- FFmpeg installed on the system
- yt-dlp for YouTube video downloads
"""

import os
import sys
import argparse
import tempfile
import logging
import re
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

import ffmpeg
import yt_dlp
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
try:
    load_dotenv()
except Exception:
    # Ignore any errors loading .env file
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoTranslator:
    """Main class for translating English videos to Hindi."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the VideoTranslator with OpenAI client."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info("VideoTranslator initialized successfully")
    
    def is_youtube_url(self, url: str) -> bool:
        """Check if the input is a YouTube URL."""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
            r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+',  # YouTube Shorts
        ]
        
        return any(re.match(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)
    
    def download_youtube_video(self, url: str, output_dir: str = None) -> str:
        """Download YouTube video and return the path to downloaded file."""
        logger.info(f"Downloading YouTube video from: {url}")
        
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        # Configure yt-dlp options
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'format': 'best[ext=mp4]/best',  # Prefer mp4, fallback to best available
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info to get the final filename
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video')
                
                # Sanitize filename
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', video_title)
                
                # Update output template with sanitized title
                ydl_opts['outtmpl'] = os.path.join(output_dir, f'{safe_title}.%(ext)s')
                
                # Download the video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                    ydl_download.download([url])
                
                # Find the downloaded file
                expected_path = os.path.join(output_dir, f'{safe_title}.mp4')
                if os.path.exists(expected_path):
                    logger.info(f"YouTube video downloaded successfully: {expected_path}")
                    return expected_path
                
                # Fallback: search for recently downloaded files
                for file in os.listdir(output_dir):
                    if safe_title in file and file.endswith(('.mp4', '.mkv', '.webm')):
                        full_path = os.path.join(output_dir, file)
                        logger.info(f"YouTube video downloaded successfully: {full_path}")
                        return full_path
                
                raise FileNotFoundError("Downloaded file not found")
                
        except Exception as e:
            logger.error(f"Error downloading YouTube video: {str(e)}")
            raise
    
    def extract_audio(self, video_path: str, output_path: str) -> None:
        """Extract audio from video using FFmpeg."""
        logger.info(f"Extracting audio from {video_path}")
        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_path, acodec='libmp3lame', ar=16000, ac=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            logger.info(f"Audio extracted successfully to {output_path}")
        except ffmpeg.Error as e:
            logger.error(f"Error extracting audio: {e.stderr.decode()}")
            raise
    
    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio to text using OpenAI Whisper."""
        logger.info(f"Transcribing audio from {audio_path}")
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
            
            transcribed_text = transcript.text
            logger.info(f"Transcription completed. Length: {len(transcribed_text)} characters")
            return transcribed_text
        
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
    
    def translate_text(self, text: str, target_language: str = "Hindi") -> str:
        """Translate English text to Hindi using OpenAI."""
        logger.info(f"Translating text to {target_language}")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the following English text to {target_language}. "
                                 f"Maintain the original meaning, tone, and context. Return only the translated text without any additional comments."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content
            logger.info(f"Translation completed. Length: {len(translated_text)} characters")
            return translated_text
        
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            raise
    
    def text_to_speech(self, text: str, output_path: str, voice: str = "alloy") -> None:
        """Convert text to speech using OpenAI TTS."""
        logger.info(f"Converting text to speech using voice '{voice}'")
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3"
            )
            
            with open(output_path, 'wb') as audio_file:
                for chunk in response.iter_bytes():
                    audio_file.write(chunk)
            
            logger.info(f"Text-to-speech completed. Audio saved to {output_path}")
        
        except Exception as e:
            logger.error(f"Error converting text to speech: {str(e)}")
            raise
    
    def replace_audio(self, video_path: str, new_audio_path: str, output_path: str) -> None:
        """Replace video audio with new audio using FFmpeg."""
        logger.info(f"Replacing audio in {video_path} with {new_audio_path}")
        try:
            video_input = ffmpeg.input(video_path)
            audio_input = ffmpeg.input(new_audio_path)
            
            (
                ffmpeg
                .output(
                    video_input['v'], 
                    audio_input['a'], 
                    output_path,
                    vcodec='copy',
                    acodec='aac',
                    strict='experimental'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            logger.info(f"Audio replacement completed. Output saved to {output_path}")
        
        except ffmpeg.Error as e:
            logger.error(f"Error replacing audio: {e.stderr.decode()}")
            raise
    
    def translate_video(
        self, 
        input_source: str, 
        output_video: str, 
        target_language: str = "Hindi",
        voice: str = "alloy",
        keep_temp_files: bool = False,
        youtube_download_dir: str = None
    ) -> None:
        """Complete video translation pipeline supporting both local files and YouTube URLs."""
        logger.info(f"Starting video translation: {input_source} -> {output_video}")
        
        # Create temporary directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Handle YouTube URL or local file
            if self.is_youtube_url(input_source):
                logger.info("Detected YouTube URL, downloading video...")
                download_dir = youtube_download_dir or str(temp_path)
                input_video = self.download_youtube_video(input_source, download_dir)
            else:
                # Validate input file exists
                if not Path(input_source).exists():
                    raise FileNotFoundError(f"Input video file not found: {input_source}")
                input_video = input_source
            
            # Define temporary file paths
            extracted_audio = temp_path / "extracted_audio.mp3"
            hindi_audio = temp_path / "hindi_audio.mp3"
            
            try:
                # Step 1: Extract audio from video
                self.extract_audio(input_video, str(extracted_audio))
                
                # Step 2: Transcribe audio to English text
                english_text = self.transcribe_audio(str(extracted_audio))
                logger.info(f"Transcribed text preview: {english_text[:100]}...")
                
                # Step 3: Translate English text to target language
                translated_text = self.translate_text(english_text, target_language)
                logger.info(f"Translated text preview: {translated_text[:100]}...")
                
                # Step 4: Convert translated text to speech
                self.text_to_speech(translated_text, str(hindi_audio), voice)
                
                # Step 5: Replace original audio with translated audio
                self.replace_audio(input_video, str(hindi_audio), output_video)
                
                # Optionally keep temporary files for debugging
                if keep_temp_files:
                    import shutil
                    output_dir = Path(output_video).parent
                    shutil.copy2(extracted_audio, output_dir / "extracted_audio.mp3")
                    shutil.copy2(hindi_audio, output_dir / "hindi_audio.mp3")
                    
                    # Save text files
                    with open(output_dir / "english_transcript.txt", 'w', encoding='utf-8') as f:
                        f.write(english_text)
                    with open(output_dir / f"{target_language.lower()}_translation.txt", 'w', encoding='utf-8') as f:
                        f.write(translated_text)
                    
                    # Save downloaded video if it was from YouTube
                    if self.is_youtube_url(input_source) and youtube_download_dir is None:
                        original_video_name = f"original_{Path(output_video).stem}.mp4"
                        shutil.copy2(input_video, output_dir / original_video_name)
                        logger.info(f"Original YouTube video saved as: {original_video_name}")
                    
                    logger.info(f"Temporary files saved to {output_dir}")
                
                logger.info("Video translation completed successfully!")
                
            except Exception as e:
                logger.error(f"Error during video translation: {str(e)}")
                raise


def main():
    """Main function to run the video translator."""
    parser = argparse.ArgumentParser(
        description="Translate English videos to Hindi using OpenAI APIs and FFmpeg. "
                   "Supports both local video files and YouTube URLs."
    )
    parser.add_argument(
        "input_source",
        help="Path to the input English video file OR YouTube URL"
    )
    parser.add_argument(
        "output_video",
        help="Path to the output Hindi video file"
    )
    parser.add_argument(
        "--language",
        default="Hindi",
        help="Target language for translation (default: Hindi)"
    )
    parser.add_argument(
        "--voice",
        default="alloy",
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        help="Voice model for text-to-speech (default: alloy)"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary files for debugging"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (can also be set via OPENAI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--youtube-dir",
        help="Directory to save downloaded YouTube videos (default: temporary directory)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize translator
        translator = VideoTranslator(api_key=args.api_key)
        
        # Run translation
        translator.translate_video(
            input_source=args.input_source,
            output_video=args.output_video,
            target_language=args.language,
            voice=args.voice,
            keep_temp_files=args.keep_temp,
            youtube_download_dir=args.youtube_dir
        )
        
        print(f"✅ Translation completed! Output saved to: {args.output_video}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
