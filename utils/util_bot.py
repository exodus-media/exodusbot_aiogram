import asyncio
import logging
from aiogram.utils import exceptions

from loader import bot

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')


async def send_message(user_id: int, text: str, disable_web_page_preview: bool = True) -> bool:
    try:
        await bot.send_message(user_id, text, disable_web_page_preview=disable_web_page_preview)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False