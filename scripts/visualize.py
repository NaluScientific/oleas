import argparse
import os
from pathlib import Path
import pickle
import sys

import matplotlib.pyplot as plt
import numpy as np


def main():
    args = parse_args(sys.argv[1:])
    dir = Path(args.dir).resolve()
    watch = args.watch
    if not dir.exists() or not dir.is_dir():
        print("Input directory does not exist or is not a directory")

    fig = plt.figure(constrained_layout=True)
    fig.canvas.mpl_connect("close_event", lambda _: sys.exit(0))
    plt.ion()  # needed for redraw
    plt.show()
    try:
        last_file_plotted = None
        while True:
            latest_file = max(list(dir.glob("*")), key=os.path.getctime)
            if latest_file == last_file_plotted:
                plt.pause(1)  # let the window process events
                continue

            last_file_plotted = latest_file
            ATTEMPTS = 5
            for _ in range(ATTEMPTS):
                try:
                    plot_file(fig, latest_file)
                    break
                except Exception as e:
                    print(f"Failed to plot file: {latest_file} due to {e}")
                    plt.pause(0.4)

            if not watch:
                plt.ioff()
                plt.show()
                break
    except KeyboardInterrupt:
        print("Interrupted.")


def plot_file(fig, file: Path):
    """Plot a single file from the capture script output

    Args:
        fig: matplotlib figure
        file (Path): path to file
    """
    with open(file, "rb") as f:
        data = pickle.load(f)

    NUM_SETTINGS = len(data["corrected_data"])
    subfigs = fig.subfigures(nrows=NUM_SETTINGS, ncols=1)
    for setting, subfig in enumerate(subfigs):
        delay = data["delay"][setting]
        dac = data["dac"][setting]
        subfig.suptitle(f"Delay={delay}, DAC={dac:.03}")
        axs = subfig.subplots(nrows=1, ncols=3)
        for channel, ax in enumerate(axs):
            colors = plt.rcParams["axes.prop_cycle"].by_key()["color"][
                channel * 2 : channel * 2 + 2
            ]
            unaveraged_data = data["corrected_data"][setting]
            ax.plot(
                average_for_channel(unaveraged_data, channel=channel),
                label=f"Channel {channel}",
                color=colors[0],
            )
            ax.plot(
                average_for_channel(unaveraged_data, channel=channel + 4),
                label=f"Channel {channel + 4}",
                color=colors[1],
            )
            ax.set_title(f"Channels {channel}, {channel + 4}")

            if setting == 0:
                ax.legend()
            if setting == len(subfigs) - 1:
                ax.set_xlabel("Sample")
            if channel == 0:
                ax.set_ylabel("ADC Counts")

    fig.suptitle(f"{file.name}")
    plt.draw()


def average_for_channel(data: list[dict], channel: int):
    """Compute average of captures for a single channel"""
    return np.mean(np.array([x["data"][channel] for x in data]), axis=0)


def parse_args(argv):
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Plot data from capture script")
    parser.add_argument(
        "--dir", "-d", type=Path, required=True, help="Directory to plot from"
    )
    parser.add_argument(
        "--watch", "-w", action="store_true", help="Watch input directory for new data"
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    main()
