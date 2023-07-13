# -*- coding: utf-8 -*-
import os, sys, time
import asyncio, json
from loguru import logger
from pathlib import Path
from decouple import config, UndefinedValueError
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

PROMPT = '請你扮演一個檔案命名工具，我會以List的資料格式給予你許多的檔案名稱，你要將這些檔案名稱重新組合為 "節目名稱 S01E01" 這類的名稱，如果檔案名稱內有包含中文劇名請優先使用，如果沒有中文劇名的話請務必先線上查找中文劇名，如果檔案名稱看起來是劇場版或是特別篇就在劇名後面加上劇場版或是特別篇並以第0季來命名並，第幾季通常會以S1, S2之類的格式來辨別。 回答我的時候請只給予我重新組合的名稱不要有任何其他的字語。回答不要包含類似"好的，新的檔案名稱是"之類的詞語。單獨的把新的檔案名稱以List的資料格式給我。'

try:
    cookies = json.loads(
        open("bing_cookies/bing_cookies_1.json", encoding="utf-8").read()
    )
    logger.info("Cookies loaded")
except Exception as e:
    cookies = None
    logger.error(e)
    logger.info("No cookies loaded")


async def renamer_engine(series_list, proxy):
    while True:
        bot = None
        try:
            if proxy:
                logger.info(f"Proxy configured.")
                bot = await Chatbot.create(proxy=proxy, cookies=cookies)
            elif not proxy:
                logger.info(f"No proxy configured.")
                bot = await Chatbot.create()
        except Exception as e:
            logger.error(e)
            logger.error("Error occurred, try again later.")
            os._exit(0)

        try:
            # Passing cookies is "optional", as explained above
            initial_prompt = await bot.ask(
                prompt=PROMPT,
                conversation_style=ConversationStyle.precise,
                simplify_response=True,
            )

            renamer = await bot.ask(
                prompt=str(series_list),
                conversation_style=ConversationStyle.precise,
                simplify_response=True,
            )
            result = json.loads(renamer["text"].replace("'", '"'))
            await bot.close()
            break
        except Exception as e:
            logger.error(e)
            logger.error("Error occurred, try again later.")
            await bot.close()
            os._exit(0)
    logger.info(f"Fetching finished.")
    logger.warning(f"{renamer['messages_left']} Messages left.")
    logger.debug(f"Result: {result}")
    return result


def rename_series(series_list):
    try:
        proxy = config("PROXY")
    except UndefinedValueError:
        proxy = None
    logger.info(f"Fetching data from EdgeGPT...")
    result = asyncio.run(renamer_engine(series_list, proxy))
    return result
