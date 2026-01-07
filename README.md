# EDFPlotter

Small tool I created while writing my engineering thesis.
Allows you to render EDF files as pretty and reproducible plots which can be used in your LaTeX document.

## Usage

Run using uv
```bash
uv sync
uv run plotter.py config.toml
```

![Example](assets/example.png)

## Configuration

```toml
[general]
filename = "output.png"
trigger_ch_index = 0
data_ch_index = 1
time_limit_sec = 0.001
remove_offset = false
x_label = "Time (s)"
y_Label = "Amplitude (mV)"

[smoothing]
apply = true
window = 401
poly = 3

[visual]
line_width = 1.0

# Define input files
[[files]]
path = "measurements/signal_a.edf"
label = "Signal A"

[[files]]
path = "measurements/signal_b.edf"
label = "Signal B"
```
