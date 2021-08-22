# Copyright (c) 2021 Itz-fork
# Part of: Nexa-Userbot
import logging
import asyncio
import os

from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.errors.exceptions.bad_request_400 import MessageIdInvalid

from nexa_userbot.core.nexaub_database.nexaub_db_conf import get_log_channel
from nexa_userbot.core.nexaub_database.nexaub_db_sudos import get_sudos
from nexa_userbot import NEXAUB
from config import Config


# ================= MAIN ================= #
# Log channel id
log_cid_loop = asyncio.get_event_loop()
LOG_CHANNEL_ID = log_cid_loop.run_until_complete(get_log_channel())

# Sudo users
SUDO_IDS = log_cid_loop.run_until_complete(get_sudos())
SUDO_IDS.append("me")


def add_handler(x_wrapper, nexaub_filter):
    NEXAUB.add_handler(MessageHandler(x_wrapper, filters=nexaub_filter), group=0)


async def e_or_r(nexaub_message, msg_text, parse_mode="md", disable_web_page_preview=True):
    message = nexaub_message
    le_sudos = SUDO_IDS
    if not message:
        return await message.edit(msg_text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    if not message.from_user:
        return await message.edit(msg_text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    if message.from_user.id in SUDO_IDS:
        if message.reply_to_message:
            return await message.reply_to_message.reply_text(msg_text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
        else:
            return await message.reply_text(msg_text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    else:
        return await message.edit(msg_text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)



def nexaub_on_cmd(
    command,
    modlue,
    admins_only: bool = False,
    only_pm: bool = False,
    only_groups: bool = False,
    no_sudos: bool = False
):
    if no_sudos:
        nexaub_filter = (filters.me & filters.command(command, Config.CMD_PREFIX) & ~filters.via_bot & ~filters.forwarded)
    else:
        nexaub_filter = (filters.user(SUDO_IDS) & filters.command(command, Config.CMD_PREFIX) & ~filters.via_bot & ~filters.forwarded)
    def decorate_nexaub(func):
        async def x_wrapper(client, message):
            nexaub_chat_type = message.chat.type
            if only_groups and nexaub_chat_type != "supergroup":
                await message.edit("`Is this even a group?`")
                return
            if only_pm and nexaub_chat_type != "private":
                await message.edit("`Yo, this command is only for PM!`")
                return
            try:
                await func(client, message)
            except MessageIdInvalid:
                logging.warning("Don't delete message while processing. It may crash the bot!")
            except BaseException as e:
                logging.error(f"\nModule - {modlue} | Command: {command}")
                error_text = f"""
**#ERROR**

**Module:** `{modlue}`
**Command:** `{Config.CMD_PREFIX + command}`
**Traceback:**
`{e}`

Forward this to @NexaUB_Support
"""
                if len(error_text) > 4000:
                    file = open("error_nexaub.txt", "w+")
                    file.write(error_text)
                    file.close()
                    await NEXAUB.send_document(LOG_CHANNEL_ID, "error_nexaub.txt", caption="`Error of Nexa Userbot`")
                    os.remove("error_nexaub.txt")
                else:
                    print(LOG_CHANNEL_ID)
                    await NEXAUB.send_message(chat_id=LOG_CHANNEL_ID, text=error_text)
        add_handler(x_wrapper, nexaub_filter)
        return x_wrapper
    return decorate_nexaub