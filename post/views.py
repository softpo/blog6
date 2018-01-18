# coding: utf-8
from math import ceil

from django.shortcuts import render, redirect
from django.core.cache import cache

from post.helper import page_cache
from post.helper import record_click
from post.helper import get_top_n_articles
from post.helper import statistic
from post.models import Article, Comment, Tag


@page_cache(1)
def home(request):
    # 计算总页数
    count = Article.objects.count()
    pages = ceil(count / 5)

    # 获取当前页数
    page = int(request.GET.get('page', 1))
    page = 0 if page < 1 or page >= (pages + 1) else (page - 1)

    # 取出当前页面的文章
    start = page * 5
    end = start + 5
    articles = Article.objects.all()[start:end]

    # 取出 Top 10
    top10 = get_top_n_articles(10)
    return render(request, 'home.html',
                  {'articles': articles, 'page': page, 'pages': range(pages), 'top10': top10})


@statistic
@page_cache(5)
def article(request):
    aid = int(request.GET.get('aid', 1))
    article = Article.objects.get(id=aid)
    comments = Comment.objects.filter(aid=aid)
    record_click(aid)  # 记录文章点击
    return render(request, 'article.html', {'article': article, 'comments': comments})


def create(request):
    if request.method == 'POST':
        # 创建文章
        title = request.POST.get('title')
        content = request.POST.get('content')
        article = Article.objects.create(title=title, content=content)

        # 创建 Tags
        tags = request.POST.get('tags', '')
        if tags:
            tags = [t.strip() for t in tags.split(',')]
            Tag.create_new_tags(tags, article.id)

        return redirect('/post/article/?aid=%s' % article.id)
    else:
        return render(request, 'create.html')


def editor(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        aid = int(request.POST.get('aid'))

        article = Article.objects.get(id=aid)
        article.title = title
        article.content = content
        article.save()

        # 创建或更新
        tags = request.POST.get('tags', '')
        if tags:
            tags = [t.strip() for t in tags.split(',')]
            Tag.update_article_tags(tags)

        return redirect('/post/article/?aid=%s' % article.id)
    else:
        aid = int(request.GET.get('aid', 0))
        article = Article.objects.get(id=aid)
        return render(request, 'editor.html', {'article': article})


def comment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        content = request.POST.get('content')
        aid = int(request.POST.get('aid'))

        Comment.objects.create(name=name, content=content, aid=aid)
        return redirect('/post/article/?aid=%s' % aid)
    return redirect('/post/home/')


def search(request):
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        articles = Article.objects.filter(content__contains=keyword)
        return render(request, 'home.html', {'articles': articles})
