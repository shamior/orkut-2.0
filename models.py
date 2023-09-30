from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    usuario = Column(String(20), primary_key=True)
    nome = Column(String(64), nullable=False)
    sobrenome = Column(String(64), nullable=False)
    senha = Column(String(102), nullable=False)
    criado_em = Column(DateTime, default=datetime.now)