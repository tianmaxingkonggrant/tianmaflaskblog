# coding=utf-8
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.login import UserMixin
from . import login_manager
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Role(db.Model):
	__tablename__='roles'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True)
	default = db.Column(db.Boolean,default=False,index=True)
	users = db.relationship('User',backref='role',lazy='dynamic')

	def __repr__(self):
		return '<Role %r>' % self.name


class User(UserMixin,db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key=True,unique=True)
	username = db.Column(db.String(64),unique=True,index=True)
	email = db.Column(db.String(64),unique=True,index=True)
	password_hash = db.Column(db.String(128))
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))


	@property
	def password(self):
		raise AttributeError('密码不是一个可读的属性')

	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)


	def __repr__(self):
		return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))









