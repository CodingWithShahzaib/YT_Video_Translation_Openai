#!/usr/bin/env python3
"""
Example Usage of Video Translator

This script demonstrates how to use the VideoTranslator class programmatically
with proper error handling and configuration. Includes examples for both local
video files and YouTube URLs.
"""

import os
import sys
from pathlib import Path
from main import VideoTranslator


def example_basic_usage():
    """Basic example of video translation."""
    print("🎬 Basic Video Translation Example")
    print("=" * 40)
    
    # Initialize translator
    try:
        translator = VideoTranslator()
        print("✅ VideoTranslator initialized successfully")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure to set OPENAI_API_KEY environment variable")
        return False
    
    # Example video paths (replace with your actual files)
    input_video = "sample_english_video.mp4"
    output_video = "sample_hindi_video.mp4"
    
    # Check if input file exists
    if not Path(input_video).exists():
        print(f"📁 Input video not found: {input_video}")
        print("💡 Please provide a valid English video file")
        return False
    
    try:
        # Translate the video
        translator.translate_video(
            input_source=input_video,
            output_video=output_video,
            target_language="Hindi",
            voice="nova",  # Try different voices: alloy, echo, fable, onyx, nova, shimmer
            keep_temp_files=True  # Keep intermediate files for debugging
        )
        
        print(f"🎉 Translation completed! Output: {output_video}")
        return True
        
    except Exception as e:
        print(f"❌ Error during translation: {e}")
        return False


def example_youtube_translation():
    """Example of translating YouTube videos."""
    print("🎥 YouTube Video Translation Example")
    print("=" * 40)
    
    # Initialize translator
    try:
        translator = VideoTranslator()
        print("✅ VideoTranslator initialized successfully")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure to set OPENAI_API_KEY environment variable")
        return False
    
    # Example YouTube URLs (replace with actual URLs you want to translate)
    youtube_examples = [
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "output": "rickroll_hindi.mp4",
            "description": "Classic video"
        },
        {
            "url": "https://youtu.be/dQw4w9WgXcQ",  # Short URL format
            "output": "short_url_hindi.mp4", 
            "description": "Short URL format example"
        }
    ]
    
    for i, example in enumerate(youtube_examples, 1):
        print(f"\n📺 Example {i}: {example['description']}")
        print(f"   URL: {example['url']}")
        print(f"   Output: {example['output']}")
        
        # Note: These are example URLs - replace with actual content you have rights to translate
        print("   💡 Replace with actual YouTube URLs you have rights to translate")
        
        # Example of how you would call it (commented out to avoid actual downloads)
        """
        try:
            translator.translate_video(
                input_source=example['url'],
                output_video=example['output'],
                target_language="Hindi",
                voice="alloy",
                keep_temp_files=True  # Keep downloaded video and intermediate files
            )
            print(f"   ✅ Completed: {example['output']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        """
    
    print("\n💡 To run YouTube translation:")
    print("   1. Replace example URLs with actual videos")
    print("   2. Ensure you have rights to download and translate the content")
    print("   3. Uncomment the translation code above")
    print("   4. Run the script")
    
    return True


def example_batch_processing():
    """Example of processing multiple videos."""
    print("\n📚 Batch Processing Example")
    print("=" * 40)
    
    # Mixed list of local files and YouTube URLs
    video_sources = [
        {"source": "video1.mp4", "type": "local"},
        {"source": "https://youtu.be/EXAMPLE1", "type": "youtube"},
        {"source": "video2.mp4", "type": "local"},
        {"source": "https://www.youtube.com/watch?v=EXAMPLE2", "type": "youtube"}
    ]
    
    # Initialize translator once
    try:
        translator = VideoTranslator()
    except ValueError as e:
        print(f"❌ Error: {e}")
        return False
    
    successful = 0
    failed = 0
    
    for i, video_info in enumerate(video_sources, 1):
        source = video_info["source"]
        source_type = video_info["type"]
        
        print(f"\n📹 Processing {source_type} {i}/{len(video_sources)}: {source}")
        
        # Skip if local file doesn't exist
        if source_type == "local" and not Path(source).exists():
            print(f"   ⚠️ Skipping {source} - local file not found")
            failed += 1
            continue
        
        # Generate output filename
        if source_type == "youtube":
            output_file = f"hindi_youtube_{i}.mp4"
        else:
            output_file = f"hindi_{source}"
        
        print(f"   💡 Would translate to: {output_file}")
        print(f"   💡 This is a demonstration - actual translation commented out")
        
        # Example of how you would process (commented out for demonstration)
        """
        try:
            translator.translate_video(
                input_source=source,
                output_video=output_file,
                target_language="Hindi",
                voice="alloy",
                keep_temp_files=False
            )
            print(f"   ✅ Completed: {output_file}")
            successful += 1
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            failed += 1
        """
        
        # For demonstration, mark as successful
        successful += 1
    
    print(f"\n📊 Batch processing summary:")
    print(f"   ✅ Would be successful: {successful}")
    print(f"   ❌ Would fail: {failed}")
    
    return successful > 0


def example_different_languages():
    """Example of translating to different languages."""
    print("\n🌍 Multi-language Translation Example")
    print("=" * 40)
    
    # Can use either local file or YouTube URL
    input_sources = [
        "english_sample.mp4",  # Local file
        "https://youtu.be/EXAMPLE_ID"  # YouTube URL
    ]
    
    # Languages to translate to
    languages = [
        ("Hindi", "hindi"),
        ("Spanish", "spanish"),
        ("French", "french"),
        ("German", "german"),
        ("Japanese", "japanese")
    ]
    
    try:
        translator = VideoTranslator()
    except ValueError as e:
        print(f"❌ Error: {e}")
        return False
    
    for source in input_sources:
        source_type = "YouTube URL" if source.startswith("http") else "Local file"
        print(f"\n🎬 Processing {source_type}: {source}")
        
        if not source.startswith("http") and not Path(source).exists():
            print(f"   📁 {source_type} not found, skipping...")
            continue
        
        for language, suffix in languages:
            print(f"\n🗣️ Would translate to {language}...")
            
            if source.startswith("http"):
                output_file = f"{suffix}_youtube_video.mp4"
            else:
                output_file = f"{suffix}_{source}"
            
            print(f"   💡 Output would be: {output_file}")
            print(f"   💡 Language: {language}")
            print(f"   💡 This is a demonstration - actual translation commented out")
            
            # Example of how you would translate (commented out for demonstration)
            """
            try:
                translator.translate_video(
                    input_source=source,
                    output_video=output_file,
                    target_language=language,
                    voice="nova",
                    keep_temp_files=False
                )
                print(f"   ✅ {language} translation completed: {output_file}")
                
            except Exception as e:
                print(f"   ❌ {language} translation failed: {e}")
            """
    
    return True


def example_custom_configuration():
    """Example with custom API configuration and YouTube download directory."""
    print("\n⚙️ Custom Configuration Example")
    print("=" * 40)
    
    # You can provide API key directly instead of environment variable
    custom_api_key = os.getenv('CUSTOM_OPENAI_KEY')  # Use different env var
    
    if custom_api_key:
        try:
            translator = VideoTranslator(api_key=custom_api_key)
            print("✅ Custom API key configuration successful")
        except ValueError as e:
            print(f"❌ Error with custom API key: {e}")
            return False
    else:
        print("💡 No custom API key provided, using default configuration")
        try:
            translator = VideoTranslator()
        except ValueError as e:
            print(f"❌ Error: {e}")
            return False
    
    # Example with detailed configuration for YouTube video
    youtube_url = "https://www.youtube.com/watch?v=EXAMPLE_ID"
    output_video = "custom_config_hindi.mp4"
    download_dir = "./youtube_downloads"
    
    print(f"📺 Example YouTube URL: {youtube_url}")
    print(f"📁 Custom download directory: {download_dir}")
    print(f"🎯 Output video: {output_video}")
    print("💡 This is a demonstration - actual translation commented out")
    
    # Create download directory if it doesn't exist
    Path(download_dir).mkdir(exist_ok=True)
    print(f"   ✅ Download directory created/verified: {download_dir}")
    
    # Example configuration (commented out for demonstration)
    """
    try:
        translator.translate_video(
            input_source=youtube_url,
            output_video=output_video,
            target_language="Hindi",
            voice="shimmer",  # Soft, warm voice
            keep_temp_files=True,  # Keep files for inspection
            youtube_download_dir=download_dir  # Save YouTube videos here
        )
        print(f"✅ Custom configuration translation completed")
        return True
        
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        return False
    """
    
    print("✅ Configuration example completed")
    return True


def example_url_detection():
    """Demonstrate YouTube URL detection functionality."""
    print("\n🔍 YouTube URL Detection Example")
    print("=" * 40)
    
    try:
        from main import VideoTranslator
        
        # Create translator instance for testing
        translator = VideoTranslator(api_key="test-key")  # Dummy key for URL testing
        
        # Test various URL formats
        test_inputs = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ", 
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "local_video.mp4",
            "not_a_url_at_all",
            "/path/to/video.mp4"
        ]
        
        print("Testing URL detection:")
        for test_input in test_inputs:
            is_youtube = translator.is_youtube_url(test_input)
            status = "✅ YouTube URL" if is_youtube else "📁 Local file/other"
            print(f"   {status}: {test_input}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL detection test failed: {e}")
        return False


def main():
    """Run all examples."""
    print("🚀 Video Translator Examples (with YouTube Support!)")
    print("=" * 60)
    
    # Check if we have the required modules
    try:
        from main import VideoTranslator
        print("✅ VideoTranslator module loaded successfully\n")
    except ImportError as e:
        print(f"❌ Error importing VideoTranslator: {e}")
        print("💡 Make sure you're running this from the project directory")
        return 1
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("YouTube Translation", example_youtube_translation),
        ("Batch Processing", example_batch_processing),
        ("Multi-language", example_different_languages),
        ("Custom Configuration", example_custom_configuration),
        ("URL Detection", example_url_detection)
    ]
    
    for name, example_func in examples:
        try:
            print(f"\n{'='*60}")
            result = example_func()
            if result:
                print(f"✅ {name} example completed successfully")
            else:
                print(f"⚠️ {name} example finished with warnings")
        except Exception as e:
            print(f"❌ {name} example failed: {e}")
        
        print()
    
    print("📚 Examples completed!")
    print("\n💡 Tips for YouTube Translation:")
    print("   - Ensure you have rights to download and translate the content")
    print("   - Use --youtube-dir to save downloaded videos permanently")
    print("   - YouTube videos are downloaded temporarily by default")
    print("   - Some videos may have regional restrictions")
    print("   - Large videos will take longer to download and process")
    
    print("\n💡 General Tips:")
    print("   - Replace example file paths with your actual video files")
    print("   - Set OPENAI_API_KEY environment variable before running")
    print("   - Check the README.md for more detailed instructions")
    print("   - Use --keep-temp flag to debug translation issues")
    print("   - Test with short videos first to verify everything works")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 