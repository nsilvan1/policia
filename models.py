# /policia_civil/models.py
from flask_pymongo import PyMongo

class Policial:
    def __init__(self, passport, name, cargo, unidade, transgressao, ultima_promocao, username, password, active=False):
        self.passport = passport
        self.name = name
        self.cargo = cargo
        self.unidade = unidade
        self.transgressao = transgressao
        self.ultima_promocao = ultima_promocao
        self.username = username
        self.password = password
        self.active = active

class Curso:
    def __init__(self, nome, descricao, instrutor):
        self.nome = nome
        self.descricao = descricao
        self.instrutor = instrutor

class Armamento:
    def __init__(self, nome, patente_permitida):
        self.nome = nome
        self.patente_permitida = patente_permitida

class Aviso:
    def __init__(self, titulo, conteudo, autor):
        self.titulo = titulo
        self.conteudo = conteudo
        self.autor = autor