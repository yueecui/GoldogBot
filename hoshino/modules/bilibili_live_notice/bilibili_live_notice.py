import os
import re

from hoshino import Service, priv
from hoshino import aiorequests
from hoshino.typing import CQEvent

from danteng import load_json, save_json, broadcast

sv_help = """
[订阅直播<url|room_id>] 订阅（仅限管理员）
[取消订阅<url|room_id>] 取消订阅（仅限管理员）
[订阅列表] 显示已订阅的直播
""".strip()

sv = Service(
    name="B站开播公告",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_=sv_help,  # 帮助说明
)

subs_path = os.path.join(os.path.dirname(__file__), 'subs.json')

_subscribes = load_json(subs_path)
_lives = []

# 循环_subscribes，将每个值都插入_lives
for k, v in _subscribes.items():
    _lives.append(v)

bililive_api_url = "https://api.live.bilibili.com/room/v1/Room/get_info_by_id?ids[]="
bililive_baseurl = "https://live.bilibili.com"


async def get_live_info(room_id):
    response = await aiorequests.get(bililive_api_url + room_id)
    response.raise_for_status()
    result = await response.json()
    try:
        return result['data'][room_id]
    except ValueError:
        return None


async def update_live_status(live: dict):
    room_info = await get_live_info(live['room_id'])
    if room_info is None:
        sv.logger.error(f'更新时，{live["room_id"]}直播间数据获取失败')
        return False
    latest_time = room_info['live_time']
    if latest_time != "0000-00-00 00:00:00" and live['latest_time'] != latest_time:
        live['latest_time'] = latest_time
        global _subscribes
        _subscribes[live['room_id']]['latest_time'] = latest_time
        save_json(_subscribes, subs_path)

        sv.logger.info(f'检测到{live["room_id"]}直播间开播了')
        await notice(live['room_id'],
                     f'====开播提醒====\n'
                     f'{room_info["uname"]}：【{room_info["area_v2_name"]}】{room_info["title"]}\n'
                     f'{bililive_baseurl}/{room_info["roomid"]}')


async def notice(room_id, msg):
    groups = _subscribes[str(room_id)]['subs_groups']
    await broadcast(msg, groups=groups)


@sv.scheduled_job('cron', minute='*/3', second='10')
async def bilibili_live_notice():
    for live in _lives:
        await update_live_status(live)


@sv.on_prefix("直播订阅")
@sv.on_prefix("订阅直播")
async def subscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有管理员可以使用此功能')
        return
    msg = ev.message.extract_plain_text().strip()
    if msg == '':
        return
    find = re.findall(r'(?:https?://live.bilibili.com/)?(\d+)\??.*', msg)
    if not find:
        await bot.finish(ev, '请输入正确的直播间链接或ID')
        return
    room_id = find[0]  # room_id是str
    room_info = await get_live_info(room_id)
    if room_info is None:
        await bot.finish(ev, '直播间不存在，请输入正确的直播间链接或ID')
        return

    global _subscribes
    if room_id not in _subscribes:
        _subscribes[room_id] = {
            "room_id": room_id,
            "uname": room_info["uname"],
            "latest_time": room_info["live_time"],
            "subs_groups": [],
        }
    gid = ev.group_id
    if gid in _subscribes[room_id]["subs_groups"]:
        await bot.finish(ev, f'本群已订阅直播间{room_id}的开播提醒')
    else:
        global _lives
        _subscribes[room_id]["subs_groups"].append(gid)
        _lives.append(_subscribes[room_id])
        save_json(_subscribes, subs_path)
        await bot.finish(ev, f'成功订阅直播间{room_id}（{room_info["uname"]}）的开播提醒')


@sv.on_prefix("取消直播订阅")
@sv.on_prefix("取消订阅")
async def cancel(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有管理员可以使用此功能')
        return
    msg = ev.message.extract_plain_text().strip()
    if msg == '':
        return
    find = re.findall(r'(?:https?://live.bilibili.com/)?(\d+)\??.*', msg)
    if not find:
        await bot.finish(ev, '请输入正确的直播间链接或ID')
        return
    room_id = find[0]  # room_id是str

    global _subscribes
    global _lives
    gid = ev.group_id

    if room_id not in _subscribes.keys() or gid not in _subscribes[room_id]['subs_groups']:
        await bot.finish(ev, f'本群没有订阅直播间{room_id}的开播提醒')
        return

    if len(_subscribes[room_id]['subs_groups']) == 1:  # 只有一个群订阅该直播
        for live in _lives[::-1]:
            if live['room_id'] == room_id:
                _lives.remove(live)
        del _subscribes[room_id]
        save_json(_subscribes, subs_path)
    else:
        _subscribes[room_id]['subs_groups'].remove(gid)
        save_json(_subscribes, subs_path)
    await bot.send(ev, f'成功取消直播间{room_id}的开播提醒')


@sv.on_keyword("订阅列表")
async def subs_list(bot, ev: CQEvent):
    if len(_subscribes.keys()) == 0:
        await bot.finish(ev, f'本群还未订阅任何主播的开播提醒')
        return
    result = ['本群订阅了以下主播的开播提醒：']
    for room_id in _subscribes.keys():
        result.append(f'{_subscribes[room_id]["room_id"]}（{_subscribes[room_id]["uname"]}）')
    await bot.send(ev, '\n'.join(result))
