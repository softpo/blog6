# coding: utf-8

from django.core.cache import cache


def page_cache(timeout):
    '''页面缓存'''
    def wrap1(view_func):
        def wrap2(request, *args, **kwargs):
            key = 'PAGES-%s' % request.get_full_path()
            # 从缓存获取 response
            response = cache.get(key)
            if response is not None:
                print('return from cache')
                # 如果有 -> 直接返回 response
                return response
            else:
                print('return from view')
                # 没有 -> 执行 view 函数
                response = view_func(request, *args, **kwargs)
                # 将结果添加缓存
                cache.set(key, response, timeout)
                return response
        return wrap2
    return wrap1
