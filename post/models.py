from django.db import models
from django.utils.functional import cached_property


class Article(models.Model):
    title = models.CharField(max_length=128)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    @property
    def tags(self):
        article_tags = ArticleTags.objects.filter(aid=self.id).only('tid')
        tid_list = [at.tid for at in article_tags]
        return Tag.objects.filter(id__in=tid_list)

    def update_article_tags(self, tag_names):
        old_tag_names = set(tag.name for tag in self.tags)
        new_tag_names = set(tag_names) - old_tag_names
        need_delete = old_tag_names - set(tag_names)

        # 创建新的关系
        Tag.create_new_tags(new_tag_names, self.id)
        # 删除旧关系
        need_delete_tids = [t.id for t in Tag.objects.filter(name__in=need_delete).only('id')]
        articletags = ArticleTags.objects.filter(tid__in=need_delete_tids)
        for atag in articletags:
            atag.delete()

        # 取出需要删除的关系的 tid
        # need_delete = []
        # for tag in self.tags:
        #     if tag.name not in tag_names:
        #         need_delete.append(tag.id)
        #     else:
        #         tag_names.remove(tag.name)  # 需要保留的, 剔除掉了
        # 删除旧的关系
        # articletags = ArticleTags.objects.filter(tid__in=need_delete)
        # for atag in articletags:
        #     atag.delete()

        # 创建新的 Tag 和 关系
        # Tag.create_new_tags(tag_names, self.id)


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
        tags = cls.objects.filter(name__in=tag_names)
        for t in tags:
            ArticleTags.objects.update_or_create(aid=aid, tid=t.id)
        return tags

    @cached_property
    def articles(self):
        aid_list = [at.aid for at in ArticleTags.objects.filter(tid=self.id).only('aid')]
        return Article.objects.filter(id__in=aid_list)


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
