import asyncio
import re
from datetime import datetime
import sys
import logging

from croniter import croniter
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from models import Notification


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)


if len(sys.argv) >= 3:
    API_TOKEN = sys.argv[1]
    USER_ID = sys.argv[2]
    try:
        USER_ID = int(USER_ID)
    except Exception:
        logging.error('USER_ID argument should be integer. Exiting...')
        exit(0)
else:
    logging.error('Not enough arguments. Exiting...')
    exit(0)

re_create_agrs = re.compile(r'text=\"(.*)\" cron=\"(.*)\"')
re_update_args_all = re.compile(r'id=(.*) text=\"(.*)\" cron=\"(.*)\"')
re_update_args_text = re.compile(r'id=(.*) text=\"(.*)\"')
re_update_args_cron = re.compile(r'id=(.*) cron=\"(.*)\"')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def cmd_help(message: types.Message):
    logging.info(f'[{message.chat.id}/{message.chat.username}] {message.get_command()} command')
    help_text = 'I\'m Reminder bot. You can set up notification and i will notify you.\n\n' \
                'Commands:\n' \
                '# list all notifications\n' \
                '/list\n\n' \
                '# create new notification\n' \
                '/create text="<notification text>" cron="<cron>"\n\n' \
                '# update notification\n' \
                '/update id=<id> text="<new notification text>" cron="<new cron>"\n' \
                '/update id=<id> text="<new notification text>"\n' \
                '/update id=<id> cron="<new cron>"\n\n' \
                '# delete notification\n' \
                '/delete <notification id>'
    await message.answer(help_text)


@dp.message_handler(commands=['list'])
async def cmd_list(message: types.Message):
    logging.info(f'[{message.chat.id}/{message.chat.username}] /list command')
    notifications = Notification.get_list()
    str_list = []
    for notification in notifications:
        str_list.append(f'id: {notification.id}\ntext: {notification.text}\ncron: {notification.cron}')
    if len(str_list) > 0:
        answer_str = '\n\n'.join(str_list)
    else:
        answer_str = 'No notifications. Add some with /create command'
    await message.answer(answer_str)


@dp.message_handler(commands=['create'])
async def cmd_create(message: types.Message):
    logging.info(f'[{message.chat.id}/{message.chat.username}] /create {message.get_args()}')
    match_result = re_create_agrs.match(message.get_args())
    if match_result is None:
        await message.answer('Can\'t parse arguments\nUse: /create text="<notification text>" cron="<cron>"')
        return
    text, cron = match_result.groups()
    notification = Notification.create(text, cron)
    if notification is None:
        await message.answer('Error: notification wasn\'t created')
    else:
        await message.answer('Success: notification was created')


@dp.message_handler(commands=['update'])
async def cmd_update(message: types.Message):
    logging.info(f'[{message.chat.id}/{message.chat.username}] /update {message.get_args()}')
    parse_err_text = 'Can\'t parse arguments\nUse one of commands:\n' \
                     '/update id=<id> text="<new notification text>" cron="<new cron>"\n' \
                     '/update id=<id> text="<new notification text>"\n' \
                     '/update id=<id> cron="<new cron>"'
    args = message.get_args()
    has_text = 'text=' in args
    has_cron = 'cron=' in args
    if has_text and has_cron:
        match_result = re_update_args_all.match(args)
        if match_result is None:
            await message.answer(parse_err_text)
            return
        _id, text, cron = match_result.groups()
    elif has_text:
        match_result = re_update_args_text.match(args)
        if match_result is None:
            await message.answer(parse_err_text)
            return
        _id, text = match_result.groups()
        cron = None
    elif has_cron:
        match_result = re_update_args_cron.match(args)
        if match_result is None:
            await message.answer(parse_err_text)
            return
        _id, cron = match_result.groups()
        text = None
    else:
        await message.answer(parse_err_text)
        return

    try:
        _id = int(_id)
    except Exception:
        await message.answer(parse_err_text)
        return

    notification = Notification.get(_id)
    if notification is None:
        await message.answer(f'Error: notification with id {_id} wasn\'t found')
        return

    success = []
    if text is not None:
        notification.text = text
        success.append(notification.text == text)
    if cron is not None:
        notification.cron = cron
        success.append(notification.cron == cron)

    if all(success):
        await message.answer('Success: notification was updated')
    else:
        await message.answer('Error: notification wasn\'t updated')


@dp.message_handler(commands=['delete'])
async def cmd_delete(message: types.Message):
    logging.info(f'[{message.chat.id}/{message.chat.username}] /delete {message.get_args()}')
    try:
        _id = int(message.get_args())
    except Exception:
        await message.answer('Can\'t parse argument\nUse: /delete <notification id>')
        return

    notification = Notification.get(_id)
    if notification is None:
        await message.answer(f'Error: notification with id {_id} wasn\'t found')
        return

    deletion_ok = notification.delete()
    if deletion_ok:
        await message.answer('Success: notification was deleted')
    else:
        await message.answer('Error: notification wasn\'t deleted')


async def wait_until_next_minute():
    dt = datetime.now()
    delta = 60.0 - (dt.second + dt.microsecond / 1000000)
    await asyncio.sleep(delta)


@dp.async_task
async def notificator():
    while True:
        await wait_until_next_minute()

        notifications = Notification.get_list()
        for notification in notifications:
            if croniter.match(notification.cron, datetime.now()):
                await bot.send_message(USER_ID, notification.text)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(notificator())
    executor.start_polling(dp, loop=loop, skip_updates=True)
