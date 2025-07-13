#!/usr/bin/env python3
"""
Simple launcher script for the Video Translator GUI

This script provides an easy way to launch the GUI application
with proper error handling and requirements checking.
"""

import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all required dependencies are installed."""
    missing_deps = []
    
    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")
    
    try:
        import ffmpeg
    except ImportError:
        missing_deps.append("ffmpeg-python")
    
    try:
        import openai
    except ImportError:
        missing_deps.append("openai")
    
    try:
        import yt_dlp
    except ImportError:
        missing_deps.append("yt-dlp")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 Install missing dependencies with:")
        print("   uv sync")
        print("   OR")
        print("   pip install " + " ".join(missing_deps))
        return False
    
    return True

def main():
    """Main launcher function."""
    print("🎬 Video Translator GUI Launcher")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Error: Python 3.11 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_requirements():
        sys.exit(1)
    
    print("✅ All dependencies found!")
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set.")
        print("   You can set it in the GUI or create a .env file.")
    else:
        print("✅ OpenAI API key found in environment.")
    
    # Check for FFmpeg
    import shutil
    if not shutil.which('ffmpeg'):
        print("⚠️  Warning: FFmpeg not found in PATH.")
        print("   Please install FFmpeg and add it to your PATH.")
        print("   Download from: https://ffmpeg.org/download.html")
    else:
        print("✅ FFmpeg found in PATH.")
    
    print("\n🚀 Starting GUI application...")
    
    try:
        # Import and run the GUI
        from video_translator_gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 