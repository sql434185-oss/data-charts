"""Plot one or more data tables onto one chart with auto-detected labels."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd


TIME_COL = "Time (s)"
VALUE_COL = "Value"

SUPPORTED_SUFFIXES = {".xlsx", ".xls", ".csv"}

CJK_FONTS = (
    "Microsoft YaHei",
    "SimHei",
    "PingFang SC",
    "Noto Sans CJK SC",
    "WenQuanYi Zen Hei",
)

Y_LABELS = {
    "vdc": "Voltage (V)",
    "voltage": "Voltage (V)",
    "volt": "Voltage (V)",
    "current": "Current (A)",
    "amp": "Current (A)",
    "temp": "Temperature (C)",
    "power": "Power (W)",
    "watt": "Power (W)",
}


def configure_fonts():
    available = {font.name for font in fm.fontManager.ttflist}
    for name in CJK_FONTS:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name] + plt.rcParams["font.sans-serif"]
            break
    plt.rcParams["axes.unicode_minus"] = False


def discover_inputs(paths):
    files = []
    for path in paths:
        path = Path(path)
        if path.is_dir():
            found = [p for p in path.rglob("*") if p.suffix.lower() in SUPPORTED_SUFFIXES]
            files.extend(sorted(found))
        else:
            files.append(path)
    if not files:
        raise ValueError("没有找到任何 Excel/CSV 文件")
    return files


def find_columns(raw):
    columns = [str(c).strip() for c in raw.columns]
    time_col = next((c for c in columns if "time" in c.lower()), None)
    if time_col is None:
        raise ValueError("找不到时间列（列名需要包含 time）")
    candidates = [c for c in columns if c != time_col]
    for keyword in Y_LABELS:
        match = next((c for c in candidates if keyword in c.lower()), None)
        if match:
            return time_col, match
    numeric = [c for c in candidates if pd.api.types.is_numeric_dtype(raw[c])]
    if not numeric:
        raise ValueError("找不到数值数据列")
    return time_col, numeric[0]


def detect_ylabel(column):
    text = str(column).strip()
    lower = text.lower()
    for keyword, label in Y_LABELS.items():
        if keyword in lower:
            return label
    return text


def load_input(path, sheet_name=None):
    path = Path(path)
    if path.suffix.lower() in (".xlsx", ".xls"):
        raw = pd.read_excel(path, sheet_name=sheet_name if sheet_name is not None else 0)
    else:
        raw = pd.read_csv(path)
    time_col, value_col = find_columns(raw)
    df = raw[[time_col, value_col]].copy()
    df.columns = [TIME_COL, VALUE_COL]
    df[TIME_COL] = pd.to_datetime(df[TIME_COL], errors="coerce")
    df[VALUE_COL] = pd.to_numeric(df[VALUE_COL], errors="coerce")
    return df.dropna(), detect_ylabel(value_col)


def sanitize_label(label):
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in label)
    return safe.strip("_") or "series"


def draw_single_chart(series, label, ylabel, step, precision, height, output):
    y_min = float(series.min())
    y_max = float(series.max())
    n = len(series)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(range(n), series.values, color="black", linewidth=1.0, label=label)

    pad = max((y_max - y_min) * 0.08, 1e-6)
    ax.set_ylim(y_min - pad, y_max + pad)
    ax.set_xlim(0, n * 1.02)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, integer=True))
    xticks = [t for t in ax.get_xticks() if 0 <= t <= n]
    ax.set_xticks(xticks)

    if step is None:
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=6))
    else:
        ax.yaxis.set_major_locator(mticker.MultipleLocator(step))
    yticks = ax.get_yticks()
    used_step = (
        float(yticks[1] - yticks[0]) if len(yticks) > 1 else (y_max - y_min) / 6
    )
    decimals = precision if precision is not None else auto_decimals(used_step)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter(f"%.{decimals}f"))

    if height is None:
        visible_ticks = [t for t in yticks if y_min - pad <= t <= y_max + pad]
        height = max(6.0, min(16.0, 1.2 + max(len(visible_ticks) - 1, 1) * 0.55))
    fig.set_size_inches(9, height)

    ax.set_xlabel("Time (s)")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(frameon=False, fontsize=9)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def auto_decimals(step):
    text = format(step, ".12f").rstrip("0")
    if "." in text:
        return len(text.split(".")[1])
    return 0


def main():
    configure_fonts()
    parser = argparse.ArgumentParser(description="Plot one or more data tables")
    parser.add_argument(
        "--input",
        nargs="+",
        required=True,
        help="Excel/CSV files or folders containing data tables",
    )
    parser.add_argument(
        "--label",
        nargs="*",
        default=[],
        help="Legend labels, one per input file",
    )
    parser.add_argument(
        "--all-sheets",
        action="store_true",
        help="Treat every sheet in each Excel file as a separate series",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Output folder (or a PNG file when plotting a single table)",
    )
    parser.add_argument(
        "--step",
        type=float,
        default=None,
        help="Numeric distance between y-axis ticks; auto when omitted",
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=None,
        help="Optional decimal places for y-axis labels; auto when omitted",
    )
    parser.add_argument(
        "--height",
        type=float,
        default=None,
        help="Figure height in inches; auto-adjusted when omitted",
    )
    args = parser.parse_args()

    if args.step is not None and args.step <= 0:
        parser.error("--step 必须是正数")

    files = discover_inputs(args.input)
    if args.label and len(args.label) != len(files):
        parser.error("--label 数量必须和文件数量一致")

    output = Path(args.output)
    if output.suffix.lower() == ".png":
        if len(files) != 1 or args.all_sheets:
            parser.error("--output 指定为 PNG 时只能用于单个数据表")
        output.parent.mkdir(parents=True, exist_ok=True)
    else:
        output.mkdir(parents=True, exist_ok=True)

    for i, file in enumerate(files):
        sheets = [None]
        if args.all_sheets and file.suffix.lower() in (".xlsx", ".xls"):
            sheets = pd.ExcelFile(file).sheet_names

        for sheet in sheets:
            label = args.label[i] if args.label else file.stem
            if len(sheets) > 1:
                label = f"{label} - {sheet}"
            df, ylabel = load_input(file, sheet_name=sheet)
            series = df.set_index(TIME_COL)[VALUE_COL]

            if output.suffix.lower() == ".png":
                chart_path = output
            else:
                chart_path = output / f"{sanitize_label(label)}_chart.png"

            draw_single_chart(
                series,
                label,
                ylabel,
                args.step,
                args.precision,
                args.height,
                chart_path,
            )
            print(f"{label}: {file} | {len(df)} samples | y-axis: {ylabel}")
            print(f"Chart written to {chart_path.resolve()}")


if __name__ == "__main__":
    main()
