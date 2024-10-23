import numpy as np
from scipy.io.wavfile import write

# DTMF frequency map (Low and High frequencies for each key)
dtmf_frequencies = {
    '1': (697, 1209),
    '2': (697, 1336),
    '3': (697, 1477),
    '4': (770, 1209),
    '5': (770, 1336),
    '6': (770, 1477),
    '7': (852, 1209),
    '8': (852, 1336),
    '9': (852, 1477),
    'asterisk': (941, 1209),
    '0': (941, 1336),
    'hashtag': (941, 1477)
}

def generate_dtmf_tone(key, duration=0.5, sample_rate=44100):
    """Generate a DTMF tone for the given key and save it as a WAV file."""
    if key not in dtmf_frequencies:
        raise ValueError(f"Invalid key: {key}. Must be one of {list(dtmf_frequencies.keys())}")
    
    low_freq, high_freq = dtmf_frequencies[key]
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Generate the tone by adding sine waves of both frequencies
    tone = np.sin(2 * np.pi * low_freq * t) + np.sin(2 * np.pi * high_freq * t)

    # Normalize the tone to the range [-32767, 32767] for WAV format
    tone = np.int16(tone / np.max(np.abs(tone)) * 32767)

    # Write the tone to a WAV file
    filename = f"dtmf_{key}.wav"
    write(filename, sample_rate, tone)
    print(f"Generated DTMF tone for '{key}' and saved as '{filename}'")

# Example usage: Generate all DTMF tones
for key in dtmf_frequencies:
    generate_dtmf_tone(key)
