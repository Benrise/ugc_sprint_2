import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    
    credentials_updated = Column(Boolean, default=True)

    is_oauth2 = Column(Boolean, default=False)
    oauth2 = relationship('OAuth2User', back_populates='user', uselist=False, cascade='all, delete-orphan')

    role_id = Column(ForeignKey('roles.id'), default=1)

    history = relationship('UserHistory', back_populates='user')
    role = relationship('Role', lazy='selectin')

    def __init__(self,
                 login: str,
                 password: str,
                 email: str | None = None,
                 first_name: str | None = None,
                 last_name: str | None = None,
                 is_oauth2: bool = False,
                 credentials_updated: bool = True) -> None:
        self.login = login
        self.email = email
        self.password = self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_oauth2 = is_oauth2
        self.credentials_updated = credentials_updated

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class OAuth2User(Base):
    __tablename__ = 'oauth2_users'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    oauth_id = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User', back_populates='oauth2')

    def __init__(self, oauth_id: str, provider: str, user_id: UUID) -> None:
        self.oauth_id = oauth_id
        self.provider = provider
        self.user_id = user_id


class UserHistory(Base):
    __tablename__ = 'login_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete="CASCADE"), default=uuid.uuid4, unique=False, nullable=False)
    logged_at = Column(DateTime, default=datetime.now())

    user = relationship('User', back_populates='history')


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    role = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return f'<User {self.role}>'
