import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from ..base import Base


class RolePermission(Base):
    __tablename__ = 'role_permission'

    id = sa.Column(sa.Integer, primary_key=True)
    role_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            'role.id',
            ondelete='CASCADE',
        ),
    )
    permission_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            'permission.id',
            ondelete='CASCADE',
        ),
    )
    role_permission = relationship('Permission')


class Permission(Base):
    __tablename__ = 'permission'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(128), nullable=False, unique=True)
    title = sa.Column(sa.String(1024), nullable=False, unique=True)


class Role(Base):
    __tablename__ = 'role'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(128), nullable=False, unique=True)
    title = sa.Column(sa.String(128), nullable=False, unique=True)

    permissions = relationship(
        'Permission', secondary=RolePermission.__table__, backref='role', lazy='select', innerjoin=True
    )
    users = relationship('User', backref='role')


class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column(sa.String(128), nullable=False, unique=True)
    password = sa.Column(sa.String(128), nullable=False)
    full_name = sa.Column(sa.String(128), nullable=False)
    email = sa.Column(sa.String(128), nullable=True)
    phone_number = sa.Column(sa.String(20), nullable=True)
    city = sa.Column(sa.String(128), nullable=True)
    address = sa.Column(sa.String(128), nullable=True)
    zip_code = sa.Column(sa.String(128), nullable=True)
    is_active = sa.Column(sa.Boolean, default=False)
    role_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            'role.id',
            ondelete='SET NULL',
        ),
    )
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.now)
