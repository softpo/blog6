# coding: utf-8

from django.shortcuts import render

from user.models import Permission


def check_permission(user, perm_name):
    '''检查用户是否具有该权限'''
    user_perm = Permission.objects.get(id=user.pid)
    need_perm = Permission.objects.get(name=perm_name)
    return user_perm.perm >= need_perm.perm


def permit(perm_name):
    '''权限检查装饰器'''
    def wrap1(view_func):
        def wrap2(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            if user is not None:
                if check_permission(user, perm_name):
                    return view_func(request, *args, **kwargs)
            return render(request, 'blockers.html')
        return wrap2
    return wrap1
