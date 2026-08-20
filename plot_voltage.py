"""Plot Keysight 34410A voltage-logging data with clearly visible variation."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd


TIME_COL = "Time (s)"
VOLT_COL = "Channel 1 (VDC)"


def find_columns(columns):
    time_col = next((c for c in columns if "time" in str(c).lower()), None)
    volt_col = next(
        (c for c in columns if "vdc" in str(c).lower() or "voltage" in str(c).lower()),
        None,
    )
    if time_col is None or volt_col is None:
        raise ValueError("找不到时间列或电压列，请检查输入文件")
    return time_col, volt_col


def load_input(path: Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() == ".xlsx":
        raw = pd.read_excel(path)
    else:
        raw = pd.read_csv(path)
    time_col, volt_col = find_columns(raw.columns)
    df = raw[[time_col, volt_col]].copy()
    df.columns = [TIME_COL, VOLT_COL]
    df[TIME_COL] = pd.to_datetime(df[TIME_COL])
    df[VOLT_COL] = pd.to_numeric(df[VOLT_COL], errors="coerce")
    return df.dropna()


def format_time_axis(ax):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=2))


def annotate_point(ax, x, y, text, y_offset):
    ax.annotate(
        text,
        (x, y),
        textcoords="offset points",
        xytext=(0, y_offset),
        ha="center",
        fontsize=9,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.7", alpha=0.9),
    )


def add_padding(ax, ratio=0.08):
    ymin, ymax = ax.get_ylim()
    span = max(ymax - ymin, 1e-6)
    ax.set_ylim(ymin - span * ratio, ymax + span * ratio)


def draw_trend_chart(df: pd.DataFrame, output: Path, label: str):
    series = df.set_index(TIME_COL)[VOLT_COL]
    minute_mean = series.resample("60s").mean().dropna()

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(series.index, series.values, color="#4c9fb5", linewidth=0.6, alpha=0.75, label="Raw samples")
    ax.plot(
        minute_mean.index,
        minute_mean.values,
        color="#c14953",
        linewidth=2.2,
        label="60s mean",
    )

    annotate_point(ax, series.index[0], series.iloc[0], f"start  {series.iloc[0]:.6f} V", 10)
    annotate_point(ax, series.index[-1], series.iloc[-1], f"end  {series.iloc[-1]:.6f} V", -16)

    ax.set_xlabel("Time")
    ax.set_ylabel("Voltage (V)")
    ax.set_title(f"{label} - Voltage Trend")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(frameon=False)
    format_time_axis(ax)
    add_padding(ax)
    fig.autofmt_xdate(rotation=0)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def draw_deviation_chart(df: pd.DataFrame, output: Path, label: str):
    series = df.set_index(TIME_COL)[VOLT_COL]
    base = series.iloc[0]
    dev_mv = (series - base) * 1000

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.fill_between(
        dev_mv.index,
        dev_mv.values,
        0,
        where=dev_mv.values <= 0,
        color="#c14953",
        alpha=0.22,
        linewidth=0,
    )
    ax.plot(dev_mv.index, dev_mv.values, color="#c14953", linewidth=1.1, label="Deviation")
    ax.axhline(0, color="gray", linewidth=1)

    annotate_point(ax, dev_mv.index[0], dev_mv.iloc[0], "0.000 mV", 10)
    annotate_point(ax, dev_mv.index[-1], dev_mv.iloc[-1], f"{dev_mv.iloc[-1]:.3f} mV", -16)

    ax.set_xlabel("Time")
    ax.set_ylabel("Deviation from start (mV)")
    ax.set_title(f"{label} - Voltage Change from Start")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(frameon=False)
    format_time_axis(ax)
    add_padding(ax)
    fig.autofmt_xdate(rotation=0)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def draw_minute_chart(df: pd.DataFrame, output: Path, label: str):
    series = df.set_index(TIME_COL)[VOLT_COL]
    mean = series.resample("60s").mean().dropna()
    std = series.resample("60s").std().dropna()

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.fill_between(
        mean.index,
        (mean - std).values,
        (mean + std).values,
        color="#4c9fb5",
        alpha=0.18,
        linewidth=0,
        label="60s mean ± std",
    )
    ax.plot(mean.index, mean.values, color="#2f6690", linewidth=2.4, label="60s mean")

    annotate_point(ax, mean.index[0], mean.iloc[0], f"{mean.iloc[0]:.6f} V", 10)
    annotate_point(ax, mean.index[-1], mean.iloc[-1], f"{mean.iloc[-1]:.6f} V", -16)

    ax.set_xlabel("Time")
    ax.set_ylabel("Voltage (V)")
    ax.set_title(f"{label} - One-Minute Average")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(frameon=False)
    format_time_axis(ax)
    add_padding(ax)
    fig.autofmt_xdate(rotation=0)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def draw_reference_chart(df: pd.DataFrame, output: Path, label: str):
    series = df.set_index(TIME_COL)[VOLT_COL]
    pad = (series.max() - series.min()) * 0.10

    fig, ax = plt.subplots(figsize=(4.8, 4.0))
    ax.plot(series.index, series.values, color="black", linewidth=0.9)
    ax.set_ylim(series.min() - pad, series.max() + pad)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.4f"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=4))
    ax.tick_params(labelsize=9)
    ax.set_xlabel("Time", fontsize=9)
    ax.set_ylabel("Voltage (V)", fontsize=9)
    if label:
        ax.set_title(label, fontsize=10)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def sanitize_label(label: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in label)
    return safe.strip("_") or "series"


def main():
    parser = argparse.ArgumentParser(description="Plot Keysight voltage logging data")
    parser.add_argument(
        "--input",
        type=Path,
        nargs="+",
        required=True,
        help="One or more Excel/CSV files",
    )
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument(
        "--label",
        nargs="*",
        default=[],
        help="Optional labels, one per input file",
    )
    args = parser.parse_args()

    if args.label and len(args.label) != len(args.input):
        parser.error("--label 数量必须和 --input 数量一致")

    args.output.mkdir(parents=True, exist_ok=True)
    multi = len(args.input) > 1

    for index, input_path in enumerate(args.input):
        label = args.label[index] if args.label else input_path.stem
        df = load_input(input_path)

        series = df.set_index(TIME_COL)[VOLT_COL]
        duration_min = (series.index.max() - series.index.min()).total_seconds() / 60
        change_mv = (series.iloc[-1] - series.iloc[0]) * 1000
        print(f"\n{label}: {input_path}")
        print(f"Samples: {len(df)}")
        print(f"Duration: {duration_min:.2f} min")
        print(f"Start: {series.iloc[0]:.6f} V | End: {series.iloc[-1]:.6f} V")
        print(f"Total change: {change_mv:+.3f} mV")

        prefix = sanitize_label(label)
        suffix = f"{prefix}_" if multi else ""
        draw_trend_chart(df, args.output / f"{suffix}voltage_trend.png", label)
        draw_deviation_chart(df, args.output / f"{suffix}voltage_deviation_mv.png", label)
        draw_minute_chart(df, args.output / f"{suffix}voltage_minute_average.png", label)
        draw_reference_chart(df, args.output / f"{suffix}voltage_line.png", label)

    print("\nCharts written to", args.output.resolve())


if __name__ == "__main__":
    main()
