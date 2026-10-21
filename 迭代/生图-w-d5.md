# 生图 worker w-d5 工作记录

日期：2026-10-20
共享任务：task-6（已 claim → complete）

## 结果
- **入库 68 张**（另有 2 张 0303/0304 被其他 worker 抢先入库，也在我领到的批次内，已确认存在）
- 校验：我领到的 70 个 id 全部在 web/art/all/ 下存在，0 缺失
- 全程 0 张判 fail（唯一一次空返回 826 重试后成功）

## 批次
| 批次 | id 范围 | 结果 |
| --- | --- | --- |
| 1 | 298-307 | 8 张由我生成，303/304 已被他人入库 |
| 2 | 446-455 | 10/10 |
| 3 | 634-643 | 10/10 |
| 4 | 818-827 | 10/10（826 首次 exit=1，重试 30s 成功）|
| 5 | 1090-1099 | 10/10 |
| 6 | 1260-1269 | 10/10 |
| 7 | 1448-1457 | 10/10（队列清空）|

## 关键经验（给后续 worker）
1. **MCP 极慢**：mcp__wbimg__generate_image 前期 190-380s/张，且经常 300s 超时后整次 run 白跑。改走 CLI 后 23-33s/张，提速约 8 倍。
2. **并行无效**：同一次 Promise.all 发两张 MCP 请求，服务端仍串行（总耗时 = 两倍），不要指望并发。
3. **tmp 是共享目录**：web/art/tmp 所有 worker 共用，绝不能靠「ls 找最新文件」认领自己的图。必须输出到私有子目录 web/art/tmp/w-d5/，并用 CLI 返回 JSON 的 files[0]。
4. **编码**：wb_image.py 的 stdout 是 GBK，直接 bash 调用再手工把路径交给 finish 最稳；若用 Python subprocess 包裹，务必加 PYTHONIOENCODING=utf-8，否则中文路径解坏、finish 报 src missing。
5. **超时兜底**：把 CLI 调用夹在「调用前 ls 快照 → 调用后快照 diff」之间，私有子目录里新增的那唯一文件就是自己的图，可救回空返回的情况。
6. 每 10 张报一次进度给 lead，附 artqueue.py stats 的 done 数。

## 写范围
只写了 web/art/tmp/w-d5/**、data/claims/w-d5.json（脚本维护）、本文件。未触碰 web/index.html、web/data.js、pipeline/*.py、项目记录.md、杜诗星海.html；未跑 rebuild.py / 07_package.py。
