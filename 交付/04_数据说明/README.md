# 数据说明

本目录是把《杜诗星海》的全部结论导出成可独立复核的表格，不依赖网页也能验证。

## 文件

| 文件 | 行数 | 说明 |
|---|---|---|
| dufu_poems.csv | 1,468 | 诗目总表：体裁、字数、句数、推定时期、主导意象、全文 |
| starfield_coords.csv | 1,468 | 每首诗在三维语义空间中的坐标（t-SNE 结果）与所属星团 |
| imagery_counts.csv | 约 3 万 | 十类意象词典在一首诗中的命中次数（长表，一行一个词） |
| clusters.csv | 8 | 星团汇总：大小、标签、代表意象 |

## 怎么复核

1. **统计类结论**：直接在 dufu_poems.csv 上筛选。例如「五律+七律 = 830 首」：
   筛 form 列等于 五言律诗 / 七言律诗，共 830 行。
2. **意象类结论**：在 imagery_counts.csv 里按 word 聚合。
   例如「月出现 236 次」，sum(count) where word='月'。
3. **空间类结论**：starfield_coords.csv 的 x/y/z 就是网页里星点的坐标。
   任意两点欧氏距离 = 它们在网页上的远近。
4. **时期是推定值**：period_id 由「地理意象直判 + 语义近邻补全」得到，
   不是学界编年。dufu_poems.csv 里 period_name 只是参考。

## 生成方式

全部由 pipeline/ 下的脚本从开源《全唐诗》语料重新算出，可完整复现：

    python pipeline/01_build_corpus.py    # 语料清洗
    python pipeline/02_features.py        # 特征、降维、聚类
    python pipeline/02b_periods.py        # 时期推定
    python pipeline/03_export_web.py      # 导出网页数据
    python pipeline/10_export_data.py     # 导出本目录
