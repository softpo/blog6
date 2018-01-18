from django.db import models
from django.utils.functional import cached_property


class Article(models.Model):
    title = models.CharField(max_length=128)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    @classmethod
    def update_article_tags(self, tags):
        pass

    # @cached_property
    def tags(self):
        article_tags = ArticleTags.objects.filter(aid=self.id).only('tid')
        tid_list = [at.tid for at in article_tags]
        return Tag.objects.in_bulk(tid_list)


class Comment(models.Model):
    aid = models.IntegerField()
    name = models.CharField(max_length=128, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=False, null=False)

    @classmethod
    def create_new_tags(cls, tag_names, aid):
        # 创建 Tags
        exist_tags = cls.objects.filter(name__in=tag_names).only('name')  # 取出已存在的 tags
        exists = [t.name for t in exist_tags]                             # 取出这些 tags 的 name
        new_tags = set(tag_names) - set(exists)                           # 去除已存在的 tags
        new_tags = [cls(name=n) for n in new_tags]                        # 生成带创建的 Tag 对象列表
        cls.objects.bulk_create(new_tags)                                 # 批量创建

        # 建立与 Article 的关系
        tags = cls.objects.in_bulk(tag_names, field_name='name')
        for t in tags:
            articletag = ArticleTags(aid=aid, tid=t.id)
            articletag.update_or_create()
        return tags

    @cached_property
    def articles(self):
        aid_list = [at.aid for at in ArticleTags.objects.filter(tid=self.id).only('aid')]
        return Article.objects.in_bulk(aid_list)


class ArticleTags(models.Model):
    '''
    文章与标签的关系表

    表结构实例
        aid  tid
        ---  ---
          1    4
          1    9
         19    5
         31    5
          1   17
    '''
    aid = models.IntegerField()  # Article ID
    tid = models.IntegerField()  # Tag ID
