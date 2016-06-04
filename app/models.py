# coding=utf-8
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.login import UserMixin,AnonymousUserMixin
from . import login_manager
import sys
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from datetime import datetime
from markdown import markdown
import bleach
from .exceptions import ValidationError
import flask_whooshalchemy  as whooshalchemy
from .ChineseAnalyzer import ChineseAnalyzer
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


class Follow(db.Model):
	__tablename__ ='follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow())


class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	username = db.Column(db.String(64), unique=True, index=True)
	email = db.Column(db.String(64), unique=True, index=True)
	password_hash = db.Column(db.String(64))
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	confirmed = db.Column(db.Boolean, default=False)
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
	img=db.Column(db.Unicode(64))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
					backref=db.backref('follower', lazy='joined'),
							   lazy='dynamic', cascade='all, delete-orphan')
	followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
							   backref=db.backref('followed', lazy='joined'),
							   lazy='dynamic', cascade='all, delete-orphan')
	comments = db.relationship('Comment', backref='author', lazy='dynamic')

	def __init__(self,**kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['FLASK_ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()
		self.follow(self)

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

	@property
	def followed_posts(self):
		return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
			.filter(Follow.follower_id == self.id)

	@staticmethod
	def add_self_follows():
		for user in User.query.all():
			if not user.is_following(user):
				user.follow(user)
				db.session.add(user)
				db.session.commit()

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

	def is_following(self, user):
		return self.followed.filter_by(followed_id=user.id).first() is not None

	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)

	def unfollow(self, user):
		f =self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)

	def is_followed_by(self, user):
		return self.follower.filter_by(follower_id=user.id).first() is not None

	def generate_auth_token(self,expiration=3600):
		s =Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'id': self.id})

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return None
		return User.query.get(data['id'])

	def allowed_img(self, img):
		from manage import app
		return '.' in img and img.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

	def to_json(self):
		json_user = {
			'url': url_for('api.get_user', id=self.id, _external=True),
			'username': self.username,
			'member_since': self.member_since,
			'last_seen': self.last_seen,
			'posts': url_for('api.get_posts',id=self.id, _external=True),
			'followed_posts': url_for('api.get_user_followed_posts', id=self.id,_external=True),
			'post.count':self.posts.count()
		} # 提供给客户端的资源<没必要>和数据库模型的内部表示完全一致，以实现隐私保护.
		return json_user


	def __repr__(self):
		return '<User %r>' % self.username

	def __str__(self):
		return '<User %r>' % self.name


class AnonymousUser(AnonymousUserMixin):
	def can(self,permissions):
		return False

	@staticmethod
	def is_administrator():
		return False


class Post(db.Model):
	__tablename__ ='posts'
	__searchable__ = ['title', 'body']
	__analyzer__ = ChineseAnalyzer()
	id = db.Column(db.Integer, primary_key=True, unique=True)
	title = db.Column(db.String(128))
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	comments = db.relationship('Comment', backref='post', lazy='dynamic')

	@staticmethod
	def on_changed_body(target,value,oldvalue,initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
					   'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3',
					   'p', 'br', 'u', 'time', 'article', 'h4']
		target.body_html = bleach.linkify(bleach.clean(markdown(value,\
				output_format='html'), tags=allowed_tags, strip=True))

	def to_json(self):
		json_post = {
			'url': url_for('api.get_post', id=self.id, _external=True),
			'title': self.title,
			'body': self.body,
			'body_html': self.body_html,
			'timestamp': self.timestamp,
			'author': url_for('api.get_user', id=self.author_id, _external=True),
			'comments': url_for('api.get_comments', id=self.id, _external=True),
			'comment_count': self.comments.count()
		}
		return json_post

	# json_post 是从客户端提供的
	@staticmethod
	def from_json(json_post):
		title = json_post.get('title')
		body = json_post.get('body')
		if body is None or body == '':
			raise ValidationError('博文没有内容.') # 这里的ValidationError不是来自wtforms
		return Post(title=title, body=body)

	def __repr__(self):
		return '<%r>' % (self.body)

	def __str__(self):
		return '<%s>' % (self.body)

def a():
	from manage import app
	whooshalchemy.whoosh_index(app, Post)

class Comment(db.Model):
	__tablename__ = 'comments'
	id =db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)
	disabled = db.Column(db.Boolean)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

	@staticmethod
	def on_changed_body(target,value,oldvalue,initiator):
		allowed_tag = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
					   'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3',
					   'p', 'br', 'u', 'time', 'article', 'h4']
		target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format='html'), tags=allowed_tag, strip=True))

	def to_json(self):
		json_comment = {
			'url': url_for('api.get_comment', id=self.id, _external=True),
			'post': url_for('api.get_post', id=self.post_id, _external=True),
			'body': self.body,
			'body_html': self.body_html,
			'author': url_for('api.get_user', id=self.author_id, _external=True)
		}
		return json_comment

	@staticmethod
	def from_json(json_comment):
		body = json_comment.get('body')
		if body is None or body == '':
			raise ValidationError('评论不能为空.')
		return Comment(body=body)

	def __repr__(self):
		return '<%r>' % (self.body)

	def __str__(self):
		return '<%s>' % (self.body)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

login_manager.anonymous_user = AnonymousUser

db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Comment.body, 'set', Comment.on_changed_body)