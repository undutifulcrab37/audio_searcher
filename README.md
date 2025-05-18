# AUCHIVE 🎵

AUCHIVE is a powerful audio search tool built for audio producers, podcasters, and content creators who need to quickly find specific moments in their audio archives. Using advanced AI-powered transcription, AUCHIVE makes your audio content searchable in seconds.

## Features ✨

- **Smart Audio Transcription**: Automatically transcribes audio files using state-of-the-art Whisper AI technology
- **Multi-Format Support**: Handles various audio formats including MP3, WAV, and M4A
- **Intelligent Search**: Search through transcripts with context-aware results
- **Timestamp Integration**: Every search result includes precise timestamps for easy audio location
- **Cache System**: Smart caching system for faster repeated searches
- **Modern UI**: Clean, intuitive interface with real-time visual feedback

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/yourusername/auchive.git
cd auchive
```

2. Create and activate a virtual environment:
```bash
# For macOS/Linux
python -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage 💡

1. Start the application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Upload audio files:
   - Click the upload button in the left column
   - Select one or more audio files (MP3, WAV, M4A)
   - Wait for the transcription process to complete

4. Search your content:
   - Enter keywords in the search box
   - Click "Search" to find matches
   - Results will show with timestamps and context

## Supported File Types 📁

### Audio Files
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)

### Transcript Files
- Text files (.txt)
- SubRip Subtitle (.srt)
- WebVTT (.vtt)
- JSON (.json)

## Technical Requirements 🔧

- Python 3.8 or higher
- FFmpeg (for audio processing)
- Internet connection (for initial Whisper model download)

### Required Python Packages
- streamlit
- whisper
- speech_recognition
- pydub
- numpy

## Troubleshooting 🔍

### Common Issues

1. **FFmpeg not found**
   ```bash
   # macOS (using Homebrew)
   brew install ffmpeg

   # Windows (using Chocolatey)
   choco install ffmpeg
   ```

2. **Audio file not recognized**
   - Ensure the file format is supported
   - Check if FFmpeg is properly installed
   - Verify the file isn't corrupted

3. **Transcription is slow**
   - This is normal for the first run as the Whisper model needs to download
   - Subsequent runs will be faster due to caching
   - Consider using a machine with a GPU for faster processing

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

[MIT License](LICENSE)

## Support 💪

If you encounter any issues or have questions, please:
1. Check the troubleshooting section
2. Open an issue in the GitHub repository
3. Contact the development team

---

Built with ❤️ for audio professionals 