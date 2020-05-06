#!/usr/bin/env python3

from flask import Flask, url_for, Markup
from flask import render_template, redirect
from flask import request
from urllib.parse import urljoin
from feedgen.feed import FeedGenerator
import datetime
import os
import markdown

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

news_dir = 'news'
screens_dir = 'static/screenshots'


def load_news_file(filename):
    f = open(os.path.join(news_dir, filename), 'r')
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

    for fn in os.listdir(screens_dir):
        if fn == 'thumb':
            continue

        num, caption = fn.split("_")
        screens = os.listdir(os.path.join(screens_dir, fn))
        dirs.append((int(num), caption, fn, screens))

    dirs.sort(key=lambda x: x[0])
    dirs.reverse()

    return dirs


def make_external(url):
    return urljoin(request.url_root, url)


def render_template_page(page, *args, **kwargs):
    return render_template(page + '.html', *args, page=page, **kwargs)


@app.route('/')
def index():
    return render_template_page('home')


@app.route('/news')
def news():
    return render_template_page('news', news=load_news())


@app.route('/news.atom')
def newsfeed():
    def makedate(strdate):
        dt = datetime.datetime.strptime(strdate, '%Y-%m-%d %H:%M')
        return datetime.datetime(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            tzinfo=datetime.timezone.utc,
        )

    news = load_news()
    feed = FeedGenerator()
    feed.icon(make_external('static/favicon.ico'))
    feed.id(request.url)
    feed.language('en-US')
    feed.link(href=make_external('news'))
    feed.link(href=request.url, rel='self')
    feed.title('The State of Taisei')
    feed.updated(makedate(news[0][0]))

    for article in news:
        date = makedate(article[0])
        url = make_external("/news/" + article[3])

        entry = feed.add_entry()
        entry.author(name='Taisei team')
        entry.content(article[2], type='html')
        entry.id(url)
        entry.link(href=make_external("/news/" + article[3]))
        entry.published(date)
        entry.title(article[1])
        entry.updated(date)

    return feed.atom_str()


@app.route('/news/<filename>')
def news_entry(filename):
    news = load_news_file(filename)

    return render_template_page('news_entry', content=news)


@app.route('/media')
def media():
    dirs = load_screendirs()
    return render_template_page('media', dirs=dirs)


@app.route('/download')
def download(filename=None):
    return render_template_page('download')


@app.route('/play')
def play():
    return redirect("https://play.taisei-project.org/", code=301)


@app.route('/discord')
def discord():
    return redirect("https://discord.gg/JEHCMzW", code=302)


@app.route('/code')
def code():
    return redirect("https://github.com/taisei-project/taisei", code=301)


@app.route('/license')
def license():
    return render_template_page('license')


@app.template_filter('indent')
def indent_filter(s, width, *args):
    # incomplete reimplementation of the default 'indent' filter
    # because apparently it doesn't work with 'safe' correctly
    first, *rest = s.split('\n')
    return ('\n').join([first] + [' ' * width + s for s in rest])


if __name__ == "__main__":
    app.debug = True
    app.run()
