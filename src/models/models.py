import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from db.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    username = Column(String(125), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    files = relationship('File', cascade='delete')


class File(Base):
    __tablename__ = 'files'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(125), nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    path = Column(String(255), nullable=False, unique=True)
    size = Column(Integer, nullable=False)
    is_downloadable = Column(Boolean, default=False)
    user_id = Column(UUIDType(binary=False), ForeignKey('users.id'), nullable=False, index=True)

