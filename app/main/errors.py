# coding=utf-8
from flask import render_template,request, jsonify
from . import main

# app_errorhandler 面向蓝本但也可以处理蓝本之外的错误.#

@main.app_errorhandler(404)
def page_not_found(e):
	if request.accept_mimetypes.accept_json and not request.\
		accept_mimetypes.accept_html:
		response = jsonify({'error': '没有发现相应页面'})
		response.status_code = 404
		return response
	return render_template('404.html'), 404


@main.app_errorhandler(500)
def interval_server_error(e):
	if request.accept_mimetypes.accept_json and not request.\
			accept_mimetypes.accpet_html:
		response = jsonify({'error':'处理请求过程中发生意外错误.'})
		response.status_code = 500
		return response
	return render_template('500.html'), 500


@main.app_errorhandler(401)
def authentication_required(e):
	return render_template('401.html'), 401


@main.app_errorhandler(403)
def authentication_required(e):
	return render_template('401.html'), 403
