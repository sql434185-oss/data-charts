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

## 后续

拿到真实数据和参考图后，会按目标图例调整颜色、布局、标注和图表类型，并同步更新到本仓库。
