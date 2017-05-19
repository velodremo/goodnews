from goodnews import session_manager as sm
import urllib.request as req
import time
# import httplib2
# http://132.65.125.102:8080/add/title/http://www.google2.com/img/2017-05-02T00:00:00Z  *** example
while True:
    print('starts session')
    request_url = "http://132.65.125.102:8080/add"
    with open('ts.txt', 'r+') as ts_file:
        ts = ts_file.readline().strip()
        manager = sm.session_manager(ts)
        articles, new_ts = manager.run_new_session()
        for article in articles:
            headline = req.quote(article[0])
            article_link = req.quote(article[1][7:])
            img_link = req.quote(article[2][7:])
            date = article[3]

            url = request_url + "//" + headline + "//" + article_link + "//" + img_link + "//" + date
            print(url)
            try:
                req.urlopen(url)
            except Exception as e:
                print('ERROR: ', e)

        # ts_file.seek(0)
        # ts_file.truncate()
        # ts_file.write(new_ts)
        ts_file.close()
    print("going to sleep")
    time.sleep(1000)
