#!/usr/bin/env python3
"""
Interactive plotting tool for robot data logs.

This script reads CSV files created by DataLogger and creates interactive plots.
Requires matplotlib and optionally plotly for better interactivity.

Usage:
    python plot_data.py [log_file.csv]

If no file is specified, defaults to "robot_data.csv"
"""

import sys
import csv
import argparse
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
    import matplotlib

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not found. Install with: pip install matplotlib")

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    print("Info: plotly not found. Install with: pip install plotly for interactive plots")


def load_data(filename):
    """
    Load data from CSV file.

    Returns:
        dict: Dictionary mapping stream_name to list of (elapsed_time, dt, value) tuples
    """
    data = defaultdict(list)

    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stream_name = row['stream_name']
            elapsed_time = float(row['elapsed_time'])
            dt = float(row['dt'])
            value = float(row['value'])
            data[stream_name].append((elapsed_time, dt, value))

    return data


def plot_with_matplotlib(data, filename):
    """Create plots using matplotlib."""
    if not HAS_MATPLOTLIB:
        print("Error: matplotlib is required for plotting")
        return

    streams = sorted(data.keys())
    num_streams = len(streams)

    if num_streams == 0:
        print("No data streams found in file")
        return

    # Create subplots
    fig, axes = plt.subplots(num_streams, 1, figsize=(12, 4 * num_streams))
    if num_streams == 1:
        axes = [axes]

    fig.suptitle(f'Robot Data Log: {filename}', fontsize=14, fontweight='bold')

    for idx, stream_name in enumerate(streams):
        stream_data = data[stream_name]
        times = [t for t, _, _ in stream_data]
        values = [v for _, _, v in stream_data]

        axes[idx].plot(times, values, linewidth=1.5)
        axes[idx].set_xlabel('Elapsed Time (s)')
        axes[idx].set_ylabel('Value')
        axes[idx].set_title(f'Stream: {stream_name}')
        axes[idx].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_with_plotly(data, filename):
    """Create interactive plots using plotly."""
    if not HAS_PLOTLY:
        print("Error: plotly is required for interactive plotting")
        return

    streams = sorted(data.keys())
    num_streams = len(streams)

    if num_streams == 0:
        print("No data streams found in file")
        return

    # Create subplots
    fig = make_subplots(
        rows=num_streams,
        cols=1,
        subplot_titles=[f'Stream: {name}' for name in streams],
        vertical_spacing=0.1,
        shared_xaxes=True
    )

    for idx, stream_name in enumerate(streams):
        stream_data = data[stream_name]
        times = [t for t, _, _ in stream_data]
        values = [v for _, _, v in stream_data]

        fig.add_trace(
            go.Scatter(
                x=times,
                y=values,
                mode='lines',
                name=stream_name,
                line=dict(width=2)
            ),
            row=idx + 1,
            col=1
        )

    fig.update_layout(
        title_text=f'Robot Data Log: {filename}',
        title_x=0.5,
        height=300 * num_streams,
        showlegend=True
    )

    # Update x-axis labels
    for idx in range(num_streams):
        fig.update_xaxes(title_text='Elapsed Time (s)', row=idx + 1, col=1)
        fig.update_yaxes(title_text='Value', row=idx + 1, col=1)

    fig.show()


def main():
    parser = argparse.ArgumentParser(
        description='Plot robot data logs interactively'
    )
    parser.add_argument(
        'log_file',
        nargs='?',
        default='../robot_data.csv',
        help='Path to the CSV log file (default: robot_data.csv)'
    )
    parser.add_argument(
        '--backend',
        choices=['matplotlib', 'plotly', 'auto'],
        default='auto',
        help='Plotting backend to use (default: auto - uses plotly if available, else matplotlib)'
    )

    args = parser.parse_args()

    # Load data
    try:
        data = load_data(args.log_file)
    except FileNotFoundError:
        print(f"Error: File '{args.log_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    if not data:
        print("No data found in file")
        sys.exit(1)

    print(f"Loaded {len(data)} data stream(s): {', '.join(sorted(data.keys()))}")
    for stream_name, stream_data in data.items():
        print(f"  {stream_name}: {len(stream_data)} data points")

    # Choose plotting backend
    backend = args.backend
    if backend == 'auto':
        backend = 'plotly' if HAS_PLOTLY else 'matplotlib'

    # Create plots
    if backend == 'plotly' and HAS_PLOTLY:
        print("\nCreating interactive plot with plotly...")
        plot_with_plotly(data, args.log_file)
    elif backend == 'matplotlib' and HAS_MATPLOTLIB:
        print("\nCreating plot with matplotlib...")
        plot_with_matplotlib(data, args.log_file)
    else:
        print("Error: No plotting library available. Install matplotlib or plotly.")
        sys.exit(1)

if __name__ == '__main__':
    main()
