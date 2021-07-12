from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from yaudit.database import Base


class HomePageResult(Base):
    __tablename__ = 'home_page_results'

    id = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False)
    page_section = Column(String, nullable=True)

    home_page_action_id = Column(Integer, ForeignKey('home_page_actions.id'), nullable=False)
    home_page_action = relationship('HomePageAction', back_populates='home_page_results')
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    video = relationship('Video', back_populates='home_page_results')

    def __init__(self, position, home_page_action_id, video_id):
        self.position = position
        self.home_page_action_id = home_page_action_id
        self.video_id = video_id

    def to_dict(self):
        return {
            'id': self.id,
            'position': self.position,
            'page_section': self.page_section,
            'video_id': self.video_id,
            'home_page_action_id': self.home_page_action_id,
        }

    def __repr__(self):
        return '<HomePageResult: id {}>'.format(self.id)
