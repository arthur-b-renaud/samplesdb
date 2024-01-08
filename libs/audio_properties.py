import librosa
from pydub.utils import mediainfo
import soundfile as sf


def get_audio_properties(file_path):
    # Load the audio file
    y, sr = librosa.load(file_path, sr=None)  # Load with its original sampling rate

    # Getting the duration in seconds
    duration_secs = int(librosa.get_duration(y=y, sr=sr))

    # Get BPM (tempo)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # Get media info for additional properties
    info = mediainfo(file_path)

    # Get other properties
    bitrate_bps = int(info['bit_rate'])
    nb_channels = int(info['channels'])
    try:
        bit_depth = int(sf.info(file_path).subtype.split('_')[1])
    except ValueError:
        bit_depth = None # This is the case when the file is mp3 first
    rates_hz = sr

    return {
        "bpm": tempo,
        "rates_hz": rates_hz,
        "bitrate_bps": bitrate_bps,
        "nb_channels": nb_channels,
        "bit_depth": bit_depth,
        "duration_secs": duration_secs
    }