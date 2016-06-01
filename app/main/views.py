# coding=utf-8
from flask import (render_template, session, redirect,url_for,
				   current_app, flash)
from . import main
from datetime import datetime
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Role
from ..email import send_email
from flask.ext.login import login_required, current_user
from ..decorator import admin_required

@main.route('/',methods=['GET','POST'])
def index():
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user = User(username=form.name.data)
			db.session.add(user)
			session['known'] = False
			if current_app.config['FLASK_ADMIN']:
				send_email(current_app.config['FLASK_ADMIN'],'新用户','mail/new_user',
						   user=user)
		else:
			session['known'] = True
			session['name'] = form.name.data
			form.name.data = ''
		return redirect(url_for('main.index'))
	return render_template('index.html',form=form,name=session.get('name'),
						   known=session.get('known',False),
						   current_time=datetime.utcnow())


@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		return False
	return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		flash('您的资料已更新')
		return redirect(url_for('main.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.location = form.location.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.about_me = form.about_me.data
		db.session.add(user)
		flash('用户资料已更新')
		return redirect(url_for('main.user',username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.location.data = user.location
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=form, user=user)