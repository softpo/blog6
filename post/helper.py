# coding: utf-8

import logging

from redis import Redis
from django.core.cache import cache
from django.conf import settings

from post.models import Article

rds = Redis(**settings.REDIS)
logger = logging.getLogger('statistic')


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


def record_click(article_id, count=1):
    '''记录文章点击'''
    rds.zincrby('Article-clicks', article_id, count)


def get_top_n_articles(number):
    '''获取 TopN 的文章'''
    # article_clicks 格式：
    #   [
    #       (b'3', 725.0),
    #       (b'4', 512.0),
    #       (b'2', 456.0),
    #       ...
    #   ]
    article_clicks = rds.zrevrange('Article-clicks', 0, number, withscores=True)  # 从 Redis 取出排行数据

    # article_clicks 列表推导式拆解过程
    # article_clicks_data = []
    # for aid, click in article_clicks:
    #     aid, click = int(aid), int(click)
    #     article_clicks_data.append([aid, click])
    article_clicks = [[int(aid), int(click)] for aid, click in article_clicks]    # 数据类型转换

    aid_list = [d[0] for d in article_clicks]                                     # 文章 id
    articles = Article.objects.in_bulk(aid_list)                                  # 批量取出文章

    # 转换 aid 为 Article 的实例
    for data in article_clicks:
        aid = data[0]
        data[0] = articles[aid]

    # 返回的数据格式
    #    [
    #        [Article(6), 725],
    #        [Article(2), 251],
    #        [Article(9), 312],
    #    ]
    return article_clicks


def statistic(view_func):
    def wrap(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        if response.status_code == 200:
            ip = request.META['REMOTE_ADDR']
            aid = request.GET.get('aid')
            logger.info('%s %s' % (ip, aid))
        return response
    return wrap
