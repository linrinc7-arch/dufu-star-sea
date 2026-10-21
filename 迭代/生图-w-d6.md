# 生图 w-d6 进度日志（完成）

- 11:21 基线 done=286, pending=1170；12:41 队列基本清空 done=1460/1468（pending=0, claimed=7）
- w-d6 累计交付 **90 张**，全部 finish ok，0 张 fail/重做：
  - 328-337, 355-357, 392-398, 482-491, 590-599, 774-783, 1000-1009, 1170-1179, 1306-1315, 1434-1443
- 前期 wbimg MCP 慢（175-242s/张，两次 300s 超时）；12:01 起按 lead 指示改 CLI wb_image.py，22-32s/张
- 输出目录固定 web/art/tmp/w-d6/（自有子目录），取 CLI JSON 的 files[0] 传 finish
- 质检：两张联系表（contact_40.jpg、contact_last50.jpg）人工看过，画风统一：宋人水墨山水、竖幅、大面积留白、人物远景不画面部，无文字/印章/签名/明显畸形

## 经验
- wbimg MCP 在 8 worker 并发下排队严重；CLI 直连稳定 25-30s
- CLI stdout 为 GBK；subprocess 必须 PYTHONIOENCODING=utf-8，否则中文路径损坏 → finish "src missing"
- 不要 ls 最新文件取图，用 files[0]
