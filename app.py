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

	#check if we have content for subreddit

	if not model.Submissions.checkSubmissions(session, subreddit) or not model.Comments.checkComments(session, subreddit):
		APIconnect.queryContent(session, subreddit)

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


	#check if we have subreddit in database
	if not (model.Subreddits.checkSubreddit(session, subreddit):
		return redirect(subreddit + "/add", code=302)
	
	return redirect(subreddit + "/add", code=302)
	'''if not (model.Submissions.checkSubreddit(session, subreddit) and (model.Comments.checkSubreddit(session, subreddit))):
		#return render_template('error.html', subreddit=subreddit)
		return redirect(subreddit + "/add", code=302)'''

	#get info from model
	subreddits = model.Subreddits.getSubredditsUnique(session)
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
		if (model.Submissions.checkSubreddit(session, subreddit) and (model.Comments.checkSubreddit(session, subreddit))):
			flash('Subreddit already tracked.', 'alert-warning')
			return redirect(subreddit)
		else:
			#APIconnect.queryContent(session, subreddit)
			return render_template('error.html', subreddit=subreddit, modal=True)
	else:
		return render_template('error.html', subreddit=subreddit)


if __name__ == '__main__':
    app.run(debug=True)