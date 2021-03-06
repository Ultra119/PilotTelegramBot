from init import bot, dp, tw, Chats, session
from aiogram.types import Message
import config
from loguru import logger

@dp.message_handler(commands='broadcast')
async def broadcast(message: Message):
    trans = tw.get_translation(message, default=True)
    if trans == 1:
        return
    if message.from_user.username == config.owner_username:
        try:
            logger.info('The broadcast has begun')
            chat_ids = session.query(Chats.chat_id).all()

            msg = await bot.send_message(chat_id=message.chat.id, text=trans['admin']['broadcast']['start'])

            i = 0
            for chat_id in chat_ids:
                await bot.send_message(chat_id=chat_id[0], text=message.text.split(' ', 1)[1])
                i += 1
                await bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                            text=trans['admin']['broadcast']['process'].format(count=str(i)))

            await bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                        text=trans['admin']['broadcast']['end'].format(count=str(i)))
            logger.info(f'Broadcast ended, messages sent: {str(i)}')
        except Exception as err:
            logger.error(f"{message.chat.full_name}: User {message.from_user.full_name} {err}")
