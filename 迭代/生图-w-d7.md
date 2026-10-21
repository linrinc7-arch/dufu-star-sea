# 生图 worker w-d7 日志（2026-10-20）

## 交付
共 **50 张**入库（目标 ≥40），全部为队列任务，按 prompt 原样出图，768 宽 jpg 存 web/art/all/。

- 第一批（MCP 期）：318-326、423-426
- 第二批（CLI）：660-663、698-701、788-791
- 第三批（CLI）：874-877、924-927、1022-1025、1072-1075
- 第四批（CLI）：1160-1163、1212-1215
- 收尾：1419（原 cli-nofile 失败项，重生成成功）

## 过程要点
- MCP（mcp__wbimg__generate_image）当时 3-5 分钟/张且频繁 300s 超时；中途遇到超时后图已落盘但路径丢失，故改用 CLI 直连 wb_image.py（约 22-40s/张）。
- wb_image.py stdout 为 GBK：调 CLI 时加 `PYTHONIOENCODING=utf-8`，用 JSON 里的 files[0] 绝对路径交给 finish，避免中文路径解坏报 src missing。
- 输出统一落在自建子目录 web/art/tmp/w-d7/，不与其它 worker 混。
- 批量用 `python pipeline/artbatch.py w-d7 N`（每轮领 4 张）；长时间前台调用可能被 540s 超时截断，剩余 claimed 项用单张 CLI 补完。

## 结果
最终 python pipeline/artqueue.py stats：done=1466 / 1468（其余 2 张由其它 worker 收尾），无我方遗留未完成项。
