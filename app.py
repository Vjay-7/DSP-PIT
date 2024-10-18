from flask import Flask, render_template, jsonify, request
import numpy as np
from scipy.fft import fft, fftfreq
import plotly.graph_objs as go
import plotly.io as pio
import sounddevice as sd
import wave
import io
import base64

app = Flask(__name__)


dtmf_frequencies = {
    '1': (697, 1209), '2': (697, 1336), '3': (697, 1477),
    '4': (770, 1209), '5': (770, 1336), '6': (770, 1477),
    '7': (852, 1209), '8': (852, 1336), '9': (852, 1477),
    '*': (941, 1209), '0': (941, 1336), '#': (941, 1477)
}


def read_wav_file(filepath):
    import wave

    with wave.open(filepath, 'rb') as wf:
        n_channels = wf.getnchannels()
        fs = wf.getframerate()
        n_samples = wf.getnframes()
        signal = wf.readframes(n_samples)
        signal = np.frombuffer(signal, dtype=np.int16)
        if n_channels > 1:
            signal = signal[::n_channels]  
    return signal, fs

# Function to generate DTMF signal for a key
def generate_dtmf_tone(key, duration=0.5, fs=8000):
    f_low, f_high = dtmf_frequencies[key]
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    signal = np.sin(2 * np.pi * f_low * t) + np.sin(2 * np.pi * f_high * t)
    return signal, t, f_low, f_high

# Function to perform FFT and return frequencies and magnitudes
def compute_fft(signal, fs):
    N = len(signal)
    yf = fft(signal)
    xf = fftfreq(N, 1 / fs)[:N // 2]
    magnitude = 2.0 / N * np.abs(yf[:N // 2])
    return xf, magnitude


def play_sound(signal, fs=8000):
    sd.play(signal, samplerate=fs)
    sd.wait()  # Wait until sound is played


def create_plotly_plot(x, y, title, x_label, y_label):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=title))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode="x unified",
        template="plotly_white"
    )
    return pio.to_json(fig)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play_key', methods=['POST'])
def play_key():
    data = request.json
    key = data.get('key')
    
    # Generate DTMF tone for the selected key
    signal, t, f_low, f_high = generate_dtmf_tone(key)
    
    # Play the sound
    play_sound(signal)

    return jsonify({"status": "success", "message": f"Playing sound for key {key}", "frequencies": (f_low, f_high)})

@app.route('/analyze_key', methods=['POST'])
def analyze_key():
    data = request.json
    key = data.get('key')
    
   
    signal, t, f_low, f_high = generate_dtmf_tone(key)

  
    fs = 8000
    xf, magnitude = compute_fft(signal, fs)


    time_domain_plot = create_plotly_plot(t[:100], signal[:100], f"Time-Domain Signal for Key '{key}'", "Time [s]", "Amplitude")
    
  
    freq_domain_plot = create_plotly_plot(xf, magnitude, f"Frequency-Domain Spectrum for Key '{key}'", "Frequency [Hz]", "Magnitude")
 
    low_signal = np.sin(2 * np.pi * f_low * t)
    high_signal = np.sin(2 * np.pi * f_high * t)
    combined_signal = (low_signal + high_signal) / 2

    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t[:200], y=low_signal[:200], mode='lines', name='Low Frequency (Blue)', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=t[:200], y=high_signal[:200], mode='lines', name='High Frequency (Red)', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=t[:200], y=combined_signal[:200], mode='lines', name='Combined (Green)', line=dict(color='green')))
    fig.update_layout(
        title=f"Sine Wave Representation for Key '{key}'",
        xaxis_title="Time [s]",
        yaxis_title="Amplitude",
        hovermode="x unified",
        template="plotly_white"
    )
    combined_plot = pio.to_json(fig)

    # Identify DTMF keys with the same frequencies
    identified_keys = [k for k, v in dtmf_frequencies.items() if v == (f_low, f_high)]
    
    return jsonify({
        'time_domain_plot': time_domain_plot,
        'freq_domain_plot': freq_domain_plot,
        'combined_plot': combined_plot,
        'identified_key': identified_keys,
        'frequencies': (f_low, f_high)
    })

    
@app.route('/analyze_file', methods=['POST'])
def analyze_file():
    try:
        file = request.files['file']
        filepath = './uploaded.wav'
        file.save(filepath)

        # Read WAV file
        signal, fs = read_wav_file(filepath)

        # Perform FFT
        xf, magnitude = compute_fft(signal, fs)

        
        peak_indices = np.argsort(magnitude)[-2:]  
        identified_freqs = xf[peak_indices]

        
        identified_keys = []
        for freq in identified_freqs:
            for key, (f_low, f_high) in dtmf_frequencies.items():
                if np.isclose(freq, f_low, atol=20) or np.isclose(freq, f_high, atol=20):
                    identified_keys.append(key)

       
        freq_domain_plot = create_plotly_plot(xf, magnitude, "Frequency Spectrum from File", "Frequency [Hz]", "Magnitude")

        return jsonify({
            'freq_domain_plot': freq_domain_plot,
            'identified_keys': identified_keys
        })
    except Exception as e:
      
        print(f"Error analyzing file: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
