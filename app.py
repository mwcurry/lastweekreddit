from flask import Flask, render_template, redirect, request, flash, get_flashed_messages

from sqlalchemy import create_engine, exists, or_, and_, func, desc
from sqlalchemy.orm import sessionmaker

import engine as APIconnect

import model
from model import Base


app = Flask(__name__)
app.jinja_env.filters['date'] = APIconnect.format_datetime
app.jinja_env.filters['day'] = APIconnect.format_day
app.secret_key = 'some_secret'


@app.route('/')
def main():
	#create sessions
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	subreddit = "fitness"

	#check if we have subreddit in database
	if not (model.Submissions.checkSubreddit(session, subreddit) and (model.Comments.checkSubreddit(session, subreddit))):
		return render_template('error.html')

	#get info from model
	subreddits = model.Subreddits.getSubredditsUnique(session)
	stop, savg, sstd, sfloor = model.Submissions.getSubmissions(session,subreddit)
	ctop, cavg, cstd, cfloor, titles = model.Comments.getComments(session,subreddit)
	
	#view
	return render_template('content.html', comments=ctop, submissions=stop, subreddit = subreddit, titles = titles, menuitems = subreddits)


@app.route('/<subreddit>/')
def sub(subreddit):
	#create sessions
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	subreddit = subreddit
	
	#menu items
	subreddits = model.Subreddits.getSubredditsUnique(session)

	#check if we have subreddit in database
	if not (model.Subreddits.checkSubreddit(session, subreddit)):
		return redirect(subreddit + "/add", code=302)
	
	#check if subreddit has content, if not let user know there is no content
	if not (model.Submissions.checkSubreddit(session, subreddit) and (model.Comments.checkSubreddit(session, subreddit))):
		flash('Retrieving content from Reddit', 'alert-warning')
		return render_template('content.html', subreddit=subreddit, menuitems = subreddits)

	#get info from model

	stop, savg, sstd, sfloor = model.Submissions.getSubmissions(session,subreddit)
	ctop, cavg, cstd, cfloor, titles = model.Comments.getComments(session,subreddit)
	
	#view
	return render_template('content.html', comments=ctop, submissions=stop, subreddit = subreddit, titles = titles, menuitems = subreddits)

@app.route('/<subreddit>/add', methods=['GET', 'POST'])
@app.route('/add', methods=['GET', 'POST'])
def add_sub(subreddit=None):
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	if request.method == 'POST':
		subreddit = str(request.form['to_add'])
		if (model.Subreddits.checkSubreddit(session, subreddit)):
			flash('Subreddit already tracked.', 'alert-warning')
			return redirect(subreddit)
		else:
			#APIconnect.queryContent(session, subreddit)
			return render_template('error.html', subreddit=subreddit, modal=True)
	else:
		return render_template('error.html', subreddit=subreddit)


if __name__ == '__main__':
    app.run(debug=True)