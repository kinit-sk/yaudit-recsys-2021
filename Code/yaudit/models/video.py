from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from yaudit.database import Base, session_scope


class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    youtube_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=True)
    channel = relationship('Channel', back_populates='videos')

    num_likes = Column(Integer, nullable=True)
    num_dislikes = Column(Integer, nullable=True)
    num_views = Column(Integer, nullable=True)
    num_comments = Column(Integer, nullable=True)

    stats = relationship('VideoStat', back_populates='video')
    seed_videos = relationship('SeedVideo', back_populates='video')
    view_actions = relationship('ViewAction', back_populates='video')
    search_results = relationship('SearchResult', back_populates='video')
    recommendations = relationship('Recommendation', back_populates='video')
    home_page_results = relationship('HomePageResult', back_populates='video')
    api_search_results = relationship('APISearchResult', back_populates='video')

    def __init__(self, youtube_id: str):
        self.youtube_id = youtube_id

    def to_dict(self):
        return {
            'id': self.id,
            'youtube_id': self.youtube_id,
            'title': self.title,
            'description': self.description,
            'duration_seconds': self.duration_seconds,
            'channel_id': self.channel_id,
            'num_likes': self.num_likes,
            'num_dislikes': self.num_dislikes,
            'num_views': self.num_views,
            'num_comments': self.num_comments
        }

    def __repr__(self):
        return '<Video: id {} youtube_id {}>'.format(self.id, self.youtube_id)

    @staticmethod
    def get_or_create(youtube_id):
        with session_scope() as session:
            video = session.query(Video).filter_by(youtube_id=youtube_id).first()
            if video is None:
                video = Video(youtube_id=youtube_id)
                session.add(video)
                session.commit()
                session.refresh(video)
            video = video.to_dict()
        return video
