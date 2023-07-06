# -*- coding: utf-8 -*-
import os, sys, time
import asyncio, json
from loguru import logger
from decouple import config, UndefinedValueError
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))


async def renamer_engine(series_list, proxy):
    while True:
        bot = None
        try:
            if proxy:
                logger.info(f"Proxy configured.")
                bot = await Chatbot.create(proxy=proxy)
            elif not proxy:
                logger.info(f"No proxy configured.")
                bot = await Chatbot.create()
        except Exception as e:
            logger.trace(e)
            logger.error("Error occurred, try again later.")
            os._exit(0)

        try:
            # Passing cookies is "optional", as explained above
            initial_prompt = await bot.ask(
                prompt='請你扮演一個檔案命名工具，我會以List的資料格式給予你許多的檔案名稱，你要將這些檔案名稱重新組合為 "節目名稱 S01E01" 這類的名稱，節目名稱通常會是中文。 回答我的時候請只給予我重新組合的名稱不要任何其他的字語。回答不要包含類似"好的，新的檔案名稱是"之類的詞語。單獨的把新的檔案名稱以List的資料格式給我。',
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
            logger.trace(e)
            await bot.close()
            continue
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
