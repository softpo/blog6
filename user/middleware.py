# coding: utf-8

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from user.models import User


class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        uid = request.session.get('uid')
        if uid is not None:
            user = User.objects.get(id=uid)
            request.user = user
