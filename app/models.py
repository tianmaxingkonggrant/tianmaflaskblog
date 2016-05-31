# coding=utf-8
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.login import UserMixin
from . import login_manager
import sys
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


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
	confirmed = db.Column(db.Boolean,default=False)

	@property
	def password(self):
		raise AttributeError('密码不是一个可读的属性')

	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)

	def generate_confirmation_token(self,expiration=3600):
		s=Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
		return s.dumps({'confirm':self.id})

	def confirm(self,token):
		s=Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed =True
		db.session.add(self)
		return True

	def generate_reset_password_token(self,expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset':self.id})

	def reset_password(self, token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset') != self.id:
			return False
		self.password = new_password
		db.session.add(self)
		return True

	def generate_email_change_token(self, new_email,expiration=3600):
		s =Serializer(current_app.config['SECRET_KEY'],expiration)
		return s.dumps({'change_email':self.id,'new_email':new_email})

	def change_email(self, token):
		s =Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('change_email') != self.id:
			return False
		new_email = data.get('new_email')
		if new_email is None:
			return False
		if self.query.filter_by(email=new_email).first() is not None:
			return False
		self.email = new_email
		db.session.add(self)
		return True

	def __repr__(self):
		return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))









