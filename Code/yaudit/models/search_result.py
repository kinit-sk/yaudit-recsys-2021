from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from yaudit.database import Base


class SearchResult(Base):
    __tablename__ = 'search_results'

    id = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False)

    search_action_id = Column(Integer, ForeignKey('search_actions.id'), nullable=False)
    search_action = relationship('SearchAction', back_populates='search_results')
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    video = relationship('Video', back_populates='search_results')

    def __init__(self, position, search_action_id, video_id):
        self.position = position
        self.search_action_id = search_action_id
        self.video_id = video_id

    def to_dict(self):
        return {
            'id': self.id,
            'position': self.position,
            'video_id': self.video_id,
            'search_action_id': self.search_action_id,
        }

    def __repr__(self):
        return '<SearchResult: id {}>'.format(self.id)
