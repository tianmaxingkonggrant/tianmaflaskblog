# coding=utf-8
from functools import wraps
from flask import abort, flash, redirect, url_for, current_app
from flask.ext.login import current_user
from .models import Permission

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kwargs):
			if not current_user.can(permission): abort(403)
			return f(*args, **kwargs)
		return decorated_function
	return decorator


def admin_required(f):
	return permission_required(Permission.ADMINISTER)(f)


def login_required(func):
	@wraps(func)
	def decorated_view(*args, **kwargs):
		if current_app.login_manager._login_disabled:
			return func(*args, **kwargs)
		elif not current_user.is_authenticated:
			flash('您好,请先登陆.')
			return redirect(url_for('auth.login'))
		return func(*args, **kwargs)
	return decorated_view