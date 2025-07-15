#!/usr/bin/env python3
"""
English to Hindi Video Translator

This script converts English language videos to Hindi by:
1. Downloading YouTube videos (if URL provided) using yt-dlp
2. Getting original video duration for synchronization
3. Extracting audio from the input video using FFmpeg
4. Transcribing the English audio using OpenAI Whisper
5. Translating the English text to Hindi using OpenAI
6. Converting the Hindi text to speech using OpenAI TTS
7. Adjusting audio duration to match original video length
8. Replacing the original audio with the duration-matched Hindi audio using FFmpeg

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
from elevenlabs.client import ElevenLabs

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
    
    def __init__(self, api_key: Optional[str] = None, elevenlabs_api_key: Optional[str] = None):
        """Initialize the VideoTranslator with OpenAI client."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.elevenlabs_api_key = elevenlabs_api_key or os.getenv('ELEVENLABS_API_KEY')
        if self.elevenlabs_api_key:
            self.eleven_client = ElevenLabs(api_key=self.elevenlabs_api_key)
        else:
            self.eleven_client = None
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
    
    def get_youtube_video_info(self, url: str) -> dict:
        """Get YouTube video information without downloading."""
        logger.info(f"Getting video information from: {url}")
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'video'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'video_id': info.get('id', 'unknown')
                }
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {
                'title': 'video',
                'duration': 0,
                'uploader': 'Unknown',
                'video_id': 'unknown'
            }
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove emojis and other unicode characters that might cause issues
        filename = filename.encode('ascii', 'ignore').decode('ascii')
        
        # Limit length and remove extra spaces
        filename = filename.strip()[:100]  # Limit to 100 characters
        filename = ' '.join(filename.split())  # Remove extra whitespace
        
        return filename
    
    def _cleanup_temp_files(self, file_paths: list) -> None:
        """Clean up temporary files and directories."""
        if not file_paths:
            return
            
        cleaned_count = 0
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        logger.info(f"Cleaned up temporary file: {file_path} ({file_size / (1024*1024):.2f} MB)")
                        cleaned_count += 1
                    elif os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                        logger.info(f"Cleaned up temporary directory: {file_path}")
                        cleaned_count += 1
            except Exception as e:
                logger.warning(f"Could not clean up {file_path}: {str(e)}")
        
        if cleaned_count > 0:
            logger.info(f"Successfully cleaned up {cleaned_count} temporary file(s)")
    
    def download_youtube_video(self, url: str, output_dir: str = None) -> tuple[str, dict]:
        """Download YouTube video and return the path to downloaded file and video info."""
        logger.info(f"Downloading YouTube video from: {url}")
        
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        try:
            # First get video info
            video_info = self.get_youtube_video_info(url)
            video_title = video_info['title']
            safe_title = self.sanitize_filename(video_title)
            
            # Configure yt-dlp options for high quality
            ydl_opts = {
                'outtmpl': os.path.join(output_dir, f'{safe_title}.%(ext)s'),
                'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'merge_output_format': 'mp4',  # Ensure output is always mp4
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Download the video
                ydl.download([url])
                
                # Find the downloaded file
                expected_path = os.path.join(output_dir, f'{safe_title}.mp4')
                if os.path.exists(expected_path):
                    logger.info(f"YouTube video downloaded successfully: {expected_path}")
                    return expected_path, video_info
                
                # Fallback: search for recently downloaded files
                for file in os.listdir(output_dir):
                    if safe_title in file and file.endswith(('.mp4', '.mkv', '.webm')):
                        full_path = os.path.join(output_dir, file)
                        logger.info(f"YouTube video downloaded successfully: {full_path}")
                        return full_path, video_info
                
                raise FileNotFoundError("Downloaded file not found")
                
        except Exception as e:
            logger.error(f"Error downloading YouTube video: {str(e)}")
            raise
    
    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds using FFmpeg."""
        logger.info(f"Getting duration of {video_path}")
        try:
            probe = ffmpeg.probe(video_path)
            duration = float(probe['streams'][0]['duration'])
            logger.info(f"Video duration: {duration:.2f} seconds")
            return duration
        except Exception as e:
            logger.error(f"Error getting video duration: {str(e)}")
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
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds using FFmpeg."""
        try:
            probe = ffmpeg.probe(audio_path)
            duration = float(probe['streams'][0]['duration'])
            logger.info(f"Audio duration: {duration:.2f} seconds")
            return duration
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            raise

    def adjust_audio_duration(self, input_audio_path: str, output_audio_path: str, target_duration: float) -> None:
        """Adjust audio duration to match target duration using FFmpeg time-stretching."""
        logger.info(f"Adjusting audio duration to {target_duration:.2f} seconds")
        
        try:
            # Get current audio duration
            current_duration = self.get_audio_duration(input_audio_path)
            
            # Calculate speed adjustment factor
            speed_factor = current_duration / target_duration
            
            logger.info(f"Current duration: {current_duration:.2f}s, Target: {target_duration:.2f}s, Speed factor: {speed_factor:.3f}")
            
            # Apply speed adjustment with quality preservation
            if abs(speed_factor - 1.0) < 0.05:  # Less than 5% difference, no adjustment needed
                logger.info("Duration difference is minimal, no adjustment needed")
                # Just copy the file
                (
                    ffmpeg
                    .input(input_audio_path)
                    .output(output_audio_path, acodec='copy')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
            elif 0.5 <= speed_factor <= 2.0:  # Within reasonable speed adjustment range
                # Use atempo filter for speed adjustment (preserves pitch)
                (
                    ffmpeg
                    .input(input_audio_path)
                    .filter('atempo', speed_factor)
                    .output(output_audio_path, acodec='libmp3lame')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
            else:  # Extreme speed difference, use multiple atempo filters or padding/trimming
                if speed_factor > 2.0:  # Need to speed up significantly
                    logger.info("Large speed increase needed, using multiple atempo filters")
                    # Chain multiple atempo filters (each can only do 0.5-2.0x)
                    factor1 = min(speed_factor, 2.0)
                    remaining_factor = speed_factor / factor1
                    
                    if remaining_factor > 1.0:
                        factor2 = min(remaining_factor, 2.0)
                        (
                            ffmpeg
                            .input(input_audio_path)
                            .filter('atempo', factor1)
                            .filter('atempo', factor2)
                            .output(output_audio_path, acodec='libmp3lame')
                            .overwrite_output()
                            .run(capture_stdout=True, capture_stderr=True)
                        )
                    else:
                        (
                            ffmpeg
                            .input(input_audio_path)
                            .filter('atempo', factor1)
                            .output(output_audio_path, acodec='libmp3lame')
                            .overwrite_output()
                            .run(capture_stdout=True, capture_stderr=True)
                        )
                else:  # Need to slow down significantly (speed_factor < 0.5)
                    logger.info("Large speed decrease needed, using multiple atempo filters")
                    factor1 = max(speed_factor, 0.5)
                    remaining_factor = speed_factor / factor1
                    
                    if remaining_factor < 1.0:
                        factor2 = max(remaining_factor, 0.5)
                        (
                            ffmpeg
                            .input(input_audio_path)
                            .filter('atempo', factor1)
                            .filter('atempo', factor2)
                            .output(output_audio_path, acodec='libmp3lame')
                            .overwrite_output()
                            .run(capture_stdout=True, capture_stderr=True)
                        )
                    else:
                        (
                            ffmpeg
                            .input(input_audio_path)
                            .filter('atempo', factor1)
                            .output(output_audio_path, acodec='libmp3lame')
                            .overwrite_output()
                            .run(capture_stdout=True, capture_stderr=True)
                        )
            
            # Verify the final duration
            final_duration = self.get_audio_duration(output_audio_path)
            logger.info(f"Audio duration adjusted to {final_duration:.2f} seconds (target: {target_duration:.2f}s)")
            
        except ffmpeg.Error as e:
            logger.error(f"Error adjusting audio duration: {e.stderr.decode()}")
            raise
        except Exception as e:
            logger.error(f"Error adjusting audio duration: {str(e)}")
            raise

    def text_to_speech(self, text: str, output_path: str, voice: str = "alloy", tts_provider: str = "openai") -> None:
        """Convert text to speech using selected TTS provider."""
        logger.info(f"Converting text to speech using {tts_provider} with voice '{voice}'")
        try:
            if tts_provider.lower() == "openai":
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text,
                    response_format="mp3"
                )
                
                with open(output_path, 'wb') as audio_file:
                    for chunk in response.iter_bytes():
                        audio_file.write(chunk)
            
            elif tts_provider.lower() == "elevenlabs":
                if not self.eleven_client:
                    raise ValueError("ElevenLabs client not initialized. API key required.")
                
                # No mapping needed; use voice directly
                audio = self.eleven_client.generate(
                    text=text,
                    voice=voice,
                    model="eleven_multilingual_v2"
                )
                
                with open(output_path, 'wb') as audio_file:
                    audio_file.write(audio)
            else:
                raise ValueError(f"Unsupported TTS provider: {tts_provider}")
            
            logger.info(f"Text-to-speech completed. Audio saved to {output_path}")
        
        except Exception as e:
            logger.error(f"Error converting text to speech: {str(e)}")
            raise
    
    def mix_audio_with_background(self, video_path: str, new_speech_path: str, output_path: str, 
                                 background_volume: float = 0.3, speech_volume: float = 1.0) -> None:
        """Mix new speech audio with original background music from video."""
        logger.info(f"Mixing speech audio with background music from {video_path}")
        try:
            video_input = ffmpeg.input(video_path)
            speech_input = ffmpeg.input(new_speech_path)
            
            # Extract original audio and reduce its volume (for background music)
            background_audio = video_input['a'].filter('volume', background_volume)
            
            # Adjust speech volume if needed
            if speech_volume != 1.0:
                speech_audio = speech_input['a'].filter('volume', speech_volume)
            else:
                speech_audio = speech_input['a']
            
            # Mix the background music with the new speech
            mixed_audio = ffmpeg.filter([background_audio, speech_audio], 'amix', inputs=2, duration='longest')
            
            # Combine video with mixed audio
            (
                ffmpeg
                .output(
                    video_input['v'], 
                    mixed_audio, 
                    output_path,
                    vcodec='copy',
                    acodec='aac',
                    strict='experimental'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            logger.info(f"Audio mixing completed. Output saved to {output_path}")
        
        except ffmpeg.Error as e:
            logger.error(f"Error mixing audio: {e.stderr.decode()}")
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
    
    def generate_output_filename(self, input_source: str, target_language: str, video_info: dict = None) -> str:
        """Generate output filename based on input source and target language."""
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        if self.is_youtube_url(input_source):
            if video_info:
                base_name = self.sanitize_filename(video_info['title'])
            else:
                base_name = "youtube_video"
        else:
            # For local files, use the filename without extension
            base_name = Path(input_source).stem
        
        # Add language suffix
        language_suffix = target_language.lower()
        output_filename = f"{base_name}_{language_suffix}.mp4"
        
        return str(output_dir / output_filename)
    
    def translate_video(
        self, 
        input_source: str, 
        output_video: str = None, 
        target_language: str = "Hindi",
        voice: str = "alloy",
        keep_temp_files: bool = False,
        youtube_download_dir: str = None,
        mix_with_background: bool = False,
        background_volume: float = 0.3,
        speech_volume: float = 1.0,
        tts_provider: str = "openai",
        elevenlabs_api_key: Optional[str] = None
    ) -> str:
        """Complete video translation pipeline supporting both local files and YouTube URLs.
        
        Args:
            input_source: Path to video file or YouTube URL
            output_video: Path for output video (auto-generated if None)
            target_language: Language to translate to (default: Hindi)
            voice: OpenAI TTS voice model (default: alloy)
            keep_temp_files: Keep intermediate files for debugging (default: False)
            youtube_download_dir: Directory to save downloaded YouTube videos (default: temp)
            mix_with_background: Mix speech with original background music instead of replacing (default: False)
            background_volume: Volume level for background music when mixing (0.0-1.0, default: 0.3)
            speech_volume: Volume level for translated speech when mixing (0.0-1.0, default: 1.0)
        """
        logger.info(f"Starting video translation: {input_source}")
        
        # Keep track of temporary files to clean up (for non-temp directory downloads)
        temp_files_to_cleanup = []
        
        # Create temporary directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            video_info = None
            
            # Handle YouTube URL or local file
            if self.is_youtube_url(input_source):
                logger.info("Detected YouTube URL, downloading video...")
                download_dir = youtube_download_dir or str(temp_path)
                input_video, video_info = self.download_youtube_video(input_source, download_dir)
                
                # If we downloaded outside of temp directory, mark for cleanup
                if youtube_download_dir is not None:
                    temp_files_to_cleanup.append(input_video)
            else:
                # Validate input file exists
                if not Path(input_source).exists():
                    raise FileNotFoundError(f"Input video file not found: {input_source}")
                input_video = input_source
            
            # Generate output filename if not provided
            if output_video is None:
                output_video = self.generate_output_filename(input_source, target_language, video_info)
            
            logger.info(f"Output will be saved to: {output_video}")
            
            # Ensure output directory exists
            Path(output_video).parent.mkdir(parents=True, exist_ok=True)
            
            # Define temporary file paths
            extracted_audio = temp_path / "extracted_audio.mp3"
            hindi_audio = temp_path / "hindi_audio.mp3"
            adjusted_hindi_audio = temp_path / "adjusted_hindi_audio.mp3"
            
            try:
                # Step 1: Get original video duration for audio synchronization
                original_duration = self.get_video_duration(input_video)
                
                # Step 2: Extract audio from video
                self.extract_audio(input_video, str(extracted_audio))
                
                # Step 3: Transcribe audio to English text
                english_text = self.transcribe_audio(str(extracted_audio))
                logger.info(f"Transcribed text preview: {english_text[:100]}...")
                
                # Step 4: Translate English text to target language
                translated_text = self.translate_text(english_text, target_language)
                logger.info(f"Translated text preview: {translated_text[:100]}...")
                
                # Step 5: Convert translated text to speech
                self.text_to_speech(translated_text, str(hindi_audio), voice, tts_provider)
                
                # Step 6: Adjust audio duration to match original video
                logger.info("Adjusting audio duration to match original video...")
                self.adjust_audio_duration(str(hindi_audio), str(adjusted_hindi_audio), original_duration)
                
                # Step 7: Replace or mix original audio with duration-matched translated audio
                if mix_with_background:
                    logger.info("Mixing translated audio with original background music...")
                    self.mix_audio_with_background(input_video, str(adjusted_hindi_audio), output_video, 
                                                 background_volume, speech_volume)
                else:
                    self.replace_audio(input_video, str(adjusted_hindi_audio), output_video)
                
                # Optionally keep temporary files for debugging
                if keep_temp_files:
                    import shutil
                    output_dir = Path(output_video).parent
                    base_name = Path(output_video).stem
                    
                    # Create debug subdirectory
                    debug_dir = output_dir / f"{base_name}_debug"
                    debug_dir.mkdir(exist_ok=True)
                    
                    # Save audio files
                    shutil.copy2(extracted_audio, debug_dir / "extracted_audio.mp3")
                    shutil.copy2(hindi_audio, debug_dir / f"{target_language.lower()}_audio_original.mp3")
                    shutil.copy2(adjusted_hindi_audio, debug_dir / f"{target_language.lower()}_audio_adjusted.mp3")
                    
                    # Save text files
                    with open(debug_dir / "english_transcript.txt", 'w', encoding='utf-8') as f:
                        f.write(english_text)
                    with open(debug_dir / f"{target_language.lower()}_translation.txt", 'w', encoding='utf-8') as f:
                        f.write(translated_text)
                    
                    # Save video information
                    with open(debug_dir / "video_info.txt", 'w', encoding='utf-8') as f:
                        f.write(f"Input source: {input_source}\n")
                        f.write(f"Output video: {output_video}\n")
                        f.write(f"Target language: {target_language}\n")
                        f.write(f"Voice: {voice}\n")
                        f.write(f"Original video duration: {original_duration:.2f} seconds\n")
                        
                        if video_info:
                            f.write(f"\\nYouTube Video Info:\\n")
                            f.write(f"Title: {video_info.get('title', 'N/A')}\\n")
                            f.write(f"Uploader: {video_info.get('uploader', 'N/A')}\\n")
                            f.write(f"Video ID: {video_info.get('video_id', 'N/A')}\\n")
                        
                        try:
                            original_tts_duration = self.get_audio_duration(str(hindi_audio))
                            adjusted_tts_duration = self.get_audio_duration(str(adjusted_hindi_audio))
                            f.write(f"\\nAudio Duration Info:\\n")
                            f.write(f"Original TTS duration: {original_tts_duration:.2f} seconds\\n")
                            f.write(f"Adjusted TTS duration: {adjusted_tts_duration:.2f} seconds\\n")
                            f.write(f"Speed adjustment factor: {original_tts_duration/original_duration:.3f}\\n")
                        except Exception:
                            f.write("\\nCould not retrieve audio durations\\n")
                    
                    # Save downloaded video if it was from YouTube
                    if self.is_youtube_url(input_source) and youtube_download_dir is None:
                        original_video_name = f"original_{base_name}.mp4"
                        shutil.copy2(input_video, debug_dir / original_video_name)
                        logger.info(f"Original YouTube video saved as: {original_video_name}")
                    
                    logger.info(f"Debug files saved to {debug_dir}")
                
                logger.info("Video translation completed successfully!")
                
                return output_video
                
            except Exception as e:
                logger.error(f"Error during video translation: {str(e)}")
                raise
            finally:
                # Clean up the temporary directory (happens automatically)
                # and any additional files we might have downloaded outside temp dir
                if temp_files_to_cleanup:
                    logger.info("Cleaning up additional temporary files...")
                    self._cleanup_temp_files(temp_files_to_cleanup)


def main():
    """Main function to run the video translator."""
    parser = argparse.ArgumentParser(
        description="Translate English videos to Hindi using OpenAI APIs and FFmpeg. "
                   "Supports both local video files and YouTube URLs. "
                   "Automatically generates output filenames based on original video name with language suffix."
    )
    parser.add_argument(
        "input_source",
        help="Path to the input English video file OR YouTube URL"
    )
    parser.add_argument(
        "output_video",
        nargs="?",
        default=None,
        help="Path to the output video file (optional - auto-generated if not provided)"
    )
    parser.add_argument(
        "--language",
        default="Hindi",
        help="Target language for translation (default: Hindi)"
    )
    parser.add_argument(
        "--voice",
        default="shimmer",
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
    parser.add_argument(
        "--mix-background",
        action="store_true",
        help="Mix translated speech with original background music instead of replacing audio completely"
    )
    parser.add_argument(
        "--background-volume",
        type=float,
        default=0.3,
        help="Volume level for background music when mixing (0.0 to 1.0, default: 0.3)"
    )
    parser.add_argument(
        "--speech-volume",
        type=float,
        default=1.0,
        help="Volume level for translated speech when mixing (0.0 to 1.0, default: 1.0)"
    )
    parser.add_argument(
        "--tts-provider",
        default="openai",
        choices=["openai", "elevenlabs"],
        help="TTS provider to use (default: openai)"
    )
    parser.add_argument(
        "--elevenlabs-api-key",
        help="ElevenLabs API key (required if using ElevenLabs TTS)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize translator
        translator = VideoTranslator(api_key=args.api_key)
        
        # Run translation
        output_path = translator.translate_video(
            input_source=args.input_source,
            output_video=args.output_video,
            target_language=args.language,
            voice=args.voice,
            keep_temp_files=args.keep_temp,
            youtube_download_dir=args.youtube_dir,
            mix_with_background=args.mix_background,
            background_volume=args.background_volume,
            speech_volume=args.speech_volume,
            tts_provider=args.tts_provider,
            elevenlabs_api_key=args.elevenlabs_api_key
        )
        
        print(f"✅ Translation completed!")
        print(f"📁 Output saved to: {output_path}")
        
        # Show additional info if auto-generated filename was used
        if args.output_video is None:
            print(f"💡 Filename was automatically generated based on original video title")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
