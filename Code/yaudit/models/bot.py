from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from yaudit.database import Base, session_scope


class Bot(Base):
    __tablename__ = 'bots'

    id = Column(Integer, primary_key=True)
    initialized_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    account = relationship('Account', back_populates='bots')
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    topic = relationship('Topic', back_populates='bots')
    configuration_id = Column(Integer, ForeignKey('configurations.id'), nullable=False)
    configuration = relationship('Configuration', back_populates='bots')

    search_actions = relationship('SearchAction', back_populates='bot')
    view_actions = relationship('ViewAction', back_populates='bot')
    home_page_actions = relationship('HomePageAction', back_populates='bot')

    def __init__(self, account: int, topic: int, configuration: int):
        self.account_id = account
        self.topic_id = topic
        self.configuration_id = configuration

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'topic_id': self.topic_id,
            'configuration_id': self.configuration_id,
            'initialized_at': self.initialized_at,
        }

    def __repr__(self):
        return '<Bot: id {}>'.format(self.id)

    @staticmethod
    def create(account_id, topic_id, configuration_id):
        with session_scope() as session:
            bot = Bot(account_id, topic_id, configuration_id)
            session.add(bot)
            session.commit()
            session.refresh(bot)
            bot_to_return = bot.to_dict()
        return bot_to_return
