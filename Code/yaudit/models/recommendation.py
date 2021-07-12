from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from yaudit.database import Base


class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False)

    view_action_id = Column(Integer, ForeignKey('view_actions.id'), nullable=False)
    view_action = relationship('ViewAction', back_populates='recommendations')
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    video = relationship('Video', back_populates='recommendations')

    def __init__(self, position, view_action_id, video_id):
        self.position = position
        self.view_action_id = view_action_id
        self.video_id = video_id

    def to_dict(self):
        return {
            'id': self.id,
            'position': self.position,
            'video_id': self.video_id,
            'view_action_id': self.view_action_id,
        }

    def __repr__(self):
        return '<Recommendation: id {}>'.format(self.id)
