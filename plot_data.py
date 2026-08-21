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


def draw_chart(series_list, labels, ylabel, output):
    max_len = max(len(series) for series in series_list)
    y_min = min(series.min() for series in series_list)
    y_max = max(series.max() for series in series_list)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    if len(series_list) == 1:
        colors = ["black"]
    else:
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    for i, (series, label) in enumerate(zip(series_list, labels)):
        x = range(len(series))
        ax.plot(
            x,
            series.values,
            color=colors[i % len(colors)],
            linewidth=1.0,
            label=label,
        )

    pad = max((y_max - y_min) * 0.08, 1e-6)
    ax.set_ylim(y_min - pad, y_max + pad)
    ax.set_xlim(0, max_len * 1.02)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, integer=True))
    ticks = [t for t in ax.get_xticks() if 0 <= t <= max_len]
    ax.set_xticks(ticks)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(frameon=False, fontsize=9)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


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
    parser.add_argument("--output", type=Path, default=Path("output/data_chart.png"))
    args = parser.parse_args()

    files = discover_inputs(args.input)
    if args.label and len(args.label) != len(files):
        parser.error("--label 数量必须和文件数量一致")

    series_list = []
    labels = []
    ylabels = set()

    for i, file in enumerate(files):
        sheets = [None]
        if args.all_sheets and file.suffix.lower() in (".xlsx", ".xls"):
            sheets = pd.ExcelFile(file).sheet_names

        for sheet in sheets:
            label = args.label[i] if args.label else file.stem
            if len(sheets) > 1:
                label = f"{label} - {sheet}"
            df, ylabel = load_input(file, sheet_name=sheet)
            series_list.append(df.set_index(TIME_COL)[VALUE_COL])
            labels.append(label)
            ylabels.add(ylabel)
            print(f"{label}: {file} | {len(df)} samples | y-axis: {ylabel}")

    if len(ylabels) > 1:
        print("warning: 多个文件识别出的纵坐标不同:", sorted(ylabels))
    ylabel = next(iter(ylabels)) if len(ylabels) == 1 else "Value"

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    draw_chart(series_list, labels, ylabel, output)
    print("Chart written to", output.resolve())


if __name__ == "__main__":
    main()
