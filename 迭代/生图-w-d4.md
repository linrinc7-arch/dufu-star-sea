# 生图 worker w-d4 日志

队列：`python pipeline/artqueue.py`（共享任务 task-5）
产出目录：`web/art/all/<id 四位补零>.jpg`（768 宽）
本 worker 临时目录：`web/art/tmp/w-d4/`

## 工具与环境结论（重要）

1. **MCP `mcp__wbimg__generate_image` 已不可用**：8 个 worker 并发时单张 240s+，且常在 300s 触发 `Request timed out`（图其实已在后台生成，但客户端拿不到返回）。
2. **改用 CLI 直连**：`python "D:\Desktop\开放空间\wb_image.py" --prompt ... --size 1024x1536 --out <dir> --json`，同账号池、同模型 `gpt-image-2.5-sunburst`，实测 **28s/张**，约 8 倍提速。
3. **坑 1 — tmp 目录共享**：`web/art/tmp` 为全 worker 共用，不能靠「ls 最新文件」认领结果，会拿到别人的图。每个 worker 必须写自己的子目录，并直接使用 CLI 返回 JSON 的 `files[0]`。
4. **坑 2 — stdout 是 GBK**：用 Python `subprocess` 调用 CLI 时若按 UTF-8 解码，中文路径会被解坏，`finish` 报 `{"ok": false, "err": "src missing"}`（图其实已生成）。修法：子进程 env 设 `PYTHONIOENCODING=utf-8`。直接用 bash/pwsh 调 CLI 不触发此问题。

## 驱动脚本（均在 web/art/tmp/w-d4/，不入库）

- `drive.py <N>`：循环 `next 10` → 逐张 CLI 生成 → `finish`，直到累计 N 张。
- `runids.py <id,id,...>`：对当前 claims 文件里的指定 id 补做（换工具时清理遗留单）。

## 批次记录

| 批次 | id 区间 | 张数 | 失败 |
| --- | --- | --- | --- |
| 1 | 308-317 | 10 | 0 |
| 2 | 536-545, 730-739, 934-943 | 30 | 0 |
| 3 | 1106-1115, 1270-1279, 1390-1399 | 30 | 0 |

批 1 期间因 MCP 超时留下 4 张状态不明的图，已全部删除重生成，确保 id 与 prompt 严格对应。

注：313-317 在队列里 worker 字段最终显示为 w-s1/w-s3/w-s7 —— 共享队列 JSON 在 8 worker 并发下
save 存在互相覆盖，同一 id 会被重复认领。因为 prompt 是队列里按 id 固定下发的，重复认领不影响
图文对应关系，但 stats 按 worker 归因会少算这几张。
批 2 起全部走 CLI，驱动脚本串行，`OK <id>` 即入库成功。

## 质量

抽查 0308 / 0314 / 0536 / 0943：宋代水墨竖幅、墨色层次、大面积留白、人物为远景小像；未见文字、印章、签名、畸形。成品 768x1152，169-220 KB。

## 状态

- 本 worker 累计入库 **70 张**，0 失败（批 1 = 10，批 2 = 30，批 3 = 30）。
- 跑完时队列 pending 归零；全库 done=1455 / 1455 张成品，仅剩 11 条 claimed（在跑 worker 手上）+ 2 条 failed。
- 全程只写 `web/art/tmp/`、`data/claims/w-d4.json`、本文件。
