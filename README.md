# DTMF Signal Generator with Sound and Adjustable Graph

This project generates **Dual-Tone Multi-Frequency (DTMF)** signals, simulating the sounds produced by pressing keys on a phone keypad. You can use the web-based interface to select keys, generate tones, and visualize the signal graph interactively.

### Features:
- **Web UI**: Built using Flask, with buttons created in JavaScript to allow interactive selection of phone keypad keys.
- **Sound Generation**: Uses the `sounddevice` library to generate real-time audio based on the DTMF frequencies for each key.
- **Interactive Graph**: Visualize the generated signals using `Plotly`, with adjustable time-domain and frequency-domain graphs.
- **Toot Toot Sound**: Each keypress produces the corresponding **DTMF tones**, giving an authentic phone keypad experience.

### Technologies Used:
- **Flask**: For serving the web-based interface.
- **JavaScript**: To handle button inputs and communicate with the server.
- **Sounddevice**: For generating the DTMF tones based on the selected keys.
- **Plotly**: To create dynamic and adjustable graphs for signal visualization.

### Demo:
![Demo](https://github.com/Vjay-7/DSP-PIT/blob/main/demo.gif)

Try it out and enjoy the sound of the **toot toot** tones!
