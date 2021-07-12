from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from yaudit.database import Base, session_scope


class SearchAction(Base):
    __tablename__ = 'search_actions'

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sequence_number = Column(Integer, nullable=False)
    warning_message = Column(String, nullable=True)

    bot_id = Column(Integer, ForeignKey('bots.id'), nullable=False)
    bot = relationship('Bot', back_populates='search_actions')
    search_query_id = Column(Integer, ForeignKey('search_queries.id'), nullable=False)
    search_query = relationship('SearchQuery', back_populates='search_actions')

    search_results = relationship('SearchResult', back_populates='search_action')

    def __init__(self, bot_id, search_query_id, sequence_number):
        self.bot_id = bot_id
        self.search_query_id = search_query_id
        self.sequence_number = sequence_number

    def to_dict(self):
        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'search_query_id': self.search_query_id,
            'started_at': self.started_at,
            'sequence_number': self.sequence_number,
        }

    def __repr__(self):
        return '<SearchAction: id {}>'.format(self.id)

    @staticmethod
    def create(bot_id, search_query_id, sequence_number):
        with session_scope() as session:
            search_action = SearchAction(bot_id, search_query_id, sequence_number)
            session.add(search_action)
            session.commit()
            session.refresh(search_action)
            search_action = search_action.to_dict()
        return search_action

    @staticmethod
    def update_warning_message(search_action_id, warning_message):
        with session_scope() as session:
            search_action = session.query(SearchAction).get(search_action_id)
            search_action.warning_message = warning_message
