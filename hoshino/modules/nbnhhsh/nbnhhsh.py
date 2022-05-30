from hoshino import Service, priv
from hoshino.typing import CQEvent
from hoshino import aiorequests

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
    if text == '':
        return ''
    response = await aiorequests.post(guess_api_url, json={"text": text})
    response.raise_for_status()
    result = await response.json()
    if type(result) == list and len(result) > 0:
        answer = [f'“{text}”']
        not_first = False
        if 'trans' in result[0] and len(result[0]['trans']) > 0:
            answer.append(f'经常是：' + '、'.join(result[0]['trans']))
            not_first = True
        if 'inputting' in result[0] and len(result[0]['inputting']) > 0:
            answer.append(f'{not_first and "，也" or ""}可能是：' + '、'.join(result[0]['inputting']))
            not_first = True
        if not_first:
            return ''.join(answer)
    return f'没有找到“{text}”的含义'


@sv.on_suffix("是什么意思？")
@sv.on_suffix("是什么意思?")
async def nbnhhsh(bot, ev: CQEvent):
    msg = ev.message.extract_plain_text().strip()
    result = await guess(msg)
    if result != '':
        await bot.send(ev, result, at_sender=True)

