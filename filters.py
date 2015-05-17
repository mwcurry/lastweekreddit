import re
from jinja2 import evalcontextfilter, Markup, escape
import time

#Jinja filters
def format_datetime(value):
    date = time.strftime('%m-%d-%Y', time.gmtime(value))
    return date
def format_day(value):
    day = time.strftime("%A", time.gmtime(value/1000))
    return day
def reddit_links(value):
	link_re = re.compile(r'\[(.*?)\]\((.*?)\)+')
	for find in re.findall(link_re, value):
		url = '<a href =%s target="_blank">%s</a>' % (find[1], find[0])
		link_text = "[%s](%s)" % (find[0], find[1])
		value = value.replace(link_text, url)
	return value
def str(value):
	if type(value) == str:
		return True
	else:
		return False

@evalcontextfilter
def nl2br(eval_ctx, value):
	paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
	result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', Markup('<br>\n'))
		for p in paragraph_re.split(escape(value)))
	if eval_ctx.autoescape:
		result = Markup(result)
	return result