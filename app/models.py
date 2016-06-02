# coding=utf-8
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.login import UserMixin,AnonymousUserMixin
from . import login_manager
import sys
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from markdown import markdown
import bleach

reload(sys)
sys.setdefaultencoding('utf8')


class Permission(object):
	FOLLOW = 0X01
	COMMENT = 0X02
	WRITE_ARTICLES = 0X04
	MODERATE_COMMENTS = 0X08
	ADMINISTER = 0X08


class Role(db.Model):
	__tablename__='roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)
	users = db.relationship('User', backref='role', lazy='dynamic')


	@staticmethod
	def insert_roles():
		roles = {
			'User': (Permission.FOLLOW |
					 Permission.COMMENT |
					 Permission.WRITE_ARTICLES, True),
			'Moderator': (Permission.FOLLOW |
						 Permission.COMMENT |
						 Permission.WRITE_ARTICLES |
						 Permission.MODERATE_COMMENTS, False),
			'Administrator': (0xff, False)
		}
		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.permissions = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)
		db.session.commit()

	def __repr__(self):
		return '<Role %r>' % self.name


class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key=True,unique=True)
	username = db.Column(db.String(64),unique=True,index=True)
	email = db.Column(db.String(64),unique=True,index=True)
	password_hash = db.Column(db.String(64))
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
	confirmed = db.Column(db.Boolean,default=False)
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
	posts = db.relationship('Post', backref='author', lazy='dynamic')


	def __init__(self,**kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['FLASK_ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()


	def can(self,permissions):
		return self.role is not None and \
			   (self.role.permissions & permissions) == permissions

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

	@property
	def password(self):
		raise AttributeError('密码不是一个可读的属性')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def generate_confirmation_token(self, expiration=3600):
		s=Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'confirm': self.id})

	def confirm(self, token):
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

	def generate_reset_password_token(self, expiration=3600):
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
		return s.dumps({'change_email': self.id, 'new_email': new_email})

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

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)

	def __repr__(self):
		return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
	def can(self,permissions):
		return False

	@staticmethod
	def is_administrator(self):
		return False


class Post(db.Model):
	__tablename__ ='posts'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	title = db.Column(db.String(128))
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow())
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


	@staticmethod
	def on_change_body(target,value,oldvalue,initacor):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
					   'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3',
					   'p', 'br', 'u', 'time', 'article', 'h4']
		target.body_html = bleach.linkify(bleach.clean(markdown(value,\
				output_format='html'), tags=allowed_tags, strip=True))



@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

login_manager.anonymous_user = AnonymousUser

db.event.listen(Post.body, 'set', Post.on_change_body)