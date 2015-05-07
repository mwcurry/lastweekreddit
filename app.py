from flask import Flask, render_template, redirect, request, flash, get_flashed_messages

from sqlalchemy import create_engine, exists, or_, and_, func, desc
from sqlalchemy.orm import sessionmaker

import engine as APIconnect
from celeryconfig import celapp
import filters
import model
from model import Base


app = Flask(__name__)
app.jinja_env.filters['date'] = filters.format_datetime
app.jinja_env.filters['day'] = filters.format_day
app.jinja_env.filters['redditlink'] = filters.reddit_links
app.jinja_env.filters['nl2br'] = filters.nl2br
app.secret_key = 'some_secret'


@app.route('/')
def main():
	#create sessions
	engine = create_engine('sqlite:///submissions.db')
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	#menu items
	menuitems = model.Subreddits.getSubredditsUnique(session)
	
	subreddits = model.Subreddits.getSubreddits(session)
	
	#view
	return render_template('home.html', subreddits = subreddits, menuitems = menuitems)


@app.route('/<subreddit>/')
def sub(subreddit):
	#create sessions
	engine = create_engine('sqlite:///submissions.db')
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	
	
	#check if we have subreddit in database
	if not (model.Subreddits.checkSubreddit(session, subreddit)):
		return redirect(subreddit + "/add", code=302)
	
	#menu items
	subreddits = model.Subreddits.getSubredditsUnique(session)
	sub = model.Subreddits.getSubreddit(session, subreddit)

	
	#check if subreddit has content, if not let user know there is no content
	if not (model.Submissions.checkSubreddit(session, subreddit) and model.Comments.checkSubreddit(session, subreddit)):
		flash('Retrieving content from Reddit', 'alert-warning')
		return render_template('content.html', subreddit=sub, menuitems = subreddits, progress = True)

	#get info from model

	stop, savg, sstd, sfloor = model.Submissions.getSubmissions(session,subreddit)
	ctop, cavg, cstd, cfloor = model.Comments.getComments(session,subreddit)

	titles = {}

	for c in ctop:
		if c.stitle in titles:
			titles[c.stitle][1] += 1
			continue
		titles[c.stitle] = [c.sid, 1]
	
	#view
	return render_template('content.html', comments=ctop, submissions=stop, subreddit = sub, titles = titles, menuitems = subreddits)

@app.route('/<subreddit>/add', methods=['GET', 'POST'])
@app.route('/add', methods=['GET', 'POST'])
def add_sub(subreddit=None):
	engine = create_engine('sqlite:///submissions.db')
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	#check if we have subreddit in database and foward to subreddit page
	if  (model.Subreddits.checkSubreddit(session, subreddit)):
		return redirect(subreddit, code=302)

	#menu items
	subreddits = model.Subreddits.getSubredditsUnique(session)

	if request.method == 'POST':
		subreddit = str(request.form['to_add'])
		if (model.Subreddits.checkSubreddit(session, subreddit)):
			flash('Subreddit already tracked.', 'alert-warning')
			return redirect(subreddit)
		else:
			model.Subreddits.quickAddSubreddit(session, subreddit)
			APIconnect.queryContent.delay(None, subreddit)
			return redirect(subreddit)
	else:
		return render_template('error.html', subreddit=subreddit, menuitems = subreddits)


if __name__ == '__main__':
    app.run(debug=True)