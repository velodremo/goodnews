import urllib.request as ur
import json
import operator
# from boilerpipe.extract import Extractor
import bs4
import sys
import feedparser
import time
from datetime import datetime
import facebook

class session_manager:

    def __init__(self, last_ts, access_token):
        self.__arts = dict()
        self.__last_ts = last_ts
        self.__newsapi_key = '4feda0ca546e41e680d201a64ee91ae3'
        self.test_link = 'https://newsapi.org/v1/articles?source=reuters' \
                         '&sortBy' \
                         '=latest' \
                '&apiKey=4feda0ca546e41e680d201a64ee91ae3'
        self.__rss_url = ""

    def get_fb_articles(self):

        opener = ur.build_opener(ur.HTTPCookieProcessor)
        graph = facebook.GraphAPI(access_token = access_token, version='2.7')
        # page_ids = {'bbc':'228735667216', 'skynews':'164665060214766', 'buzzfeed':'618786471475708'}

        page_ids = ['155869377766434', '164665060214766', '618786471475708']
        # page_ids = ['618786471475708']

        posts_list = list()

        for id in page_ids:
            posts_dict = dict()
            posts = graph.get_object(id + '?fields=posts')
            for post in posts['posts']['data']:
                id = post['id']
                posts_dict[id] = dict()
                reacts = graph.get_object(id + '?fields=reactions'
                                               '.type(LOVE).limit(0).summary(total_count).as(reactions_love),reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad), reactions.type(ANGRY).limit(0).summary(total_count).as(reactions_angry), reactions.type(LIKE).limit(0).summary(total_count).as(reactions_like)')
                # print(reacts)
                for reaction in reacts.items():
                    if reaction[0] != 'id':
                        posts_dict[id][reaction[0]] = reaction[1]['summary']['total_count']
            posts_list.append(posts_dict)

        post_list = []

        for posts_dict in posts_list:
            for post in posts_dict.items():
                id = post[0]
                sum_reacts = post[1]['reactions_haha'] + post[1]['reactions_love'] + \
                             post[1]['reactions_wow'] + post[1]['reactions_sad'] + post[
                                 1]['reactions_angry']
                sum_happy = post[1]['reactions_love'] + post[1]['reactions_haha']
                happy_percent = float(sum_happy) / (sum_reacts + 1)
                if happy_percent > 0.7 and sum_reacts > 50:
                    props = graph.get_object(id + '?fields=type,created_time,link,picture')
                    if props['type'] == 'link':
                        html = opener.open(props['link']).read()
                        html = html.decode('utf-8')
                        soup = bs4.BeautifulSoup(html, 'html.parser')
                        # print(props['link'])
                        title = soup.title.string
                        ts = props['created_time'][:-5] + 'Z'
                        if ts > self.__last_ts:
                            post_list.append((title, props['link'], props['picture'], ts))
        if len(post_list) > 0:
            self.__last_ts = max(map(lambda a: a[3], post_list))
        return post_list

    def get_sentiment(self, text: str):
        try:
            text_for_url = ur.quote(text)
            request_url = "https://api.meaningcloud.com/sentiment-2.1?key=114149df7fd9d4c143aaaadb6c6605de&of=json" \
                          "&model=general&lang=en&txt="

            response = ur.urlopen(request_url + text_for_url)
            json_response = response.read().decode('utf-8')
            parsed_json = json.loads(json_response)
            # print(parsed_json)
            return (parsed_json["score_tag"])
        except Exception as e:
            print("ERROR: ",e)
            return "NOT"


    # returns string with the first 2500 chars of the text of the article in the url.
    # works for nytimes only!!
    def get_article_text(self, url):
        article_text = str()
        try:
            print(url)
            opener = ur.build_opener(ur.HTTPCookieProcessor)
            html = opener.open(url).read()
            html = html.decode('utf-8')
            soup = bs4.BeautifulSoup(html, 'html.parser')
            for p in soup.find_all('p',
                                   {"class": "mol-para-with-font"}):
                article_text += p.get_text()
            #
            #     # article_text += p.get_text()

            for p in soup.find_all('p'):
                if p.parent.name == 'div' and ('itemprop' in p.parent.attrs):
                    if p.parent['itemprop'] == 'articleBody':
                        article_text += p.get_text()

        except Exception as e:
            print('ERROR: ', e)

        article_text.replace('\n', '')
        end = article_text.find(' ', 2500)
        return article_text[:end]

    def get_new_json(self, link: str):
        """
        Try to get a new json object from a link using the newsAPI app
        :param link: a full request link
        :return: a json object
        """
        # print(link)
        j_obj = None
        try:
            res = ur.urlopen(link).read().decode('utf-8')
            j_obj = json.loads(res)
            # print(j_obj)

        except Exception as e:
            print("ERROR: ")
            print(e)

        return j_obj

    # res = urllib.request.urlopen(link)

    def get_articles(self, j_obj):
        """
        Return a list of parsed articles from the current json object
        :param j_obj:
        :return:
        """
        articles = []
        try:
            articles = j_obj['articles']
        except Exception as e:
            print(e)

        # print (articles)
        for article in articles[:30]:
            # if article['publishedAt'] > self.__last_ts:
                url = article['url']
                print(url)
                title = article['title']
                urlToImage = article['urlToImage']
                publishedAt = article['publishedAt']
                txt = self.get_article_text(url)
                # print (txt)
                # sentiment = self.get_sentiment(txt)
                sentiment = "NP=P"
                self.__arts[url] = (title, urlToImage, publishedAt, sentiment)

        # self.__last_ts = max(self.__arts.items(), key=operator.itemgetter(1))[
        #     1][2]
        # print("CUR TIMESTAMP: " + self.__last_ts)

    # def extract_article(self):
    #     test_url = list(self.__arts.keys())[0]
    #     print(test_url)
    #     opener = ur.build_opener(ur.HTTPCookieProcessor)
    #     html = opener.open(test_url).read().decode('utf-8')
    #     extractor = Extractor(html=html)
    #     extracted_text = extractor.getText()
    #     return (extracted_text)

    def get_rss_articles(self):
        parser = feedparser.parse(self.__rss_url)
        articles = list()
        num_of_articles = 0
        for article in parser['entries']:
            if num_of_articles > 1000:
                break
            pub_date = str(datetime.strptime(article['published'][:-6], '%a, '
                                                                     '%d %b %Y %H:%M:%S'))
            if pub_date >= self.__last_ts:
            # if True:
                num_of_articles += 1
                text = self.get_article_text(article['link'])
                if text == "":
                    sentiment = "NOT"
                else:
                    sentiment = self.get_sentiment(text)
                    # sentiment = "P"
                articles.append((article['title'],article['link'], article['media_thumbnail'][5]['url'],
                             pub_date, sentiment))
        self.__last_ts = max(map(lambda a: a[3], articles))
        print("CUR TIMESTAMP: " + self.__last_ts)
        return articles

    def get_cnn_rss_articles(self):
        parser = feedparser.parse("http://rss.cnn.com/rss/cnn_latest.rss")
        articles = list()
        num_of_articles = 0
        for article in parser['entries']:
            if num_of_articles > 100:
                break
            pub_date = str(datetime.strptime(article['published'][:-4], '%a, '
                                                                        '%d %b %Y %H:%M:%S'))
            if pub_date >= self.__last_ts:
                num_of_articles += 1
                link = article['link']
                text = self.get_cnn_article_text(article['links'][0]['href'])
                if text == "":
                    sentiment = "NOT"
                else:
                    sentiment = self.get_sentiment(text)
                img_link = ''
                if 'media_content' in article:
                    imgs = [im['url'] for im in article['media_content'] if im['width'] == 300 and im['height'] == 250]
                    if len(imgs) > 0:
                        img_link = imgs[0]['url']
                    else:
                        img_link = article['media_content'][5]['url']
                articles.append((article['title'], link, img_link, pub_date, sentiment))
        self.__last_ts = max(map(lambda a: a[3], articles))
        return articles

    def get_cnn_article_text(self, url):
        article_text = str()
        try:
            opener = ur.build_opener(ur.HTTPCookieProcessor)
            html = opener.open(url).read()
            html = html.decode('utf-8')
            soup = bs4.BeautifulSoup(html, 'html.parser')
            for p in soup.find_all('div',
                                   {"class": "zn-body__paragraph"}):
                article_text += p.get_text()
        except Exception as e:
            print('ERROR: ', e)

        article_text.replace('\n', '')
        end = article_text.find(' ', 2500)
        return article_text[:end]

    def run_new_session(self):
        """
        run a new session
        :return:
        """
        # j_obj = self.get_new_json(self.test_link)
        # print(__arts)
        # self.extract_article()
        # articles = self.get_cnn_rss_articles()
        # filtered = list(map(lambda a: a[:-1], (filter(lambda x: x[4].startswith("P"), articles))))
        return self.get_fb_articles(), self.__last_ts

    def __parse_date(self, param):
        pass


if __name__ == '__main__':
    # latest timestamp
    last_ts = '2017-01-18 10:00:56'
    sm = session_manager(last_ts)
    sm.run_new_session()
    # print(sm.get_rss_articles())
