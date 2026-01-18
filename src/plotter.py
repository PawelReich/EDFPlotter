from typing import Any

import pyedflib
import numpy as np
import matplotlib.pyplot as plt
import os
import argparse
import sys
from scipy.signal import savgol_filter
import tomllib

def load_config(config_path) -> dict[str, Any]:
    """Loads and returns the TOML configuration dictionary."""
    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Configuration file '{config_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Parsing TOML file failed: {e}")
        sys.exit(1)

def find_falling_edge(signal, threshold=None) -> int:
    if threshold is None:
        threshold = (np.max(signal) + np.min(signal)) / 2
    
    below_thresh = signal < threshold
    transitions = np.diff(below_thresh.astype(int)) 
    falling_edges = np.where(transitions == 1)[0]
    
    return falling_edges[0] if len(falling_edges) > 0 else 0

def process_edf_files(config : dict[str, Any]) -> None:
    gen_cfg = config.get('general', {})
    smooth_cfg = config.get('smoothing', {})
    vis_cfg = config.get('visual', {})
    file_list = config.get('files', [])

    plt.style.use('seaborn-v0_8-whitegrid') 
    fig_together, ax_together = plt.subplots(figsize=(10, 6))
    ax_together.set_xlabel(gen_cfg.get("x_label"))
    ax_together.set_ylabel(gen_cfg.get("y_label"))

    for item in file_list:
        file_path = item.get('path')
        label_text = item.get('label')

        if not os.path.exists(file_path):
            print(f"[ERROR] File not found: {file_path}")
            sys.exit(1)

        try:
            f = pyedflib.EdfReader(file_path)
            trigger_signal = f.readSignal(gen_cfg.get('trigger_ch_index', 0))
            data_signal = f.readSignal(gen_cfg.get('data_ch_index', 1))
            fs = f.getSampleFrequency(gen_cfg.get('data_ch_index', 1))
            f.close()
        except Exception as e:
            print(f"[ERROR] Parsing {file_path} failed: {e}")
            sys.exit(1)

        # Alignment
        trigger_idx = find_falling_edge(trigger_signal)
        aligned_data = data_signal[trigger_idx:]

        # Time limiting
        time_limit = gen_cfg.get('time_limit_sec')
        if time_limit:
            max_samples = int(time_limit * fs)
            if len(aligned_data) > max_samples:
                aligned_data = aligned_data[:max_samples]

        # Offset removal
        if gen_cfg.get('remove_offset', False) and len(aligned_data) > 0:
            print(f"[INFO] Removing offset: {aligned_data[0]} from {label_text}") 
            aligned_data = aligned_data - aligned_data[0]

        # Smoothing
        if smooth_cfg.get('apply', False) and len(aligned_data) > smooth_cfg.get('window', 401):
            aligned_data = savgol_filter(
                aligned_data, 
                smooth_cfg.get('window', 401), 
                smooth_cfg.get('poly', 3)
            )

        # Plotting
        time_axis = np.linspace(0, len(aligned_data)/fs, len(aligned_data)) * 1e6
        
        ax_together.plot(
            time_axis, 
            aligned_data, 
            label=label_text, 
            linewidth=vis_cfg.get('line_width', 1.0), 
            antialiased=True
        )

    ax_together.grid(True, linewidth=0.5)
    ax_together.legend(frameon=True)
    plt.tight_layout()

    output_filename = gen_cfg.get('filename', 'output.png')
    plt.savefig(output_filename)
    print(f"[INFO] Plot saved to: {output_filename}")

def main():
    parser = argparse.ArgumentParser(description="Small utility for plotting EDF files")
    parser.add_argument("config_file", help="Path to the .toml configuration file")
    
    args = parser.parse_args()
    
    cfg = load_config(args.config_file)
    process_edf_files(cfg)

if __name__ == "__main__":
    main()
