#!/usr/bin/env python3
import argparse
import pandas as pd
import plotly.graph_objects as go

def main():
    parser = argparse.ArgumentParser(description="Plot robot data CSV using Plotly.")
    parser.add_argument("file", help="Path to robot_data.csv")
    args = parser.parse_args()

    # Load CSV with no header
    df = pd.read_csv(args.file, header=None, names=["stream", "timestamp", "value"])

    # Convert timestamps to numeric
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Build figure
    fig = go.Figure()

    # Create one trace per stream
    for stream_name, group in df.groupby("stream"):
        fig.add_trace(
            go.Scatter(
                x=group["timestamp"],
                y=group["value"],
                mode="lines+markers",
                name=stream_name
            )
        )

    fig.update_layout(
        title="Robot Telemetry Data",
        xaxis_title="Timestamp",
        yaxis_title="Value",
        hovermode="closest"
    )

    fig.show()

if __name__ == "__main__":
    main()
