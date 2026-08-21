# Data Charts

一个 Excel/CSV 数据表生成一张独立图片，纵坐标、图例和精度默认自动识别，坐标轴长度会自动调节，避免刻度拥挤。

## 快速绘图

安装依赖：

```bash
pip install -r requirements.txt
```

画一个文件：

```bash
python plot_data.py --input "8.12，E1 0.xlsx" --label "E1 0"
```

同时画多个文件，每个文件生成一张独立图片：

```bash
python plot_data.py --input "E1 0.xlsx" "E1 1.xlsx"
```

直接导入整个文件夹，自动为里面每个数据表出图：

```bash
python plot_data.py --input data
```

Excel 每个工作表也分别生成一张图：

```bash
python plot_data.py --input "数据.xlsx" --all-sheets
```

## 自动识别与自动调节

- 纵坐标：根据数据列名自动识别，例如 `Voltage (V)`、`Current (A)`、`Temperature (C)`
- 图例：默认使用文件名；Excel 多表使用“文件名 - 表名”，也可以用 `--label` 指定
- 横坐标：按采样点序号显示，从 `0` 到数据总数，末尾留一点余量
- 精度：`--step` 不填时自动选择刻度间距，`--precision` 不填时自动匹配小数位数
- 高度：`--height` 不填时根据刻度数量自动调整图片高度，避免刻度拥挤；也可以手动指定，例如 `--height 8`

## 输出

- 默认输出到 `output/` 文件夹
- 每个数据表生成 `output/文件名_chart.png`，例如 `output/E1_0_chart.png`

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
7. 图片生成在 `output/` 文件夹，每个数据表对应一张
