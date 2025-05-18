import streamlit as st
import os
from pathlib import Path
import json
import time
from typing import Dict, List, Tuple
import hashlib
import re
from datetime import datetime
import shutil
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_nonsilent
import tempfile
import io
import numpy as np
import whisper  # Advanced AI-based speech recognition model
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from hashlib import md5

# Initialize session state for cache and uploaded files
if 'transcript_cache' not in st.session_state:
    st.session_state.transcript_cache = {}
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'keywords' not in st.session_state:
    st.session_state.keywords = ""
if 'folder_path' not in st.session_state:
    st.session_state.folder_path = None

# Define colors
PRIMARY_PURPLE = "#7B5AC4"
SECONDARY_TEAL = "#56C8C6"
BG_COLOR = "#56C8C6"  # Teal background color
LIGHT_PURPLE = "#F0E8FF"
TEXT_DARK = "#2D3142"

# Custom styling
st.set_page_config(
    page_title="AUCHIVE",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.cdnfonts.com/css/gotham');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Define animations */
    @keyframes wave1 {
        0% { transform: scaleY(1.2); opacity: 0.7; }
        50% { transform: scaleY(0.3); opacity: 0.9; }
        100% { transform: scaleY(1.2); opacity: 0.7; }
    }
    
    @keyframes wave2 {
        0% { transform: scaleY(0.5); opacity: 0.8; }
        50% { transform: scaleY(1.4); opacity: 1; }
        100% { transform: scaleY(0.5); opacity: 0.8; }
    }
    
    @keyframes wave3 {
        0% { transform: scaleY(0.8); opacity: 0.6; }
        50% { transform: scaleY(0.2); opacity: 0.8; }
        100% { transform: scaleY(0.8); opacity: 0.6; }
    }
    
    /* Modern styling for the entire app */
    .stApp {
        background: linear-gradient(135deg, #56C8C6 0%, #4FA8A6 100%) !important;
    }
    
    /* Main container with glass effect */
    .main {
        background: transparent !important;
        min-height: 100vh;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        position: relative;
        overflow: hidden;
    }
    
    /* Glass effect containers */
    .stTextInput, .stTextArea, .stButton, .stSelectbox, [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    /* Hover effects */
    .stTextInput:hover, .stTextArea:hover, .stButton:hover, .stSelectbox:hover, [data-testid="stFileUploader"]:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px);
    }
    
    /* Button styling */
    .stButton > button {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px);
    }
    
    /* Search results styling */
    .search-result {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Background watermark */
    .main:before {
        content: "AUCHIVE";
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 35vw;
        font-weight: 900;
        font-family: 'Gotham', 'Inter', sans-serif;
        color: rgba(255, 255, 255, 0.05);
        white-space: nowrap;
        z-index: 0;
        letter-spacing: -0.05em;
        pointer-events: none;
    }
    
    /* Logo container */
    .logo-container {
        position: relative;
        margin: 1rem 0 3rem 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 140px;  /* Increased height to accommodate tagline */
    }
    
    /* Brand title */
    .brand {
        font-family: 'Gotham', 'Inter', sans-serif !important;
        font-weight: 800;
        font-size: 4.5rem !important;
        margin: 0 !important;
        letter-spacing: -0.02em;
        color: white !important;
        text-transform: uppercase;
        text-align: center;
        text-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        position: absolute;
        top: 40%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 2;
        white-space: nowrap;
    }
    
    /* Audio waves container */
    .waves-container {
        position: absolute;
        width: 100%;
        max-width: 460px; /* Match logo width */
        height: 50px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 3px;
        z-index: 1;
        top: 40%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    
    /* Wave bars with enhanced animations */
    .wave-bar {
        width: 3px;
        height: 100%;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
        animation-duration: 1.2s;
        animation-iteration-count: infinite;
        animation-timing-function: ease-in-out;
    }
    
    .wave-bar:nth-child(3n+1) {
        animation-name: wave1;
        animation-delay: -0.2s;
        height: 60%;
    }
    
    .wave-bar:nth-child(3n+2) {
        animation-name: wave2;
        animation-delay: -0.5s;
        height: 80%;
    }
    
    .wave-bar:nth-child(3n) {
        animation-name: wave3;
        animation-delay: -0.8s;
        height: 40%;
    }
    
    @keyframes wave1 {
        0% { transform: scaleY(0.6); opacity: 0.3; }
        50% { transform: scaleY(1.2); opacity: 0.6; }
        100% { transform: scaleY(0.6); opacity: 0.3; }
    }
    
    @keyframes wave2 {
        0% { transform: scaleY(1.2); opacity: 0.3; }
        50% { transform: scaleY(0.6); opacity: 0.6; }
        100% { transform: scaleY(1.2); opacity: 0.3; }
    }
    
    @keyframes wave3 {
        0% { transform: scaleY(0.8); opacity: 0.3; }
        50% { transform: scaleY(1.4); opacity: 0.6; }
        100% { transform: scaleY(0.8); opacity: 0.3; }
    }
    
    /* Brand accent text - updated styling */
    .brand-accent {
        font-family: 'Gotham', 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        color: white !important;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 2;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
        white-space: nowrap;
    }
    
    /* Modern file uploader */
    [data-testid="stFileUploader"] {
        padding: 2rem !important;
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px dashed rgba(255, 255, 255, 0.2) !important;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0.8) 100%) !important;
        border-radius: 8px !important;
    }
    
    /* Success/Warning/Error message styling */
    .stSuccess, .stWarning, .stError {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 1rem 1.5rem !important;
        color: white !important;
    }
    
    /* Keyword highlights */
    mark {
        background-color: rgba(255, 245, 157, 0.9) !important;
        color: #1a1a1a !important;
        padding: 0.2em 0.4em !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Feature icons styling */
    .feature-icons {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 3rem;
        margin: 3rem 0;
    }
    
    .feature-icon {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    
    .icon-circle {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        width: 90px;
        height: 90px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .icon-circle:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.15);
    }
    
    .icon-svg {
        width: 40px;
        height: 40px;
        stroke: white;
        stroke-width: 2;
        fill: none;
        opacity: 0.9;
    }
    
    .icon-label {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        color: white;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .feature-icon:hover .icon-label {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_cache_key(folder_path: str) -> str:
    """Generate a unique cache key for a folder."""
    return hashlib.md5(folder_path.encode()).hexdigest()

def load_cache():
    """Load cache from disk if it exists."""
    cache_file = Path("data/cache.json")
    if cache_file.exists():
        with open(cache_file, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache_data: Dict):
    """Save cache to disk."""
    os.makedirs("data", exist_ok=True)
    with open("data/cache.json", "w") as f:
        json.dump(cache_data, f)

def parse_timestamp(timestamp_str: str) -> float:
    """Convert various timestamp formats to seconds."""
    try:
        # Try MM:SS format
        time_obj = datetime.strptime(timestamp_str.strip(), "%M:%S")
        return time_obj.minute * 60 + time_obj.second
    except ValueError:
        try:
            # Try HH:MM:SS format
            time_obj = datetime.strptime(timestamp_str.strip(), "%H:%M:%S")
            return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
        except ValueError:
            # Return 0 if format is unrecognized
            return 0.0

def extract_text_from_audio(audio_file_path, progress_callback=None):
    """Extract text with timestamps from audio file using speech recognition."""
    try:
        # Update progress if callback provided
        if progress_callback:
            progress_callback(0.1)
            
        print(f"Starting transcription of {audio_file_path}")
        
        # Load the audio file
        try:
            file_ext = Path(audio_file_path).suffix.lower()
            
            if file_ext == '.mp3':
                audio = AudioSegment.from_mp3(audio_file_path)
            elif file_ext == '.wav':
                audio = AudioSegment.from_wav(audio_file_path)
            elif file_ext == '.m4a':
                audio = AudioSegment.from_file(audio_file_path, format='m4a') 
            else:
                audio = AudioSegment.from_file(audio_file_path)
        except Exception as e:
            print(f"Error loading audio: {str(e)}")
            return f"Error loading audio: {str(e)}"
        
        # Get audio duration
        duration_seconds = len(audio) / 1000
        
        # Update progress
        if progress_callback:
            progress_callback(0.15)
            
        # Choose transcription method based on file duration
        if duration_seconds > 600:  # Over 10 minutes
            # For longer files, use chunking approach
            print(f"Long audio detected ({duration_seconds:.1f} seconds). Using chunked processing.")
            return process_long_audio(audio_file_path, progress_callback)
        else:
            # For shorter files, process directly with Whisper
            print(f"Short audio detected ({duration_seconds:.1f} seconds). Using direct processing.")
            
            try:
                if progress_callback:
                    progress_callback(0.2)
                    
                model = whisper.load_model("tiny")
                
                if progress_callback:
                    progress_callback(0.3)
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_path = temp_file.name
                    audio.export(temp_path, format="wav")
                    
                    if progress_callback:
                        progress_callback(0.4)
                    
                    print("Starting Whisper transcription...")
                    result = model.transcribe(
                        temp_path,
                        fp16=False,
                        language="en"
                    )
                    
                    os.unlink(temp_path)
                    
                    if progress_callback:
                        progress_callback(0.9)
                    
                    transcription = result["text"]
                    timestamp_text = ""
                    
                    current_time = 0
                    segments = transcription.split(". ")
                    total_segments = len(segments)
                    
                    for i, segment in enumerate(segments):
                        if i % 3 == 0 or i == 0:
                            minutes = int(current_time // 60)
                            seconds = int(current_time % 60)
                            timestamp = f"[{minutes:02d}:{seconds:02d}] "
                            timestamp_text += timestamp + segment + ". "
                            
                            current_time += min(30, duration_seconds / total_segments * 3)
                        else:
                            timestamp_text += segment + ". "
                    
                    if progress_callback:
                        progress_callback(0.95)
                    
                    return timestamp_text
                
            except Exception as e:
                print(f"Whisper transcription failed: {str(e)}. Falling back to Google.")
            
            # Fallback to traditional speech recognition with Google
            try:
                recognizer = sr.Recognizer()
                chunk_length_ms = 30000
                chunks = []
                
                for i in range(0, len(audio), chunk_length_ms):
                    chunk = audio[i:i + chunk_length_ms]
                    chunks.append((i, chunk))
                
                transcript_with_timestamps = ""
                
                for i, (start_ms, chunk) in enumerate(chunks):
                    if progress_callback:
                        # Ensure progress stays within [0,1]
                        chunk_progress = min(0.95, 0.2 + (0.75 * i / len(chunks)))
                        progress_callback(chunk_progress)
                    
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        temp_path = temp_file.name
                        chunk.export(temp_path, format="wav")
                        
                        with sr.AudioFile(temp_path) as source:
                            audio_data = recognizer.record(source)
                            try:
                                text = recognizer.recognize_google(audio_data)
                                
                                start_seconds = start_ms / 1000
                                minutes = int(start_seconds // 60)
                                seconds = int(start_seconds % 60)
                                timestamp = f"[{minutes:02d}:{seconds:02d}] "
                                
                                transcript_with_timestamps += timestamp + text + " "
                                
                            except Exception as e:
                                print(f"Error in chunk {i}: {str(e)}")
                        
                        os.unlink(temp_path)
                
                if progress_callback:
                    progress_callback(0.98)
                
                return transcript_with_timestamps
                
            except Exception as e:
                return f"Error extracting text: {str(e)}"
    
    except Exception as e:
        print(f"Error in speech extraction: {str(e)}")
        return f"Error in speech extraction: {str(e)}"

def process_long_audio(audio_path: str, progress_callback=None) -> str:
    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_path)
        full_transcript = ""
        
        # Split into 30-second chunks
        chunk_length_ms = 30000
        chunks = [audio[i:i + chunk_length_ms] 
                 for i in range(0, len(audio), chunk_length_ms)]
        
        # Initialize Whisper model
        model = whisper.load_model("base")
        
        for i, chunk in enumerate(chunks):
            # Calculate progress (ensure it stays within 0.0 to 1.0)
            if progress_callback:
                progress = min(1.0, float(i) / max(1, len(chunks) - 1))
                progress_callback(progress)
            
            start_ms = i * chunk_length_ms
            
            # Create temp file for this chunk
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                chunk.export(temp_path, format="wav")
                
                try:
                    # Transcribe with Whisper
                    result = model.transcribe(
                        temp_path,
                        fp16=False,
                        language="en"
                    )
                    
                    # Add timestamp at the start of each chunk
                    start_seconds = start_ms / 1000
                    minutes = int(start_seconds // 60)
                    seconds = int(start_seconds % 60)
                    timestamp = f"[{minutes:02d}:{seconds:02d}] "
                    
                    chunk_transcript = timestamp + result["text"]
                    
                    # Add timestamps within the chunk for long segments
                    segments = chunk_transcript.split(". ")
                    timestamped_segments = []
                    
                    current_time = start_seconds
                    segment_time_estimate = len(chunk) / 1000 / max(1, len(segments))
                    
                    for j, segment in enumerate(segments):
                        if j > 0 and j % 3 == 0:  # Add timestamps every 3 sentences
                            current_time += segment_time_estimate * 3
                            minutes = int(current_time // 60)
                            seconds = int(current_time % 60)
                            new_timestamp = f"[{minutes:02d}:{seconds:02d}] "
                            timestamped_segments.append(new_timestamp + segment)
                        else:
                            timestamped_segments.append(segment)
                    
                    # Join segments back together
                    chunk_transcript = ". ".join(timestamped_segments)
                    if not chunk_transcript.endswith("."):
                        chunk_transcript += "."
                    
                    full_transcript += chunk_transcript + " "
                    
                except Exception as e:
                    print(f"Error processing chunk {i}: {str(e)}")
                    # If Whisper fails, add a placeholder
                    start_seconds = start_ms / 1000
                    minutes = int(start_seconds // 60)
                    seconds = int(start_seconds % 60)
                    timestamp = f"[{minutes:02d}:{seconds:02d}] "
                    
                    full_transcript += f"{timestamp}[Transcription unavailable for this segment] "
                
                # Clean up temp file
                os.unlink(temp_path)
        
        if progress_callback:
            progress_callback(1.0)
        
        return full_transcript
        
    except Exception as e:
        print(f"Error in long audio processing: {str(e)}")
        return f"Error in long audio processing: {str(e)}"

class CacheManager:
    """Unified cache manager for all types of searches and processing"""
    
    def __init__(self):
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different cache types
        self.audio_cache = self.cache_dir / "audio"
        self.transcript_cache = self.cache_dir / "transcript"
        self.search_cache = self.cache_dir / "search"
        
        self.audio_cache.mkdir(exist_ok=True)
        self.transcript_cache.mkdir(exist_ok=True)
        self.search_cache.mkdir(exist_ok=True)
    
    def get_cache_key(self, data_type: str, file_path: str, keywords: List[str] = None) -> str:
        """Generate a unique cache key based on file metadata and keywords"""
        file_stat = os.stat(file_path)
        base_info = f"{os.path.basename(file_path)}_{file_stat.st_size}_{file_stat.st_mtime}"
        
        if keywords:
            # Sort keywords to ensure consistent key regardless of order
            keyword_str = "_".join(sorted([k.lower().strip() for k in keywords]))
            cache_key = f"{base_info}_{keyword_str}"
        else:
            cache_key = base_info
            
        return md5(cache_key.encode()).hexdigest()
    
    def get_cache_path(self, data_type: str, cache_key: str) -> Path:
        """Get the appropriate cache file path based on data type"""
        if data_type == "audio":
            return self.audio_cache / f"{cache_key}.pkl"
        elif data_type == "transcript":
            return self.transcript_cache / f"{cache_key}.pkl"
        else:
            return self.search_cache / f"{cache_key}.pkl"
    
    def load_from_cache(self, data_type: str, cache_key: str):
        """Load data from cache if it exists"""
        cache_file = self.get_cache_path(data_type, cache_key)
        
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    data = pickle.load(f)
                    print(f"Cache hit for {data_type}: {cache_key}")
                    return data, True
            except Exception as e:
                print(f"Error loading from cache: {e}")
        
        return None, False
    
    def save_to_cache(self, data_type: str, cache_key: str, data) -> bool:
        """Save data to cache"""
        cache_file = self.get_cache_path(data_type, cache_key)
        
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
            print(f"Saved to {data_type} cache: {cache_key}")
            return True
        except Exception as e:
            print(f"Error saving to cache: {e}")
            return False

# Initialize cache manager at the top level
if 'cache_manager' not in st.session_state:
    st.session_state.cache_manager = CacheManager()

def process_files(folder_path: str, progress_bar) -> Dict:
    """Process all files in a folder with caching."""
    cache_manager = st.session_state.cache_manager
    processed_data = {}
    files = []
    
    # Collect all supported files
    for ext in ['.txt', '.srt', '.vtt', '.json', '.mp3', '.mp4', '.wav', '.m4a', '.png', '.jpg', '.jpeg']:
        files.extend(list(Path(folder_path).glob(f"*{ext}")))
    
    total_files = len(files)
    if total_files == 0:
        st.warning(f"No supported files found in {folder_path}. Please upload files to search.")
        return processed_data
    
    successful_count = 0
    for i, file in enumerate(files):
        try:
            # Update progress
            progress = min(0.99, (i + 1) / max(1, total_files))
            progress_bar.progress(progress, f"Processing file {i+1} of {total_files}: {file.name}")
            
            # Try to load from cache first
            cache_key = cache_manager.get_cache_key("file_process", str(file))
            cached_data, cache_hit = cache_manager.load_from_cache("transcript", cache_key)
            
            if cache_hit:
                processed_data[str(file)] = cached_data
                successful_count += 1
                continue
            
            # Process based on file type if not in cache
            file_ext = file.suffix.lower()
            
            if file_ext in ['.txt', '.srt', '.vtt', '.json']:
                with open(file, "r", encoding='utf-8') as f:
                    text = f.read()
                    if not text or len(text.strip()) < 10:
                        st.warning(f"File {file.name} appears to be empty or too short.")
                        continue
                    
                    file_data = {
                        "text": text,
                        "filename": file.name,
                        "type": "transcript",
                        "last_modified": os.path.getmtime(file)
                    }
                    processed_data[str(file)] = file_data
                    cache_manager.save_to_cache("transcript", cache_key, file_data)
                    successful_count += 1
                    
            elif file_ext in ['.mp3', '.wav', '.m4a']:
                try:
                    progress_bar.progress(progress, f"Analyzing audio in {file.name}...")
                    
                    def audio_progress_callback(audio_progress):
                        audio_progress = min(1.0, max(0.0, float(audio_progress)))
                        audio_overall_progress = min(0.99, progress + (audio_progress * 0.9 / total_files))
                        progress_bar.progress(audio_overall_progress, 
                                           f"Analyzing audio in {file.name}: {int(min(100, audio_progress * 100))}%")
                    
                    extracted_text = extract_text_from_audio(str(file), audio_progress_callback)
                    
                    if extracted_text and not extracted_text.startswith("Error"):
                        file_data = {
                            "text": extracted_text,
                            "filename": file.name,
                            "type": "audio_transcript",
                            "last_modified": os.path.getmtime(file)
                        }
                        processed_data[str(file)] = file_data
                        cache_manager.save_to_cache("transcript", cache_key, file_data)
                        st.success(f"✅ Successfully extracted text from audio: {file.name}")
                        successful_count += 1
                    else:
                        file_data = {
                            "text": f"Audio file: {file.name}\n{extracted_text if extracted_text else ''}",
                            "filename": file.name,
                            "type": "audio",
                            "last_modified": os.path.getmtime(file)
                        }
                        processed_data[str(file)] = file_data
                        cache_manager.save_to_cache("transcript", cache_key, file_data)
                        st.warning(f"⚠️ Could not fully extract text from {file.name}")
                        successful_count += 1
                except Exception as e:
                    st.error(f"Error analyzing audio {file.name}: {str(e)}")
                    file_data = {
                        "text": f"Audio file: {file.name}",
                        "filename": file.name,
                        "type": "audio",
                        "last_modified": os.path.getmtime(file)
                    }
                    processed_data[str(file)] = file_data
                    cache_manager.save_to_cache("transcript", cache_key, file_data)
                    successful_count += 1
            else:
                file_data = {
                    "text": f"File: {file.name}",
                    "filename": file.name,
                    "type": "other",
                    "last_modified": os.path.getmtime(file)
                }
                processed_data[str(file)] = file_data
                cache_manager.save_to_cache("transcript", cache_key, file_data)
                successful_count += 1
                
        except UnicodeDecodeError:
            st.error(f"Error processing {file.name}: File encoding not supported. Try converting to UTF-8.")
            continue
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
            continue
    
    progress_bar.progress(1.0, "Processing complete!")
    
    if successful_count == 0 and total_files > 0:
        st.error("Could not process any of the files. Please check file formats.")
    elif successful_count < total_files:
        st.warning(f"Processed {successful_count} out of {total_files} files. Some files had issues.")
        
    return processed_data

# Update the existing cache functions to use the new CacheManager
def get_audio_cache_key(file_path, keywords=None):
    return st.session_state.cache_manager.get_cache_key("audio", file_path, keywords)

def load_audio_from_cache(cache_key):
    return st.session_state.cache_manager.load_from_cache("audio", cache_key)

def save_audio_to_cache(cache_key, data):
    return st.session_state.cache_manager.save_to_cache("audio", cache_key, data)

def get_transcript_cache_key(file_path, keyword):
    return st.session_state.cache_manager.get_cache_key("transcript", file_path, [keyword])

def load_transcript_from_cache(cache_key):
    return st.session_state.cache_manager.load_from_cache("transcript", cache_key)

def save_transcript_to_cache(cache_key, data):
    return st.session_state.cache_manager.save_to_cache("transcript", cache_key, data)

# Main layout
st.markdown("""
<div class="logo-container">
    <div class="waves-container">
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
    </div>
    <h1 class="brand">AUCHIVE</h1>
    <div class="brand-accent">Find it fast. Play it faster.</div>
</div>
""", unsafe_allow_html=True)

# Two-column layout for upload and search
col1, col2 = st.columns(2)

# Upload section
with col1:
    st.subheader("Upload Audio")
    
    # Create a prominent, attention-grabbing upload instruction
    st.markdown("""
    <div style="background: #7B5AC4; padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem; text-align: center;">
        <p style="margin-bottom: 0; font-weight: bold;">👇 CLICK THE BUTTON BELOW TO SELECT FILES 👇</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Reset file uploader on each run to prevent caching issues
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0
    
    # Use a simpler file uploader with a consistent key and more file types
    uploaded_files = st.file_uploader(
        "Select audio files",
        type=["txt", "srt", "vtt", "json", "mp3", "mp4", "wav", "m4a"],
        accept_multiple_files=True,
        key=f"file_uploader_{st.session_state.uploader_key}"
    )
    
    # Process uploaded files
    if uploaded_files:
        # Make temp directory
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        # Clear any previous files
        for file in temp_dir.iterdir():
            if file.is_file():
                file.unlink()
        
        # Save files
        for uploaded_file in uploaded_files:
            file_path = temp_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        # Set folder path and show success
        folder_path = str(temp_dir)
        st.session_state.folder_path = folder_path
        
        # Show files with simple styling and appropriate icons
        st.success(f"✅ {len(uploaded_files)} files uploaded successfully")
        
        for file in uploaded_files:
            size_kb = round(file.size/1024, 1)
            
            # Choose appropriate icon based on file type
            file_ext = Path(file.name).suffix.lower()
            if file_ext in ['.mp3', '.wav', '.m4a']:
                icon = "🔊"  # Audio icon
            elif file_ext == '.mp4':
                icon = "🎬"  # Video icon
            else:
                icon = "📄"  # Document icon
                
            st.write(f"{icon} **{file.name}** - {size_kb} KB")
        
        # Add a clear button to reset uploads
        if st.button("Clear uploads"):
            st.session_state.uploader_key += 1
            st.rerun()
    elif st.session_state.get('folder_path'):
        # Use previously stored folder path if available
        folder_path = st.session_state.folder_path
        
        # Show reminder about previously uploaded files
        if os.path.isdir(folder_path):
            files = list(Path(folder_path).glob("*.*"))
            if files:
                st.info(f"Using {len(files)} previously uploaded files")
        else:
            st.warning("Previous upload folder not found. Please upload files again.")
            folder_path = None
            st.session_state.folder_path = None

# Keywords section
with col2:
    st.subheader("Search Keywords")
    
    # Simple keyword input
    keywords = st.text_input(
        "Enter keywords to search",
        st.session_state.keywords,
        placeholder="Enter keywords separated by commas"
    )
    st.session_state.keywords = keywords
    
    # Search button
    search_button = st.button("Search", use_container_width=True)

# Display search results
if search_button and keywords and folder_path:
    keyword_list = [k.strip() for k in keywords.split(',')]
    
    if not keyword_list:
        st.warning("Please enter at least one keyword.")
    else:
        # Process the folder first
        with st.spinner("Processing files..."):
            progress_bar = st.progress(0)
            processed_data = process_files(folder_path, progress_bar)
            
            if not processed_data:
                st.error("No files were processed successfully. Please check your files and try again.")
            else:
                st.subheader("Search Results")
                found_any_matches = False
                
                # Now search through the processed data
                for file_path in processed_data.keys():
                    data = processed_data[file_path]
                    text = data.get('text', '')
                    
                    if not text:
                        continue
                    
                    found_matches = False
                    matches_in_file = []
                    
                    # Search for each keyword
                    for keyword in keyword_list:
                        keyword_lower = keyword.lower()
                        text_lower = text.lower()
                        
                        # Find all matches
                        start = 0
                        while True:
                            index = text_lower.find(keyword_lower, start)
                            if index == -1:
                                break
                            
                            # Get context around match
                            context_start = max(0, index - 100)
                            context_end = min(len(text), index + len(keyword) + 100)
                            
                            # Get the actual matched text (preserving original case)
                            matched_text = text[index:index + len(keyword)]
                            context = text[context_start:context_end]
                            
                            # Find nearest timestamp before match
                            text_before = text[:index]
                            timestamp_match = re.findall(r'\[(\d{2}:\d{2})\]', text_before)
                            timestamp = timestamp_match[-1] if timestamp_match else "00:00"
                            
                            # Store match information
                            matches_in_file.append({
                                'keyword': keyword,
                                'matched_text': matched_text,
                                'context': context,
                                'timestamp': timestamp,
                                'position': index
                            })
                            
                            found_matches = True
                            found_any_matches = True
                            start = index + 1
                    
                    # If matches were found in this file, display them
                    if found_matches:
                        with st.expander(f"📄 {os.path.basename(file_path)} ({len(matches_in_file)} matches)", expanded=True):
                            # Sort matches by position in file
                            matches_in_file.sort(key=lambda x: x['position'])
                            
                            for i, match in enumerate(matches_in_file, 1):
                                # Get context parts
                                context = match['context']
                                keyword_pos = context.lower().find(match['matched_text'].lower())
                                before_match = context[:keyword_pos]
                                after_match = context[keyword_pos + len(match['matched_text']):]
                                
                                # Display match with styling
                                st.markdown(
                                    f"""
                                    <div style='background-color: white; padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #eee;'>
                                        <div style='color: #666; margin-bottom: 5px;'>
                                            <span style='background-color: #7B5AC4; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.9em;'>
                                                🕒 {match['timestamp']}
                                            </span>
                                            <span style='margin-left: 10px; color: #666;'>Match #{i} for "{match['keyword']}"</span>
                                        </div>
                                        <div style='font-family: monospace; line-height: 1.5; background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>
                                            {before_match}<mark style='background-color: #FFF59D; font-weight: bold; padding: 0 2px;'>{match['matched_text']}</mark>{after_match}
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                
                if not found_any_matches:
                    st.warning("No matches found for any of the keywords in any files.")
elif search_button and not folder_path:
    st.error("Please upload files before searching.")
elif search_button and not keywords:
    st.warning("Please enter keywords to search for.")

# Moved icons to bottom of page
st.markdown("<hr style='margin: 3rem 0 2rem 0; border: none; height: 1px; background-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)

# Add marketing copy here
st.markdown("""
<div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08); margin-bottom: 2rem; border: 1px solid rgba(255, 255, 255, 0.2);">
    <p style="font-family: 'Gotham', 'Gotham Medium', sans-serif; font-size: 1.1rem; line-height: 1.6; color: #2D3142; margin: 0; text-align: center;">
        AUCHIVE is built for audio producers who know the magic isn't just in making great radio—it's in being able to find it again. 
        Whether you're digging for the perfect moment to replay, pulling a clip for reference, or chasing a quote that aired years ago, 
        AUCHIVE lets you search your show's entire archive in seconds.
    </p>
</div>
""", unsafe_allow_html=True)

# Then update the feature icons HTML to use SVG white line drawings
st.markdown("""
<div class="feature-icons">
    <div class="feature-icon">
        <div class="icon-circle">
            <svg class="icon-svg" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
        </div>
        <div class="icon-label">Search</div>
    </div>
    <div class="feature-icon">
        <div class="icon-circle">
            <svg class="icon-svg" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <line x1="10" y1="9" x2="8" y2="9"></line>
            </svg>
        </div>
        <div class="icon-label">Find</div>
    </div>
    <div class="feature-icon">
        <div class="icon-circle">
            <svg class="icon-svg" viewBox="0 0 24 24">
                <polygon points="5,3 19,12 5,21"></polygon>
            </svg>
        </div>
        <div class="icon-label">Play</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Remove the experimental_rerun() call and replace with st.rerun()
if st.session_state.get('needs_rerun', False):
    st.session_state.needs_rerun = False
    st.rerun() 