# English to Hindi Video Translator

A Python application that automatically translates English videos to Hindi using OpenAI's APIs (Whisper, GPT-4, and TTS) combined with FFmpeg for video processing. Supports both local video files and YouTube URLs.

## 🎯 Features

- **Modern GUI Interface**: Intuitive PyQt6-based graphical user interface with drag-and-drop support
- **Command-Line Interface**: Full-featured CLI for automation and scripting
- **YouTube Video Support**: Download and translate videos directly from YouTube URLs in high quality (up to 1080p)
- **Automatic Filename Generation**: Smart output filenames based on original video title with language suffix
- **Automatic Audio Extraction**: Extracts audio from video files using FFmpeg
- **Speech-to-Text**: Transcribes English audio using OpenAI Whisper
- **Text Translation**: Translates English text to Hindi using GPT-4
- **Text-to-Speech**: Converts Hindi text to natural-sounding speech using OpenAI TTS
- **Audio Duration Matching**: Automatically adjusts translated audio to match original video length
- **Background Music Preservation**: Option to mix translated speech with original background music
- **Video Processing**: Replaces original audio with synchronized translated audio while preserving video quality
- **Multiple Voice Options**: Choose from 6 different voice models
- **Multi-language Support**: Translate to any language supported by OpenAI
- **Real-time Progress Tracking**: Live progress updates and logging
- **Organized Output**: Saves videos to organized output directory with debug subdirectories

## 🏗️ Architecture

```
Input Source (Video File or YouTube URL)
    ↓
1. YouTube Download (if URL) - yt-dlp
    ↓
2. Duration Analysis (FFmpeg)
    ↓
3. Audio Extraction (FFmpeg)
    ↓
4. Speech-to-Text (Whisper)
    ↓
5. Text Translation (GPT-4)
    ↓
6. Text-to-Speech (OpenAI TTS)
    ↓
7. Audio Duration Matching (FFmpeg)
    ↓
8. Audio Replacement (FFmpeg)
    ↓
Output Video (Hindi - Synchronized)
```

## 📋 Requirements

### System Requirements
- Python 3.11 or higher
- FFmpeg installed and accessible from command line
- OpenAI API key
- Internet connection (for YouTube downloads and OpenAI APIs)

### Python Dependencies
- `openai>=1.93.0` - OpenAI API client
- `ffmpeg-python>=0.2.0` - Python wrapper for FFmpeg
- `yt-dlp>=2025.6.25` - YouTube video downloader
- `python-dotenv>=1.1.1` - Environment file loader
- `PyQt6>=6.4.0` - GUI framework (for graphical interface)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd en-to-hin-brainrot
```

### 2. Install FFmpeg

#### Windows
1. Download FFmpeg from [official website](https://ffmpeg.org/download.html)
2. Extract and add to PATH environment variable
3. Verify installation: `ffmpeg -version`

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Install Python Dependencies

This project uses `uv` for dependency management:

```bash
# Install uv if not already installed
pip install uv

# Install dependencies
uv sync
```

Alternatively, using pip:
```bash
pip install openai ffmpeg-python yt-dlp python-dotenv PyQt6
```

**Note**: The GUI application requires PyQt6. If you only plan to use the command-line interface, you can skip PyQt6 installation.

### 4. Set Up OpenAI API Key

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set it as an environment variable:

#### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

#### macOS/Linux
```bash
export OPENAI_API_KEY="your_api_key_here"
```

#### Using .env File (Recommended)
Create a `.env` file in the project root (this method works on all platforms):
```bash
# Copy the template and edit it
cp env.template .env
# Edit .env file with your actual API key
```

The `.env` file should contain:
```
OPENAI_API_KEY=your_api_key_here
```

## 🎬 Usage

### GUI Application (Recommended)

For the easiest experience, use the modern graphical interface:

```bash
# Launch the GUI application
uv run python run_gui.py

# Or use the script entry point (after installation)
video-translator-gui
```

**GUI Features:**
- **Drag & Drop**: Simply drag video files into the application
- **YouTube Support**: Paste YouTube URLs directly into the input field
- **Visual Progress**: Real-time progress tracking with detailed logs
- **Audio Mixing Controls**: Interactive sliders for background music and speech volume
- **Settings Persistence**: Automatically saves your preferences
- **File Browser**: Easy file selection for input and output
- **Error Handling**: User-friendly error messages and recovery options

### Command Line Interface

For automation and scripting, use the command-line interface:

### YouTube Video Translation
```bash
# Translate a YouTube video (filename auto-generated)
uv run python main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# With custom voice and keep debug files
uv run python main.py "https://youtu.be/VIDEO_ID" --voice nova --keep-temp

# With custom output filename
uv run python main.py "https://youtu.be/VIDEO_ID" custom_output.mp4
```

### Local Video Translation
```bash
# Basic local file translation (filename auto-generated)
uv run python main.py input_video.mp4

# With custom output filename
uv run python main.py input_video.mp4 custom_output.mp4
```

### Advanced Usage
```bash
# Specify target language and voice (auto-generated filename)
uv run python main.py input_video.mp4 --language "Spanish" --voice "nova"

# Keep original background music while adding translated speech
uv run python main.py input_video.mp4 --mix-background --background-volume 0.3 --speech-volume 1.0

# YouTube video with background music preservation
uv run python main.py "https://youtu.be/ID" --mix-background --background-volume 0.25 --speech-volume 1.2

# Keep debug files for troubleshooting
uv run python main.py input_video.mp4 --keep-temp

# Save YouTube videos to specific directory with high quality
uv run python main.py "https://youtube.com/watch?v=ID" --youtube-dir ./downloads

# Use different API key
uv run python main.py input_video.mp4 --api-key "your_api_key"

# Custom output with specific directory
uv run python main.py "https://youtu.be/ID" ./my_videos/custom_name.mp4
```

### YouTube URL Formats Supported
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID` (YouTube Shorts)

### Available Voice Options
- `alloy` (default) - Neutral voice
- `echo` - Clear and expressive
- `fable` - British accent
- `onyx` - Deep, authoritative
- `nova` - Young, energetic
- `shimmer` - Soft and warm

### Audio Mixing Feature
The `--mix-background` option allows you to preserve the original background music while adding translated speech:

```bash
# Basic audio mixing - keeps background music at 30% volume
uv run python main.py input_video.mp4 --mix-background

# Custom volume levels - quieter background, louder speech
uv run python main.py input_video.mp4 --mix-background --background-volume 0.2 --speech-volume 1.2

# Balanced mix for music videos
uv run python main.py music_video.mp4 --mix-background --background-volume 0.4 --speech-volume 0.9
```

**Volume Guidelines:**
- **Background Volume**: 0.1-0.5 (10%-50%) works best for most content
- **Speech Volume**: 0.8-1.2 (80%-120%) ensures clear dialogue
- **Music Videos**: Use higher background volume (0.4-0.6) to preserve musical experience
- **Educational Content**: Use lower background volume (0.1-0.3) to prioritize speech clarity

### Command Line Arguments
```
positional arguments:
  input_source          Path to the input English video file OR YouTube URL
  output_video          Path to the output video file (optional - auto-generated if not provided)

optional arguments:
  -h, --help            Show help message and exit
  --language LANGUAGE   Target language for translation (default: Hindi)
  --voice {alloy,echo,fable,onyx,nova,shimmer}
                        Voice model for text-to-speech (default: alloy)
  --keep-temp           Keep debug files for troubleshooting
  --api-key API_KEY     OpenAI API key (can also be set via OPENAI_API_KEY environment variable)
  --youtube-dir YOUTUBE_DIR
                        Directory to save downloaded YouTube videos (default: temporary directory)
  --mix-background      Mix translated speech with original background music instead of replacing audio completely
  --background-volume BACKGROUND_VOLUME
                        Volume level for background music when mixing (0.0 to 1.0, default: 0.3)
  --speech-volume SPEECH_VOLUME
                        Volume level for translated speech when mixing (0.0 to 1.0, default: 1.0)
```

## 📁 Project Structure

```
en-to-hin-brainrot/
├── main.py                  # Main CLI application script
├── video_translator_gui.py  # Modern PyQt6 GUI application
├── run_gui.py              # GUI launcher script
├── pyproject.toml          # Project configuration and dependencies
├── uv.lock                 # Lock file for exact dependency versions
├── README.md               # This file
├── env.template            # Environment variables template
├── .gitignore              # Git ignore rules
├── .venv/                  # Virtual environment (created by uv)
├── downloads/              # Downloaded YouTube videos (if --youtube-dir used)
├── output/                 # Generated translated videos
├── check_requirements.py  # System requirements checker
├── example_usage.py        # Usage examples including YouTube
└── project_summary.py     # Project overview and verification
```

## 🔧 Development

### Running in Development Mode
```bash
# Run the script directly
uv run python main.py input.mp4 output.mp4

# Test with YouTube URL
uv run python main.py "https://youtu.be/dQw4w9WgXcQ" output.mp4
```

### Adding Dependencies
```bash
uv add package_name
```

### Code Quality
The project uses standard Python practices:
- Type hints for better code documentation
- Comprehensive error handling
- Structured logging for debugging
- Modular class-based architecture

## 📊 API Usage and Costs

This application uses three OpenAI APIs:

1. **Whisper API** (Transcription): $0.006 per minute
2. **GPT-4 API** (Translation): ~$0.03 per 1K tokens
3. **TTS API** (Text-to-Speech): $0.015 per 1K characters

### Estimated Costs
- 1-minute video: ~$0.10-0.50
- 5-minute video: ~$0.50-2.50
- 10-minute video: ~$1.00-5.00

*Costs may vary based on video content, speech density, and text length.*

### YouTube Download Considerations
- Downloaded videos are temporary by default (use `--youtube-dir` to keep them)
- Video quality depends on availability (prefers MP4 format)
- Large videos may take longer to download and process

## 🚨 Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in PATH
   - Test with: `ffmpeg -version`

2. **OpenAI API errors**
   - Verify API key is correct and has sufficient credits
   - Check rate limits and quotas

3. **YouTube download fails**
   - Check if the video is public and accessible
   - Verify internet connection
   - Some videos may have regional restrictions

4. **Audio extraction fails**
   - Ensure input video file is valid
   - Check video codec compatibility

5. **Memory issues with large files**
   - Consider processing shorter video segments
   - Ensure sufficient disk space for temporary files

### Debug Mode
Use the `--keep-temp` flag to save intermediate files:
- `extracted_audio.mp3` - Original audio
- `hindi_audio.mp3` - Translated audio
- `english_transcript.txt` - Transcribed text
- `hindi_translation.txt` - Translated text
- `original_[name].mp4` - Downloaded YouTube video (if applicable)

## 🎯 Usage Examples

### GUI Examples

**Basic Usage:**
1. Launch the GUI: `uv run python run_gui.py`
2. Drag and drop a video file or paste a YouTube URL
3. Select your target language and voice
4. Click "🚀 Start Translation"
5. Monitor progress in real-time
6. Play or open the translated video when complete

**Audio Mixing:**
1. Enable "Mix with original background music"
2. Adjust background volume (10-50% recommended)
3. Adjust speech volume (80-120% recommended)
4. Perfect for music videos and content with important background audio

**YouTube URLs:**
- Simply paste any YouTube URL into the input field
- The GUI automatically detects and handles YouTube links
- Download progress is shown in the progress bar

### Command Line Examples

### YouTube Examples
```bash
# Educational video translation
uv run python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" educational_hindi.mp4

# YouTube Shorts translation
uv run python main.py "https://www.youtube.com/shorts/VIDEO_ID" shorts_hindi.mp4 --youtube-dir ./downloads

# News video with different voice
uv run python main.py "https://youtu.be/VIDEO_ID" news_hindi.mp4 --voice onyx

# Tutorial video to Spanish
uv run python main.py "https://youtube.com/watch?v=ID" tutorial_spanish.mp4 --language Spanish
```

### Batch Processing
```bash
# Process multiple YouTube videos
for url in "https://youtu.be/ID1" "https://youtu.be/ID2"; do
    uv run python main.py "$url" "hindi_$(basename $url).mp4"
done
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

- This tool is for educational and personal use
- Respect copyright laws when processing videos
- Ensure you have rights to download and modify YouTube content
- OpenAI API usage is subject to their terms of service
- Quality of translation depends on source audio clarity and content complexity
- YouTube downloads are subject to platform terms of service

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on GitHub with:
   - Input source (video file path or YouTube URL)
   - Error messages
   - System information (OS, Python version)
   - Video duration and format details
