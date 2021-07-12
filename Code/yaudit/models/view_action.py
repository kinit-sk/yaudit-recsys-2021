from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from yaudit.database import Base, session_scope
from datetime import datetime


class ViewAction(Base):
    __tablename__ = 'view_actions'

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sequence_number = Column(Integer, nullable=False)
    warning_message = Column(String, nullable=True)

    bot_id = Column(Integer, ForeignKey('bots.id'), nullable=False)
    bot = relationship('Bot', back_populates='view_actions')
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    video = relationship('Video', back_populates='view_actions')

    recommendations = relationship('Recommendation', back_populates='view_action')

    def __init__(self, bot_id, video_id, sequence_number):
        self.bot_id = bot_id
        self.video_id = video_id
        self.sequence_number = sequence_number

    def to_dict(self):
        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'video_id': self.video_id,
            'started_at': self.started_at,
            'sequence_number': self.sequence_number,
        }

    def __repr__(self):
        return '<ViewAction: id {}>'.format(self.id)

    @staticmethod
    def create(bot_id, video_id, sequence_number):
        with session_scope() as session:
            view_action = ViewAction(bot_id, video_id, sequence_number)
            session.add(view_action)
            session.commit()
            session.refresh(view_action)
            view_action = view_action.to_dict()
        return view_action

    @staticmethod
    def update_warning_message(view_action_id, warning_message):
        with session_scope() as session:
            view_action = session.query(ViewAction).get(view_action_id)
            view_action.warning_message = warning_message
