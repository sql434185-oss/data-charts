"""Generate clear charts from a period/series/value CSV."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


EXPECTED_COLUMNS = {"period", "series", "value"}


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [str(col).strip().lower() for col in df.columns]
    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV 缺少列: {sorted(missing)}")
    if df["value"].isna().any():
        raise ValueError("CSV 中存在空值，请补全后再运行")
    return df


def add_value_labels(ax, x_positions, values, offset=0.02):
    for x, value in zip(x_positions, values):
        ax.annotate(
            f"{value:g}",
            (x, value),
            textcoords="offset points",
            xytext=(0, 6),
            ha="center",
            fontsize=9,
            fontweight="bold",
        )


def tighten_ylim(ax, values, ratio=0.12):
    ymin, ymax = ax.get_ylim()
    span = max(ymax - ymin, 1.0)
    ax.set_ylim(ymin, ymax + span * ratio)


def draw_line_chart(df: pd.DataFrame, output: Path):
    pivot = df.pivot(index="period", columns="series", values="value")
    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(pivot.index))
    for series in pivot.columns:
        values = pivot[series].astype(float)
        ax.plot(x, values, marker="o", linewidth=2.5, label=series)
        add_value_labels(ax, x, values)
    ax.set_xticks(list(x))
    ax.set_xticklabels(pivot.index)
    ax.set_xlabel("Period")
    ax.set_ylabel("Value")
    ax.set_title("Value Trend by Series")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(title="Series", frameon=False)
    tighten_ylim(ax, pivot.to_numpy().flatten())
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def draw_bar_chart(df: pd.DataFrame, output: Path):
    pivot = df.pivot(index="period", columns="series", values="value")
    periods = pivot.index
    series_list = list(pivot.columns)
    x = range(len(periods))
    width = 0.8 / len(series_list)

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, series in enumerate(series_list):
        values = pivot[series].astype(float)
        offsets = [pos + (i - (len(series_list) - 1) / 2) * width for pos in x]
        bars = ax.bar(offsets, values, width=width, label=series)
        add_value_labels(ax, offsets, values)
    ax.set_xticks(list(x))
    ax.set_xticklabels(periods)
    ax.set_xlabel("Period")
    ax.set_ylabel("Value")
    ax.set_title("Value Comparison by Series")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(title="Series", frameon=False)
    tighten_ylim(ax, pivot.to_numpy().flatten(), ratio=0.16)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def draw_change_chart(df: pd.DataFrame, output: Path):
    pivot = df.pivot(index="period", columns="series", values="value").astype(float)
    base = pivot.iloc[0]
    change = (pivot - base) / base * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(change.index))
    for series in change.columns:
        values = change[series]
        ax.plot(x, values, marker="s", linewidth=2.5, label=series)
        add_value_labels(ax, x, values, offset=0.5)
    ax.axhline(0, color="gray", linewidth=1, linestyle="-")
    ax.set_xticks(list(x))
    ax.set_xticklabels(change.index)
    ax.set_xlabel("Period")
    ax.set_ylabel("Change vs First Period (%)")
    ax.set_title("Change Rate by Series")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(title="Series", frameon=False)

    ymin, ymax = ax.get_ylim()
    span = max(ymax - ymin, 1.0)
    ax.set_ylim(ymin, ymax + span * 0.14)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Draw charts from period/series/value CSV")
    parser.add_argument("--data", type=Path, default=Path("data/sample_data.csv"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()

    df = load_data(args.data)
    args.output.mkdir(parents=True, exist_ok=True)

    draw_line_chart(df, args.output / "line_chart.png")
    draw_bar_chart(df, args.output / "bar_chart.png")
    draw_change_chart(df, args.output / "change_chart.png")
    print("Charts written to", args.output.resolve())


if __name__ == "__main__":
    main()
