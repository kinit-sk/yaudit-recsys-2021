from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from yaudit.database import Base, session_scope


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)

    username = Column(String(), nullable=True)
    password = Column(String(), nullable=True)
    attributes = Column(MutableDict.as_mutable(JSON), nullable=False)

    bots = relationship('Bot', back_populates='account')

    def __init__(self, attributes: dict = {}):
        self.attributes = attributes

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'attributes': self.attributes
        }

    def __repr__(self):
        return '<Account: id {}>'.format(self.id)

    @staticmethod
    def get_by_id(account_id):
        with session_scope() as session:
            account = session.query(Account).get(account_id).to_dict()
        return account
