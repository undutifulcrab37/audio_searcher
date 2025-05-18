
from setuptools import setup

APP = ['app_launcher.py']
DATA_FILES = [
    ('', ['app.py']),
    ('data/audio_cache', []),
    ('data/transcript_cache', [])
]
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'streamlit', 
        'pydub', 
        'speech_recognition', 
        'whisper',
        'numpy',
        'pathlib'
    ],
    'includes': [
        'streamlit.web',
        'streamlit.runtime',
        'streamlit.runtime.scriptrunner',
        're',
        'json',
        'datetime',
        'pickle',
        'tempfile',
        'io',
        'hashlib',
        'time'
    ],
    'iconfile': 'auchive_icon.icns',
    'plist': {
        'CFBundleName': 'AUCHIVE',
        'CFBundleDisplayName': 'AUCHIVE',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025',
        'CFBundleIdentifier': 'com.auchive.app',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name="AUCHIVE"
)
