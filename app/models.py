# coding=utf-8
from . import db
class Role(db.Model):
	__tablename__='roles'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True)
	default = db.Column(db.Boolean,default=False,index=True)
	users = db.relationship('User',backref='role',lazy='dynamic')

	def __repr__(self):
		return '<Role %r>' % self.name


class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key=True,unique=True)
	username = db.Column(db.String(64),unique=True,index=True)
	email = db.Column(db.String(64),unique=True,index=True)
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'),nullable=False)


	def __repr__(self):
		return '<User %r>' % self.username










