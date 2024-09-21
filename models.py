# models.py
import enum

from base import Base

from sqlalchemy import Column, String, Enum, ForeignKey, Float, BigInteger
from sqlalchemy.orm import relationship




class BiddingState(enum.Enum):
    STALL = 'stall'
    WAITING_FOR_RATE = 'wait_bid_rate'


class TransactionState(enum.Enum):
    STALL = 'stall'
    WAITING_FOR_DESCRIPTION = 'wait_description'
    WAITING_FOR_CURRENCY = 'wait_currency'


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    username = Column(String)
    chat_id = Column(BigInteger, unique=True)
    offers = relationship('Offer', back_populates='creator', lazy='subquery')
    bids = relationship('Bid', back_populates='buyer', lazy='subquery')

    def __init__(self, name, lastname, username, chat_id):
        self.name = name
        self.lastname = lastname
        self.chat_id = chat_id
        self.username = username

    @staticmethod
    def get_user_by_chat_id(session, chat_id):
        return session.query(User).filter_by(chat_id=chat_id).first()


class Offer(Base):
    __tablename__ = 'offers'

    id = Column(BigInteger, primary_key=True)
    creator_id = Column(BigInteger, ForeignKey('users.id'))
    creator = relationship("User", back_populates="offers", lazy='subquery')
    description = Column(String)
    currency = Column(String)
    bid = relationship('Bid', uselist=False, back_populates='offer', lazy='subquery')
    bids = relationship('Bid', back_populates='offer', lazy='subquery')

    @staticmethod
    def get_offers(session, user=None):
        if user:
            return session.query(Offer).filter_by(creator=user).all()
        return session.query(Offer).filter_by().all()

    @staticmethod
    def get_active_bids_count(session, offer_id):
        return session.query(Bid).filter_by(offer_id=offer_id).count()

    @staticmethod
    def get_bids(session, offer_id):
        return session.query(Bid).filter_by(offer_id=offer_id).all()


class Bid(Base):
    __tablename__ = 'bids'

    id = Column(BigInteger, primary_key=True)
    offer = relationship('Offer', uselist=False, back_populates='bid', lazy='subquery')
    offer_id = Column(BigInteger, ForeignKey('offers.id'))
    bid_rate = Column(Float)
    buyer_id = Column(BigInteger, ForeignKey('users.id'))
    buyer = relationship("User", back_populates="bids", lazy='subquery')

    @staticmethod
    def get_bids(session, state=None, user=None):
        if state and not user:
            return session.query(Bid).filter_by(state=state).all()
        elif user and not state:
            return session.query(Bid).filter_by(buyer=user).all()
        return session.query(Bid).filter_by(buyer=user, state=state).all()