import sys
import asyncio
import telepot
from telepot.async.delegate import per_chat_id, create_open
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent

import dataset
import pickle

import stackexchange

import config

# From stackoverflow: http://stackoverflow.com/questions/3398852/using-python-remove-html-tags-formatting-from-a-string
import re
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

# class NotStackOverflowBot(telepot.async.helper.ChatHandler):
#     def __init__(self, seed_tuple, timeout):
#         super(NotStackOverflowBot, self).__init__(seed_tuple, timeout)
so = stackexchange.Site(stackexchange.StackOverflow, config.STACKOVERFLOW_KEY)
so.be_inclusive()


async def on_chat_message(bot, msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if "/help" in msg['text']:
        await bot.sender.sendMessage(
            chat_id,
            """This bot is currently in ALPHA.

            It will eventually search for stackoverflow questions in chat using a simple AI engine (Mycroft's Adapt)
            """)
    else:
        results = so.search(intitle=msg['text'])
        await bot.sender.sendMessage(results[0].link)

def on_inline_query(msg):
    print("Inline query {}".format(str(msg)))

    def compute_answer():
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        results = so.search(intitle=query_string, body=query_string)

        articles = []
        for i, result in enumerate(results[:10]):
            # TODO get question to be cached somehow with
            # question = get_cached_or_not(result)
            question = result

            articles.append(
                InlineQueryResultArticle(
                    id="{}".format(i),
                    title="▴{} - {}".format(question.score, question.title),
                    # description=striphtml(question.body),
                    url=question.link,
                    input_message_content=InputTextMessageContent(message_text=question.link)))

        return articles

    # Defined later (?!?!)
    answerer.answer(msg, compute_answer)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
answerer = telepot.async.helper.Answerer(bot)

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop({'chat': on_chat_message,
                                   # 'callback_query': on_callback_query,
                                   'inline_query': on_inline_query,
                                   # 'chosen_inline_result': on_chosen_inline_result
}))
print('Listening ...')

loop.run_forever()

# TOKEN = sys.argv[1]  # get token from command-line

# bot = telepot.async.DelegatorBot(TOKEN, [
#     (per_chat_id(), create_open(NotStackOverflowBot, timeout=10)),
# ])

# loop = asyncio.get_event_loop()
# loop.create_task(bot.message_loop())
# print('Listening ...')

# loop.run_forever()
