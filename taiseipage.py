#!/usr/bin/env python2

from flask import Flask, url_for, Markup
from flask import render_template
from flask import request
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
import datetime
import os
import markdown

app = Flask(__name__)

news_dir = 'news'
screens_dir = 'static/screenshots'

class NavEntry():
    def __init__(self, name, href):
        self.href = href
        self.name = name

def get_navigation():
    return [
        NavEntry('Home', url_for('index')),
        NavEntry('News', url_for('news')),
        NavEntry('Media', url_for('media')),
        NavEntry('Github', 'http://github.com/laochailan/taisei'),
        NavEntry('Download', url_for('download'))
    ]

def load_news_file(filename):
    f = open(filename, 'r');
    date = f.readline().strip('\n')
    title = f.readline().strip('\n')
    content = f.read().decode('utf8')
    content = Markup(markdown.markdown(content))
    f.close()
    return (date, title, content, filename)

def load_news():
    news = []
    l = os.listdir(news_dir)

    for fn in l:
        news.append(load_news_file(news_dir+'/'+fn))

    news.sort(key=lambda x: x[0])
    news.reverse()
    return news

def load_screendirs():
    dirs = []
    l = os.listdir(screens_dir)

    for fn in l:
        num, caption = fn.split("_")
        screens = os.listdir(screens_dir+'/'+fn)
        dirs.append((int(num), caption, fn, screens))

    dirs.sort(key=lambda x: x[0])
    dirs.reverse()

    return dirs

def make_external(url):
    return urljoin(request.url_root, url)

@app.route('/')
def index():
    return render_template('home.html', navigation=get_navigation())

@app.route('/news')
def news():
    return render_template('news.html', navigation=get_navigation(), news=load_news())

@app.route('/news.atom')
def newsfeed():
    news = load_news()
    feed = AtomFeed('The State of Taisei',
                    feed_url=request.url, url=request.url_root)
    for article in news:
        date = datetime.datetime.strptime(article[0],'%Y-%m-%d %H:%M')
        feed.add(article[1], unicode(article[2]),
                 content_type='html',
                 author="Taisei team",
                 url=make_external("/news/"+article[3]),
                 updated=date,
                 published=date)
    return feed.get_response()


@app.route('/news/<filename>')
def news_entry(filename):
    news = load_news_file(news_dir+'/'+filename)

    return render_template('news_entry.html', navigation=get_navigation(), content=news)

@app.route('/media')
def media():
    dirs = load_screendirs()
    return render_template('media.html', navigation=get_navigation(), dirs=dirs)

@app.route('/download')
def download():
    return render_template('download.html', navigation=get_navigation())

if __name__ == "__main__":
    app.debug = True
    app.run()
