from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from yaudit.database import Base


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    youtube_id = Column(String, nullable=False)
    name = Column(String, nullable=False)

    videos = relationship('Video', back_populates='channel')

    def __init__(self, youtube_id: str, name: str):
        self.youtube_id = youtube_id
        self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'name': self.name,
        }

    def __repr__(self):
        return '<Channel: id {} url {} name {}>'.format(self.id, self.url, self.name)
