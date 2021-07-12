from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import relationship
from yaudit.database import Base, session_scope


class Configuration(Base):
    __tablename__ = 'configurations'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    bubble_create_strategy = Column(String, nullable=True)
    bubble_burst_strategy = Column(String, nullable=True)
    params = Column(MutableDict.as_mutable(JSON), nullable=False)

    bots = relationship('Bot', back_populates='configuration')

    def __init__(self, name: str, params: dict = {}):
        self.name = name
        self.params = params

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bubble_create_strategy': self.bubble_create_strategy,
            'bubble_burst_strategy': self.bubble_burst_strategy,
            'params': self.params
        }

    def __repr__(self):
        return '<Configuration: id {} name {}>'.format(self.id, self.name)

    @staticmethod
    def get_by_id(configuration_id):
        with session_scope() as session:
            configuration = session.query(Configuration).get(configuration_id).to_dict()
        return configuration
