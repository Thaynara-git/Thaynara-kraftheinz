from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import validates

from app import db


class Topico(db.Model):
    __tablename__ = 'topico'
    id = Column(Integer, primary_key=True)
    titulo = Column(String(50))
    categoria = Column(String(50))
    descricao = Column(String(250))

    def __str__(self):
        return self.titulo

class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    topico = Column(Integer, ForeignKey('topico.id', ondelete="CASCADE"))
    usuario = Column(String(30))
    nota = Column(Integer)
    texto_review = Column(String(500))
    data_review = Column(DateTime)

    @validates('nota')
    def validate_rating(self, key, value):
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return f"{self.usuario}: {self.data_review:%x}"
