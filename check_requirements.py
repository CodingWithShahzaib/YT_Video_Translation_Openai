#!/usr/bin/env python3
"""
System Requirements Checker for English to Hindi Video Translator

This script checks if all necessary requirements are installed and properly configured:
- Python version
- FFmpeg installation
- Python dependencies (including yt-dlp)
- OpenAI API key
"""

import sys
import subprocess
import os
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except (ImportError, Exception):
    pass  # python-dotenv not installed or .env file has issues, skip loading


def check_python_version():
    """Check if Python version is 3.11 or higher."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 11:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.11+")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed and accessible."""
    print("🎬 Checking FFmpeg installation...")
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            # Extract version from output
            lines = result.stdout.split('\n')
            version_line = next((line for line in lines if line.startswith('ffmpeg version')), None)
            if version_line:
                version = version_line.split()[2]
                print(f"   ✅ FFmpeg {version} - OK")
            else:
                print("   ✅ FFmpeg installed - OK")
            return True
        else:
            print("   ❌ FFmpeg not working properly")
            return False
    except FileNotFoundError:
        print("   ❌ FFmpeg not found in PATH")
        print("   💡 Install FFmpeg: https://ffmpeg.org/download.html")
        return False
    except subprocess.TimeoutExpired:
        print("   ❌ FFmpeg command timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error checking FFmpeg: {e}")
        return False


def check_python_dependencies():
    """Check if required Python packages are installed."""
    print("📦 Checking Python dependencies...")
    required_packages = {
        'openai': 'OpenAI API client',
        'ffmpeg': 'FFmpeg Python wrapper',
        'yt_dlp': 'YouTube video downloader',
        'dotenv': 'Environment file loader'
    }
    
    all_installed = True
    
    for package, description in required_packages.items():
        try:
            if package == 'ffmpeg':
                import ffmpeg
                print(f"   ✅ {package} ({description}) - OK")
            elif package == 'openai':
                import openai
                print(f"   ✅ {package} ({description}) - OK")
            elif package == 'yt_dlp':
                import yt_dlp
                print(f"   ✅ {package} ({description}) - OK")
            elif package == 'dotenv':
                from dotenv import load_dotenv
                print(f"   ✅ {package} ({description}) - OK")
            else:
                __import__(package)
                print(f"   ✅ {package} ({description}) - OK")
        except ImportError:
            print(f"   ❌ {package} ({description}) - Not installed")
            all_installed = False
    
    if not all_installed:
        print("   💡 Install missing packages: uv sync")
        
    return all_installed


def check_openai_api_key():
    """Check if OpenAI API key is configured."""
    print("🔑 Checking OpenAI API key...")
    
    # Check if .env file exists
    env_file_exists = Path('.env').exists()
    if env_file_exists:
        print("   📄 .env file found - environment variables loaded")
    
    # Check environment variable (could be from .env file or system)
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        # Basic validation
        if api_key.startswith('sk-') and len(api_key) > 20:
            source = ".env file or environment" if env_file_exists else "environment"
            print(f"   ✅ OpenAI API key found in {source} - OK")
            return True
        else:
            print("   ⚠️  OpenAI API key found but format looks incorrect")
            print("   💡 API keys should start with 'sk-' and be ~51 characters long")
            return False
    else:
        print("   ❌ OpenAI API key not found")
        print("   💡 Get your API key from: https://platform.openai.com/api-keys")
        if env_file_exists:
            print("   💡 .env file found but OPENAI_API_KEY not set in it")
            print("   💡 Add this line to your .env file: OPENAI_API_KEY=your_key_here")
        else:
            print("   💡 Create a .env file with: OPENAI_API_KEY=your_key_here")
            print("   💡 Or set environment variable: export OPENAI_API_KEY='your_key_here'")
        return False


def check_project_structure():
    """Check if project files are in place."""
    print("📁 Checking project structure...")
    
    required_files = [
        'main.py',
        'pyproject.toml',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file} - OK")
        else:
            print(f"   ❌ {file} - Missing")
            missing_files.append(file)
    
    return len(missing_files) == 0


def test_basic_functionality():
    """Test basic functionality without API calls."""
    print("🧪 Testing basic functionality...")
    
    try:
        # Test imports
        from main import VideoTranslator
        print("   ✅ Main module imports - OK")
        
        # Test class initialization without API key
        try:
            translator = VideoTranslator(api_key="test-key")
            print("   ✅ VideoTranslator class - OK")
        except Exception as e:
            if "API key" in str(e):
                print("   ✅ VideoTranslator class validation - OK")
            else:
                print(f"   ❌ VideoTranslator class error: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False


def test_youtube_functionality():
    """Test YouTube URL detection functionality."""
    print("🎥 Testing YouTube functionality...")
    
    try:
        from main import VideoTranslator
        
        # Test without API key for URL detection
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "local_video.mp4",
            "not_a_url"
        ]
        
        # Create a temporary instance for URL testing
        try:
            translator = VideoTranslator(api_key="test-key")
        except:
            # Even without valid API key, we can test URL detection
            pass
        
        # Test URL detection method directly
        from main import VideoTranslator
        temp_translator = object.__new__(VideoTranslator)
        
        youtube_detected = temp_translator.is_youtube_url(test_urls[0])
        youtube_short_detected = temp_translator.is_youtube_url(test_urls[1])
        youtube_shorts_detected = temp_translator.is_youtube_url(test_urls[2])
        local_file_detected = temp_translator.is_youtube_url(test_urls[3])
        
        if youtube_detected and youtube_short_detected and youtube_shorts_detected and not local_file_detected:
            print("   ✅ YouTube URL detection - OK")
            return True
        else:
            print("   ❌ YouTube URL detection failed")
            return False
            
    except Exception as e:
        print(f"   ❌ YouTube functionality test error: {e}")
        return False


def check_internet_connection():
    """Check basic internet connectivity."""
    print("🌐 Checking internet connection...")
    
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("   ✅ Internet connection - OK")
        return True
    except Exception:
        print("   ❌ Internet connection - Failed")
        print("   💡 Internet connection required for YouTube downloads and OpenAI APIs")
        return False


def main():
    """Run all checks and provide summary."""
    print("🔍 Video Translator Requirements Checker")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("FFmpeg", check_ffmpeg),
        ("Python Dependencies", check_python_dependencies),
        ("OpenAI API Key", check_openai_api_key),
        ("Project Structure", check_project_structure),
        ("Basic Functionality", test_basic_functionality),
        ("YouTube Functionality", test_youtube_functionality),
        ("Internet Connection", check_internet_connection)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Error during {name} check: {e}")
            results.append(False)
        print()
    
    # Summary
    print("📊 Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All checks passed! You're ready to translate videos.")
        print("\n🚀 Usage examples:")
        print("   # Local video:")
        print("   uv run python main.py input_video.mp4 output_video.mp4")
        print("   # YouTube video:")
        print("   uv run python main.py 'https://youtu.be/VIDEO_ID' output_video.mp4")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed. Please fix the issues above.")
        
        if not results[0]:  # Python version
            print("\n🔧 Fix Python version first, then re-run this check.")
        elif not results[1]:  # FFmpeg
            print("\n🔧 Install FFmpeg next:")
            print("   Windows: Download from https://ffmpeg.org/download.html")
            print("   macOS: brew install ffmpeg")
            print("   Linux: sudo apt install ffmpeg")
        elif not results[2]:  # Dependencies
            print("\n🔧 Install Python dependencies:")
            print("   uv sync")
        elif not results[3]:  # API key
            print("\n🔧 Set up OpenAI API key:")
            print("   1. Get key from https://platform.openai.com/api-keys")
            print("   2. Set environment variable: export OPENAI_API_KEY='your_key'")
        elif not results[7]:  # Internet connection
            print("\n🔧 Check internet connection:")
            print("   - Required for YouTube downloads and OpenAI API calls")
            print("   - Verify your network settings")
        
        return 1


if __name__ == "__main__":
    sys.exit(main()) 