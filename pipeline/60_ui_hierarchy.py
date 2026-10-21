# -*- coding: utf-8 -*-
"""60_ui_hierarchy.py — 界面层级：非当前章节只留编号；图例默认收起"""
import os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("这一轮的层级改动已落在 web/index.html：")
print("  1. .sb span 默认 max-height:0，只在 :hover / .on 展开")
print("  2. #legend 默认 .collapsed，底部 #lgtog 切换")
print("  3. 长诗卡两句一行（.row）")
