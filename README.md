# Data Charts

一键把多个 Excel/CSV 数据表画成一张实际数据图，纵坐标和图例会按数据自动识别。

## 快速绘图

安装依赖：

```bash
pip install -r requirements.txt
```

画一个文件：

```bash
python plot_data.py --input "8.12，E1 0.xlsx" --label "E1 0" --step 0.0005
```

`--step` 是纵轴相邻刻度之间的数值距离（默认 `0.001`），例如 `0.0005`、`0.0001`；数值距离越小，比例越精细，数据变化越明显。`--precision` 可以单独指定小数位数，默认会根据 `--step` 自动计算。

同时画多个文件：

```bash
python plot_data.py --input "E1 0.xlsx" "E1 1.xlsx" --label "E1 0" "E1 1"
```

直接导入整个文件夹：

```bash
python plot_data.py --input data
```

Excel 每个工作表都画成一条线：

```bash
python plot_data.py --input "数据.xlsx" --all-sheets
```

## 自动识别

- 纵坐标：根据数据列名自动识别，例如 `Voltage (V)`、`Current (A)`、`Temperature (C)`
- 图例：默认使用文件名；Excel 多表使用“文件名 - 表名”，也可以用 `--label` 指定
- 横坐标：按采样点序号显示，从 `0` 到数据总数，末尾留一点余量
- 精度：用 `--step` 手动设置纵轴刻度间的数值距离，用 `--precision` 可选设置小数位数

## 输出

- `output/data_chart.png`：合并后的实际数据图

## 在另一台电脑上运行（VSCode）

1. 安装 Python 3.10 或更高版本，安装时勾选 `Add Python to PATH`
2. 获取项目源码：GitHub 页面点击 `Code` -> `Download ZIP` 并解压，或 `git clone https://github.com/sql434185-oss/data-charts.git`
3. 用 VSCode 打开项目文件夹
4. 创建虚拟环境：`python -m venv .venv`
5. 激活环境并安装依赖：
   - Windows：`.venv\Scripts\activate`
   - macOS / Linux：`source .venv/bin/activate`
   - 然后执行 `pip install -r requirements.txt`
6. 在 VSCode 终端运行绘图命令，例如 `python plot_data.py --input "你的数据.xlsx"`
7. 图片生成在 `output/data_chart.png`
