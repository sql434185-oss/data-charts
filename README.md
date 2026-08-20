# Data Charts

一个轻量的数据绘图项目：放入 CSV 数据，自动生成变化明显、带数值标注的折线图、柱状图和变化率图。

## 数据格式

CSV 文件需要包含三列，第一行是表头：

| period | series | value |
| ------ | ------ | ----- |
| 2024Q1 | A      | 12    |
| 2024Q2 | A      | 18    |

- `period`：时间或分组维度，例如 `2024Q1`、`一月`
- `series`：系列名称，例如 `A`、`B`、`C`
- `value`：数值

项目自带示例数据：`data/sample_data.csv`

## 使用方法

```bash
pip install -r requirements.txt
python plot_charts.py --data data/sample_data.csv --output output
```

运行后会生成：

- `output/line_chart.png`：折线图，每个数据点带数值标注
- `output/bar_chart.png`：分组柱状图，柱顶带数值标注
- `output/change_chart.png`：相对第一个周期的变化率图，突出数据变化量

图表会自动调整纵轴范围，保证数值标注完整可见，并把相邻数据差异直观呈现出来。

## 万用表电压数据

Keysight 34410A 等仪器导出的 Excel/CSV 可以直接用专用脚本绘图，微小变化会被放大到容易看清的程度：

```bash
python plot_voltage.py --input "8.12，E1 0.xlsx" --label "E1 0"
```

多个文件可以一次批量出图，每个文件会生成带标签前缀的独立图表：

```bash
python plot_voltage.py --input "E1 0.xlsx" "E1 1.xlsx" --label "E1 0" "E1 1"
```

单文件运行后会生成：

- `output/voltage_trend.png`：完整电压趋势，叠加 60 秒平均线
- `output/voltage_deviation_mv.png`：相对起始值的毫伏变化
- `output/voltage_minute_average.png`：每分钟平均电压及波动范围
- `output/voltage_line.png`：黑白参考样式折线图，突出电压下降趋势

仓库内附带 `data/sample_voltage_minute.csv` 示例数据，可先跑一遍熟悉流程。

## 后续

之后会根据参考图进一步调整颜色、布局、标注和图表类型，并同步更新到本仓库。
