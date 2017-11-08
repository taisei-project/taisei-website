#!/usr/bin/env python3

from flask import Flask, url_for, Markup
from flask import render_template
from flask import request
from urllib.parse import urljoin
from werkzeug.contrib.atom import AtomFeed
import datetime
import os
import markdown

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

news_dir = 'news'
screens_dir = 'static/screenshots'

def load_news_file(filename):
    f = open(os.path.join(news_dir, filename), 'r');
    date = f.readline().strip('\n')
    title = f.readline().strip('\n')
    content = f.read()
    content = Markup(markdown.markdown(content))
    f.close()
    return (date, title, content, filename)

def load_news():
    news = []
    l = os.listdir(news_dir)

    for fn in l:
        news.append(load_news_file(fn))

    news.sort(key=lambda x: x[0])
    news.reverse()
    return news

def load_screendirs():
    dirs = []
    l = os.listdir(screens_dir)

    for fn in l:
        num, caption = fn.split("_")
        screens = os.listdir(os.path.join(screens_dir, fn))
        dirs.append((int(num), caption, fn, screens))

    dirs.sort(key=lambda x: x[0])
    dirs.reverse()

    return dirs

def make_external(url):
    return urljoin(request.url_root, url)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/news')
def news():
    return render_template('news.html', news=load_news())

@app.route('/news.atom')
def newsfeed():
    news = load_news()
    feed = AtomFeed('The State of Taisei',
                    feed_url=request.url, url=request.url_root)
    for article in news:
        date = datetime.datetime.strptime(article[0],'%Y-%m-%d %H:%M')
        feed.add(article[1], article[2],
                 content_type='html',
                 author="Taisei team",
                 url=make_external("/news/"+article[3]),
                 updated=date,
                 published=date)
    return feed.get_response()


@app.route('/news/<filename>')
def news_entry(filename):
    news = load_news_file(filename)

    return render_template('news_entry.html', content=news)

@app.route('/media')
def media():
    dirs = load_screendirs()
    return render_template('media.html', dirs=dirs)

@app.route('/download')
def download():
    return render_template('download.html')

if __name__ == "__main__":
    app.debug = True
    app.run()
