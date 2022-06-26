from src.app import db
from sqlalchemy import Column, ForeignKey, String, Integer, Float, Boolean, DateTime, ARRAY
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key = True)
    name = Column(String(50), index = True, unique = True)
    access_right = Column(Boolean, default = False)
    identity = relationship('Identity')

    def __init__(self, name, access_right):
        self.name = name
        self.access_right = access_right
    
    def create(self):
        db.session.add(self)
        db.session.commit(self)
        return

class Identity(db.Model):
    __tablename__ = 'identities'
    id = Column(Integer, primary_key = True)
    name = Column(String(50), index = True)
    anchor_path = Column(String(100), index = True, unique = True)
    embedding_path = Column(String(100), unique = True)
    role_id = Column(Integer, ForeignKey('roles.id'))

    def __init__(self, name, anchor_path, embedding_path, role_id):
        self.name = name
        self.anchor_path = anchor_path
        self.embedding_path = embedding_path
        self.role_id = role_id

    def create(self):
        db.session.add(self)
        db.session.commit(self)
        return

class Access(db.Model):
    __tablename__ = 'accesses'
    time = Column(DateTime(), default = datetime.utcnow, primary_key = True)
    key = Column(String, index = True)
    query_path = Column(String(100), unique = True, index = True)
    identity_id = Column(Integer, ForeignKey('identities.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))
    conf_score = Column(Float)
    permission_status = Column(Boolean)

    def __init__(self, time, query_path, identity_id, role_id, conf_score, permission_status):
        self.time = time
        self.key = generate_password_hash(self.time)
        self.query_path = query_path
        self.identity_id = identity_id
        self.role_id = role_id
        self.conf_score = conf_score
        self.permission_status = permission_status

    def create(self):
        db.session.add(self)
        db.session.commit(self)
        return self.key