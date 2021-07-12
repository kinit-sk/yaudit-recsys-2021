from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from yaudit.database import Base
from datetime import datetime


class VideoStat(Base):
    __tablename__ = 'video_stats'

    id = Column(Integer, primary_key=True)
    num_likes = Column(Integer, nullable=True)
    num_dislikes = Column(Integer, nullable=True)
    num_favorites = Column(Integer, nullable=True)
    num_views = Column(Integer, nullable=True)
    num_comments = Column(Integer, nullable=True)
    collected_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    video = relationship('Video', back_populates='stats')

    def __init__(self, video_id: int):
        self.video_id = video_id

    def to_dict(self):
        return {
            'id': self.id,
            'num_likes': self.num_likes,
            'num_dislikes': self.num_dislikes,
            'num_favorites': self.num_favorites,
            'num_views': self.num_views,
            'num_comments': self.num_comments,
            'collected_at': self.collected_at,
        }

    def __repr__(self):
        return '<VideoStats: id {}>'.format(self.id)
