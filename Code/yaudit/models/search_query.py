from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from yaudit.database import Base


class SearchQuery(Base):
    __tablename__ = 'search_queries'

    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)

    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    topic = relationship('Topic', back_populates='search_queries')

    search_actions = relationship('SearchAction', back_populates='search_query')
    api_search_results = relationship('APISearchResult', back_populates='search_query')

    def __init__(self, topic, query: str):
        self.topic = topic
        self.query = query

    def to_dict(self):
        return {
            'id': self.id,
            'query': self.query,
            'topic_id': self.topic_id,
        }

    def __repr__(self):
        return '<SearchQuery: id {} query {}>'.format(self.id, self.query)
