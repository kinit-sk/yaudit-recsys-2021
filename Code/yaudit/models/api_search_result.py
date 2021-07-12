from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from yaudit.database import Base


class APISearchResult(Base):
    __tablename__ = 'api_search_results'

    id = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False)
    searched_at = Column(DateTime, nullable=False)

    search_query_id = Column(Integer, ForeignKey('search_queries.id'), nullable=False)
    search_query = relationship('SearchQuery', back_populates='api_search_results')
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    video = relationship('Video', back_populates='api_search_results')

    def __init__(self, position: int, search_query_id: int, searched_at):
        self.position = position
        self.search_query_id = search_query_id
        self.searched_at = searched_at

    def to_dict(self):
        return {
            'id': self.id,
            'position': self.position,
            'searched_at': self.searched_at.isoformat(),
            'video_id': self.video_id,
            'search_query_id': self.search_query_id,
        }

    def __repr__(self):
        return '<APISearchResult: id {}>'.format(self.id)
