import json

import nonebot
from hoshino.log import new_logger
from hoshino.service import Service

import asyncio
from aiocqhttp.exceptions import ActionFailed

logger = new_logger('Danteng', debug=False)


def save_json(config: dict, path: str):
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        logger.error(ex)
        return False


def load_json(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except Exception as ex:
        logger.error(f'读取Json文件"{path}"发生错误：{ex}')
        # logger.exception(ex)
        return {}


async def broadcast(msg, groups=None, sv_name=None):
    bot = nonebot.get_bot()
    # 当groups指定时，在groups中广播；当groups未指定，但sv_name指定，将在开启该服务的群广播
    svs = Service.get_loaded_services()
    if not groups and sv_name not in svs:
        raise ValueError(f'不存在服务 {sv_name}')
    if sv_name:
        enable_groups = await svs[sv_name].get_enable_groups()
        send_groups = enable_groups.keys() if not groups else groups
    else:
        send_groups = groups
    for gid in send_groups:
        try:
            await bot.send_group_msg(group_id=gid, message=msg)
            logger.info(f'群{gid}投递消息成功')
            await asyncio.sleep(0.5)
        except ActionFailed as e:
            logger.error(f'在群{gid}投递消息失败，retcode={e.retcode}')
        except Exception as e:
            logger.exception(e)
