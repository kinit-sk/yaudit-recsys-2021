from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from yaudit.database import Base


class SeedVideo(Base):
    __tablename__ = 'seed_videos'

    id = Column(Integer, primary_key=True)

    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    topic = relationship('Topic', back_populates='seed_videos')
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    video = relationship('Video', back_populates='seed_videos')
    stance = Column(String, nullable=False)

    def __init__(self):
        pass

    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'video_id': self.video_id,
            'youtube_id': self.video.youtube_id,
            'stance': self.stance,
            'video': self.video.to_dict(),
            'popularity': self.video.num_views + self.video.num_comments + self.video.num_likes + self.video.num_dislikes
        }

    def __repr__(self):
        return '<SeedVideo: id {}>'.format(self.id)
