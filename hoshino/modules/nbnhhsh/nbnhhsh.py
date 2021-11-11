import json
import os
import random

import hoshino

from hoshino import Service, priv
from hoshino.typing import CQEvent


sv_help = """
[<xxx>是什么意思？] 查询“能不能好好说话”释义网络缩写
""".strip()

sv = Service(
    name="能不能好好说话",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_=sv_help,  # 帮助说明
)

guess_api_url = "https://lab.magiconch.com/api/nbnhhsh/guess"


async def guess(text: str):

    z = 1


@sv.on_prefix("是什么意思？")
async def nbnhhsh(bot, ev: CQEvent):
    msg = ev.message.extract_plain_text().strip()
    z = 1
