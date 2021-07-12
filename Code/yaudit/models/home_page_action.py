from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from yaudit.database import Base, session_scope
from datetime import datetime


class HomePageAction(Base):
    __tablename__ = 'home_page_actions'

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sequence_number = Column(Integer, nullable=False)
    warning_message = Column(String, nullable=True)

    bot_id = Column(Integer, ForeignKey('bots.id'), nullable=False)
    bot = relationship('Bot', back_populates='home_page_actions')

    home_page_results = relationship('HomePageResult', back_populates='home_page_action')

    def __init__(self, bot_id, sequence_number):
        self.bot_id = bot_id
        self.sequence_number = sequence_number

    def to_dict(self):
        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'started_at': self.started_at,
            'sequence_number': self.sequence_number,
        }

    def __repr__(self):
        return '<HomePageAction: id {}>'.format(self.id)

    @staticmethod
    def create(bot_id, sequence_number):
        with session_scope() as session:
            homepage_action = HomePageAction(bot_id, sequence_number)
            session.add(homepage_action)
            session.commit()
            session.refresh(homepage_action)
            homepage_action = homepage_action.to_dict()
        return homepage_action

    @staticmethod
    def update_warning_message(home_page_action_id, warning_message):
        with session_scope() as session:
            home_page_action = session.query(HomePageAction).get(home_page_action_id)
            home_page_action.warning_message = warning_message
