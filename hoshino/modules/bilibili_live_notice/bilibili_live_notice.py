from hoshino import Service, priv
from hoshino.typing import CQEvent
from hoshino import aiorequests

sv_help = """
[订阅直播<url>] 订阅（仅限管理员）
""".strip()

sv = Service(
    name="B站开播公告",  # 功能名
    use_priv=priv.ADMIN,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_=sv_help,  # 帮助说明
)

guess_api_url = "https://api.live.bilibili.com/room/v1/Room/get_info_by_id?ids[]="


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


@sv.scheduled_job('cron', minute='*/3', second='10')
async def bilibili_live_notice():
    msg = ev.message.extract_plain_text().strip()
    result = await guess(msg)
    await bot.send(ev, result, at_sender=True)

