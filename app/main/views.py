# coding=utf-8
from flask import (render_template, abort, redirect,url_for,
				   current_app, flash, request)
from . import main
from datetime import datetime
from .forms import PostForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Role, Permission, Post
from ..email import send_email
from flask.ext.login import login_required, current_user
from ..decorator import admin_required,permission_required

@main.route('/',methods=['GET','POST'])
def index():
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		post = Post(title=form.title.data, body=form.body.data, author=current_user._get_current_object())
		db.session.add(post)
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'], error_out=False
	)
	posts = pagination.items
	return render_template('index.html', form=form, posts=posts, pagination=pagination)



@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'],
        error_out=False)
	posts = pagination.items
	return render_template('user.html', user=user, posts=posts, pagination=pagination)


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


@main.route('/post/<int:id>')
def post(id):
	post = Post.query.get_or_404(id)
	return render_template('post.html', posts=[post])

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		db.session.add(post)
		flash('您的博文已更新.')
		return redirect(url_for('main.post', id=post.id))
	form.title.data = post.title
	form.body.data = post.body
	return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在.')
		return redirect(url_for('main.index'))
	if current_user.is_following(user):
		flash('您已关注了%s.' % username)
		return redirect(url_for('main.user', username=username))
	current_user.follow(user)
	return redirect(url_for('main.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在.')
		return redirect(url_for('main.index'))
	if not current_user.is_following(user):
		flash('您已不再关注%s.' % username)
		return redirect(url_for('main.user', username=username))
	current_user.unfollow(user)
	return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在.')
		return redirect(url_for('main.user', username=username))
	page = request.args.get('page', 1, type=int)
	pagination = user.followers.paginate(
		page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'], error_out=False
	)
	follows = [{'user': item.follower, 'timestamp':item.timestamp} for item\
			   in pagination.items]
	return render_template('followers.html', user=user, pagination=pagination,
						   follows=follows, title="Followers of",
                           endpoint='main.followers')


@main.route('/followed/<username>')
def followed(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('用户不存在.')
		return redirect(url_for('main.user', username=username))
	page = request.args.get('page', 1, type=int)
	pagination = user.followed.paginate(
		page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'], error_out=False
	)
	follows = [{'user': item.followed, 'timestamp': item.timestamp} for item\
			   in pagination.items]
	return render_template('followers.html', user=user, pagination=pagination,
						   follows=follows, title='Followed by', endpoint='main.followed')