# coding=utf-8
from flask import jsonify
from . import api
from ..exceptions import ValidationError

def bad_request(message):
	response = jsonify({'error': '请求不可用', 'message': message})
	response.status_code = 400
	return response


def forbidden(message):
	response = jsonify({'error': '请求中发送的认证密令无权访问目标', 'message': message})
	response.status_code = 403
	return response


def unauthorized(message):
	response = jsonify({'error': '请求未包含认证信息', 'message': message})
	response.status_code = 401
	return response


@api.errorhandler(ValidationError)
def validation_error(e):
	return bad_request(e.args[0])