from django.db import models


class ArticleManager(models.Manager):
    def create_article(self, title, url, imgurl, time):
        article = self.create(title=title, url=url, imgurl=imgurl, time=time)
        return article


class Article(models.Model):
    title = models.TextField(unique=True)
    url = models.TextField()
    imgurl = models.TextField()
    time = models.DateTimeField()

    objects = ArticleManager()

    def json(self):
        return {"id": self.id, "title": self.title, "url": self.url,
                     "imgurl": self.imgurl, "time": self.time}

    def __str__(self):
        return str({"id" : self.id, "title": self.title, "url": self.url,
               "imgurl": self.imgurl, "time": self.time})
