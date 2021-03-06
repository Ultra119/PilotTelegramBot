from aiogram import Bot, Dispatcher
from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String,
                        text, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import config
from utils.translation import TranslationWorker

from loguru import logger

logger.info('Welcome to PilotTelegramBot!\nStarting init...')
bot = Bot(config.token)
dp = Dispatcher(bot)
logger.info('AIOgram init                   [ OK ]')

Base = declarative_base()


class Notes(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    message_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'))
    chat = relationship("Chats", backref='Chat')


class Chats(Base):
    __tablename__ = "chats"
    chat_id = Column(Integer, primary_key=True)
    setup_is_finished = Column(Boolean, nullable=False)
    greeting = Column(String)
    leave_msg = Column(String)
    language = Column(String, server_default=text('rus'))


engine = create_engine(
            "sqlite:///db.sqlite", 
        )
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
logger.info('SQL Alchemy init               [ OK ]')

tw = TranslationWorker(session, Chats)
logger.info('TranslationWorker init         [ OK ]')
logger.info('Init finished! Starting polling...')
