#!/usr/bin/env python3
"""
Project Summary and Quick Setup Verification

This script provides an overview of the Video Translator project and
performs basic verification checks.
"""

import sys
from pathlib import Path


def display_project_info():
    """Display project information and structure."""
    print("🎬 English to Hindi Video Translator")
    print("=" * 60)
    print("A Python application that automatically translates English videos")
    print("to Hindi using OpenAI's APIs and FFmpeg.")
    print()
    
    print("🏗️ Architecture:")
    print("1. Download YouTube videos (if URL provided) - yt-dlp")
    print("2. Extract audio from video (FFmpeg)")
    print("3. Transcribe English audio (OpenAI Whisper)")
    print("4. Translate to Hindi (OpenAI GPT-4)")
    print("5. Generate Hindi speech (OpenAI TTS)")
    print("6. Replace original audio (FFmpeg)")
    print()
    
    print("🎯 Key Features:")
    print("✅ Support for local video files")
    print("✅ YouTube video download and translation")
    print("✅ Multi-language translation (not just Hindi)")
    print("✅ 6 different voice options")
    print("✅ Debug mode with intermediate files")
    print("✅ Batch processing capabilities")
    print("✅ Custom YouTube download directories")
    print()


def display_supported_formats():
    """Display supported input and output formats."""
    print("📁 Supported Input Sources:")
    print("=" * 40)
    
    print("📺 YouTube URLs:")
    print("  • https://www.youtube.com/watch?v=VIDEO_ID")
    print("  • https://youtu.be/VIDEO_ID")
    print("  • https://www.youtube.com/embed/VIDEO_ID")
    print("  • https://m.youtube.com/watch?v=VIDEO_ID")
    print("  • https://www.youtube.com/shorts/VIDEO_ID (YouTube Shorts)")
    print()
    
    print("🎥 Local Video Files:")
    print("  • MP4 (.mp4)")
    print("  • AVI (.avi)")
    print("  • MOV (.mov)")
    print("  • MKV (.mkv)")
    print("  • Any format supported by FFmpeg")
    print()
    
    print("🎙️ Voice Options:")
    print("  • alloy (default) - Neutral voice")
    print("  • echo - Clear and expressive")
    print("  • fable - British accent") 
    print("  • onyx - Deep, authoritative")
    print("  • nova - Young, energetic")
    print("  • shimmer - Soft and warm")
    print()
    
    print("🌍 Target Languages:")
    print("  • Hindi (default)")
    print("  • Spanish, French, German")
    print("  • Japanese, Chinese, Arabic")
    print("  • Any language supported by OpenAI")
    print()


def display_requirements():
    """Display system requirements."""
    print("📋 System Requirements:")
    print("=" * 40)
    
    print("🔧 System Tools:")
    print("  • Python 3.11 or higher")
    print("  • FFmpeg (for video/audio processing)")
    print("  • Internet connection (for APIs and YouTube)")
    print()
    
    print("📦 Python Dependencies:")
    print("  • openai>=1.93.0 (OpenAI API client)")
    print("  • ffmpeg-python>=0.2.0 (FFmpeg wrapper)")
    print("  • yt-dlp>=2025.6.25 (YouTube downloader)")
    print()
    
    print("🔑 API Requirements:")
    print("  • OpenAI API key")
    print("  • Sufficient API credits")
    print("  • Internet connection for API calls")
    print()


def display_usage_examples():
    """Display usage examples."""
    print("🚀 Usage Examples:")
    print("=" * 40)
    
    print("📺 YouTube Video Translation:")
    print("  uv run python main.py 'https://youtu.be/VIDEO_ID' output.mp4")
    print("  uv run python main.py 'https://youtube.com/watch?v=ID' video.mp4 --voice nova")
    print()
    
    print("📁 Local Video Translation:")
    print("  uv run python main.py input_video.mp4 output_video.mp4")
    print("  uv run python main.py video.mp4 hindi.mp4 --voice shimmer")
    print()
    
    print("🌍 Multi-language Translation:")
    print("  uv run python main.py video.mp4 spanish.mp4 --language Spanish")
    print("  uv run python main.py 'https://youtu.be/ID' french.mp4 --language French")
    print()
    
    print("🛠️ Advanced Options:")
    print("  uv run python main.py video.mp4 output.mp4 --keep-temp")
    print("  uv run python main.py 'https://youtu.be/ID' out.mp4 --youtube-dir ./downloads")
    print("  uv run python main.py video.mp4 output.mp4 --api-key YOUR_KEY")
    print()


def check_project_files():
    """Check if project files are present."""
    print("📁 Project Structure Check:")
    print("=" * 40)
    
    core_files = [
        ("main.py", "Main application with YouTube support"),
        ("pyproject.toml", "Project configuration"),
        ("README.md", "Documentation"),
        ("env.template", "Environment variables template"),
        ("check_requirements.py", "Requirements checker"),
        ("example_usage.py", "Usage examples"),
        ("uv.lock", "Dependency lock file")
    ]
    
    all_present = True
    for filename, description in core_files:
        if Path(filename).exists():
            print(f"  ✅ {filename} - {description}")
        else:
            print(f"  ❌ {filename} - Missing")
            all_present = False
    
    print()
    if all_present:
        print("🎉 All core project files are present!")
    else:
        print("⚠️ Some project files are missing. Please check your installation.")
    
    return all_present


def quick_verification():
    """Perform quick verification checks."""
    print("🔍 Quick Verification:")
    print("=" * 40)
    
    checks = []
    
    # Check Python version
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"  ✅ Python {version.major}.{version.minor} - Compatible")
        checks.append(True)
    else:
        print(f"  ❌ Python {version.major}.{version.minor} - Requires 3.11+")
        checks.append(False)
    
    # Check if main module can be imported
    try:
        from main import VideoTranslator
        print("  ✅ Main module - Can import VideoTranslator")
        checks.append(True)
        
        # Test YouTube URL detection
        try:
            temp_translator = object.__new__(VideoTranslator)
            test_result = temp_translator.is_youtube_url("https://youtu.be/test")
            if test_result:
                print("  ✅ YouTube URL detection - Working")
                checks.append(True)
            else:
                print("  ❌ YouTube URL detection - Failed")
                checks.append(False)
        except Exception:
            print("  ❌ YouTube URL detection - Error")
            checks.append(False)
            
    except ImportError as e:
        print(f"  ❌ Main module - Import error: {e}")
        checks.append(False)
        checks.append(False)  # Skip YouTube test
    
    # Check dependencies
    dependencies = ["openai", "ffmpeg", "yt_dlp"]
    for dep in dependencies:
        try:
            if dep == "ffmpeg":
                import ffmpeg
            elif dep == "yt_dlp":
                import yt_dlp
            else:
                __import__(dep)
            print(f"  ✅ {dep} - Installed")
            checks.append(True)
        except ImportError:
            print(f"  ❌ {dep} - Not installed")
            checks.append(False)
    
    print()
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print("🎉 All verifications passed! Ready to translate videos.")
        print()
        print("🚀 Next steps:")
        print("  1. Set your OpenAI API key: export OPENAI_API_KEY='your_key'")
        print("  2. Test with a video: uv run python main.py input.mp4 output.mp4")
        print("  3. Try YouTube: uv run python main.py 'https://youtu.be/ID' output.mp4")
        return True
    else:
        print(f"⚠️ {passed}/{total} checks passed. Run check_requirements.py for details.")
        return False


def display_cost_information():
    """Display API cost information."""
    print("💰 API Cost Information:")
    print("=" * 40)
    
    print("📊 OpenAI API Pricing:")
    print("  • Whisper (transcription): $0.006 per minute")
    print("  • GPT-4 (translation): ~$0.03 per 1K tokens")
    print("  • TTS (text-to-speech): $0.015 per 1K characters")
    print()
    
    print("💵 Estimated Costs:")
    print("  • 1-minute video: ~$0.10 - $0.50")
    print("  • 5-minute video: ~$0.50 - $2.50")
    print("  • 10-minute video: ~$1.00 - $5.00")
    print()
    
    print("💡 Cost Optimization Tips:")
    print("  • Test with short videos first")
    print("  • Use --keep-temp to avoid re-transcribing during debugging")
    print("  • Be mindful of video length and speech density")
    print("  • Monitor your OpenAI usage dashboard")
    print()


def display_troubleshooting():
    """Display common troubleshooting information."""
    print("🚨 Common Issues & Solutions:")
    print("=" * 40)
    
    print("❌ FFmpeg not found:")
    print("  • Windows: Download from ffmpeg.org and add to PATH")
    print("  • macOS: brew install ffmpeg")
    print("  • Linux: sudo apt install ffmpeg")
    print()
    
    print("❌ YouTube download fails:")
    print("  • Check if video is public and accessible")
    print("  • Verify internet connection")
    print("  • Some videos may have regional restrictions")
    print("  • Large videos take longer to download")
    print()
    
    print("❌ OpenAI API errors:")
    print("  • Verify API key is correct and active")
    print("  • Check you have sufficient API credits")
    print("  • Monitor rate limits and quotas")
    print()
    
    print("❌ Memory issues:")
    print("  • Process shorter video segments")
    print("  • Ensure sufficient disk space")
    print("  • Close other applications")
    print()
    
    print("💡 Debug mode:")
    print("  • Use --keep-temp to save intermediate files")
    print("  • Check logs for detailed error messages")
    print("  • Test with short videos first")
    print()


def main():
    """Main function to display project summary."""
    print()
    display_project_info()
    print()
    
    display_supported_formats()
    print()
    
    display_requirements()
    print()
    
    display_usage_examples()
    print()
    
    project_files_ok = check_project_files()
    print()
    
    verification_ok = quick_verification()
    print()
    
    display_cost_information()
    print()
    
    display_troubleshooting()
    
    print("=" * 60)
    if project_files_ok and verification_ok:
        print("🎉 Project setup looks good! You're ready to start translating videos.")
        print()
        print("🎬 Try it out:")
        print("  # For a local video:")
        print("  uv run python main.py your_video.mp4 hindi_output.mp4")
        print()
        print("  # For a YouTube video:")
        print("  uv run python main.py 'https://youtu.be/VIDEO_ID' hindi_output.mp4")
        print()
        print("📚 For more examples, run: uv run python example_usage.py")
        print("🔍 For detailed checks, run: uv run python check_requirements.py")
        return 0
    else:
        print("⚠️ Setup issues detected. Please resolve them before proceeding.")
        print()
        print("🔧 Next steps:")
        print("  1. Run: uv run python check_requirements.py")
        print("  2. Follow the installation instructions in README.md")
        print("  3. Set up your OpenAI API key")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 