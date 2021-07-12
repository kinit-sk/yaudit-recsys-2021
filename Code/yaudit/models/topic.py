from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from yaudit.database import Base, session_scope


class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    full_name = Column(String(), nullable=True)

    search_queries = relationship('SearchQuery', back_populates='topic')
    seed_videos = relationship('SeedVideo', back_populates='topic')
    bots = relationship('Bot', back_populates='topic')

    def __init__(self, name: str):
        self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'seed_videos': self.get_most_popular_videos(),
            'search_queries': [query.to_dict() for query in self.search_queries]
        }

    def __repr__(self):
        return '<Topic: id {} name {}>'.format(self.id, self.name)

    def get_most_popular_videos(self):
        promoting = sorted(
                [video.to_dict() for video in self.seed_videos if video.stance == 'promoting'],
                key=lambda i: i.get('popularity', 0),
                reverse=True
        )
        debunking = sorted(
                [video.to_dict() for video in self.seed_videos if video.stance == 'debunking'],
                key=lambda i: i.get('popularity', 0),
                reverse=True
        )
        return {'promoting': promoting, 'debunking': debunking}

    @staticmethod
    def get_by_id(topic_id):
        with session_scope() as session:
            topic = session.query(Topic).get(topic_id).to_dict()
        return topic
