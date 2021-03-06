# coding=utf-8
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard guess'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = '587'
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	FLASK_MAIL_SUBJECT_PREFIX = '[天马博客]'
	FLASK_MAIL_SENDER = os.environ.get('FLASK_ADMIN')
	FLASK_ADMIN = os.environ.get('FLASK_ADMIN')
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	FLASK_POSTS_PER_PAGE = 10
	FLASK_FOLLOWERS_PER_PAGE = 10
	FLASK_PER_PAGE_COMMENTS = 10
	ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
	UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploadimages')
	MAX_SEARCH_RESULTS = 10
	WHOOSH_BASE = os.path.join(basedir, 'searchindexdir')
	WHOSHEE_MIN_STRING_LEN = 1
	PACKAGE_DIR = '/tmp/'
	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
		'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
		'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'default': DevelopmentConfig
}





