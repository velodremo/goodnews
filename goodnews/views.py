import json
from django.http import JsonResponse
from django.http import HttpResponse
from . import models
import django.db


# def add(request, title, url, imgurl, date):
def add(request, text):
    # print('in add')
    title, url, imgurl, date = tuple(text[1:].split('//'))
    print(title, url, imgurl, date)
    try:
        article = models.Article.objects.create_article(title, url, imgurl,
                                                        date)
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(article)


def get_json(articles):
    return {"articles": [article.json() for article in articles]}


def get(request, date):
    try:
        articles = models.Article.objects.filter(time__gt=date).order_by('-time')
        json = get_json(articles)

    except Exception as e:
        return HttpResponse(e)

    return JsonResponse(json)
