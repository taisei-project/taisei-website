#!/usr/bin/env python2

from flask import Flask, url_for, Markup
from flask import render_template
import os
import markdown

app = Flask(__name__)

news_dir = 'news'

class NavEntry():
	def __init__(self, name, href):
		self.href = href
		self.name = name

def get_navigation():
	return [
		NavEntry('Home', url_for('index')),
		NavEntry('News', url_for('news')),
		NavEntry('Media', url_for('media')),
		NavEntry('Development', 'http://github.com/laochailan/taisei'),
		NavEntry('Download', url_for('download'))
	]

def load_news_file(filename):
	f = open(filename, 'r');
	date = f.readline()
	title = f.readline()
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

@app.route('/')
def index():
	return render_template('home.html', navigation=get_navigation())

@app.route('/news')
def news():
	return render_template('news.html', navigation=get_navigation(), news=load_news())

@app.route('/news/<filename>')
def news_entry(filename):
	news = load_news_file(news_dir+'/'+filename)

	return render_template('news_entry.html', navigation=get_navigation(), content=news)

@app.route('/media')
def media():
	return render_template('media.html', navigation=get_navigation())

@app.route('/download')
def download():
	return render_template('download.html', navigation=get_navigation())

#if __name__ == "__main__":
	#app.debug = True
	#app.run()
