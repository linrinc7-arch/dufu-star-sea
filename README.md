# 杜诗星海 · The Star Sea of Du Fu

一千四百六十八首杜甫诗，放进一片由代码算出来的天球。

课程作业：《走近大诗人》期末作业 · **题目二 方向C「诗歌数字化的技术实践」**

---

## 下载与使用

完整下载需要 Git 和 Git LFS：

```bash
git lfs install
git clone https://github.com/linrinc7-arch/dufu-star-sea.git
cd dufu-star-sea
git lfs pull
```

已有克隆先执行 `git pull --ff-only`，再执行 `git lfs pull`。如果图片或 ZIP 内容只有几行 LFS 指针文字，说明真实资源尚未下载。
打开 `交付/01_作品_杜诗星海.html` 使用单文件版；打开 `交付/05_全图库版/index.html` 使用完整配图版，必须保留其脚本和 art 子目录。
也可下载仓库中的 `杜诗星海_交付.zip` 实际文件，完整解压后打开作品。详细操作见 `交付/使用说明.txt`。

GitHub 文件列表右侧显示该文件或目录的最近提交说明，并非固定简介；各目录 README 提供中文用途与操作说明。

## 一、交付内容

```
交付/                        ← 提交目录（同时打成 杜诗星海_交付.zip）
  00_交付清单.md             作业要求 → 文件的对照表
  01_作品_杜诗星海.html       主件：双击即开，断网可用（约 10 MB）
  02_技术方法说明.docx        500—800 字
  03_经典文本关联说明.docx    300—500 字（杜甫 + 李白）
  04_数据说明/               4 张 CSV + README，可独立复核
  使用说明.txt               操作说明

交付/05_全图库版/               ← 本地完整图库版：1,468 首各配一图，约 280 MB（完整打包时包含在 ZIP 中）
```

## 二、工程结构

```
web/            源码：index.html 全部逻辑（单文件版由它内联打包而成）
                data.js 语料/坐标 · gloss2.js 全量注释 · annot.js 人工笺注
                imagery.js 意象词典（23 类 575 词） · collation.js 校记
                life.js + life_data.js 生平面板与行迹图 · shiyun_good.js 诗云甄选
                art/opt（精选 31 幅，内联进单文件） · art/all（全量 1,468 幅）
pipeline/       构建与检查
                01_build_corpus → 02_features → 02b_periods → 03_export_web
                04_bundle（打单文件） · 07_package（出交付目录 + zip）
                08_smoke（冒烟） · 10_export_data（导 CSV） · 11_shiyun（机器伪诗）
docs/           交付文档源文件（md）与成品（docx）、交付清单、课堂展示 PPT
data/           语料与中间数据：raw（全唐诗分片）/ build（特征、坐标）/ annot（笺注）
项目记录.md      决策与数据的完整来历（唯一事实来源）
DESIGN.md       视觉与交互设计说明
```

## 三、改完代码怎么重新出交付

```bash
python pipeline/04_bundle.py    # 单文件 → 根目录 杜诗星海.html
python pipeline/07_package.py --full # 出 交付/ 与 交付/05_全图库版/，并打包 zip
python pipeline/08_smoke.py     # 冒烟：headless 打开、点诗、确认诗卡出现
```

只改了 `web/index.html` 也必须跑一次 `04_bundle.py`，否则 `交付/` 里仍是旧件。

## 四、几个关键参数在哪改

| 要改什么 | 在哪 |
|---|---|
| 星的亮度 / 大小 / 旋臂形状 | `web/index.html`：`drawGalaxy`、`ZSCALE`、`RSCALE` |
| 星座连线阈值（0.26 边长） | `web/index.html` 搜 `0.26` |
| 配色 / 字号阶梯 | `web/index.html` 顶部 `:root` 与「字号阶梯」段 |
| 意象词典（23 类 575 词） | `web/imagery.js` |
| 注释与笺注文本 | `web/gloss2.js`、`web/annot.js` |

## 五、历史

迭代与决策记录见 `项目记录.md`；逐版差异见 `git log`。

打包注意：`07_package.py --full` 会重建交付目录；不加 --full 会生成精简包。修改说明时也需修改生成脚本，避免打包时还原旧文字。冒烟检查依赖 Windows Edge，不能代替全功能人工验收。
