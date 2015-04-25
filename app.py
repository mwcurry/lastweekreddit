from flask import Flask, render_template, redirect

from sqlalchemy import create_engine, exists, or_, and_, func, desc
from sqlalchemy.orm import sessionmaker

import engine as APIconnect

import sqlalchemy_declarative as model
from sqlalchemy_declarative import Base


app = Flask(__name__)
app.jinja_env.filters['date'] = APIconnect.format_datetime
app.jinja_env.filters['day'] = APIconnect.format_day


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
	stop, savg, sstd, sfloor = model.Submissions.getSubmissions(session,subreddit)
	ctop, cavg, cstd, cfloor, titles = model.Comments.getComments(session,subreddit)
	
	#view
	return render_template('content.html', comments=ctop, submissions=stop, subreddit = subreddit, titles = titles)


@app.route('/<subreddit>')
def sub(subreddit):
	#create sessions
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	subreddit = subreddit


	#check if we have subreddit in database
	if not (model.Submissions.checkSubreddit(session, subreddit) and (model.Comments.checkSubreddit(session, subreddit))):
		#return render_template('error.html', subreddit=subreddit)
		return redirect(subreddit + "/add", code=302)


	#check if we have content for subreddit
	if not model.Submissions.checkSubmissions(session, subreddit) or not model.Comments.checkComments(session, subreddit):
		APIconnect.queryContent(session, subreddit)

	#get info from model
	stop, savg, sstd, sfloor = model.Submissions.getSubmissions(session,subreddit)
	ctop, cavg, cstd, cfloor, titles = model.Comments.getComments(session,subreddit)
	
	#view
	return render_template('content.html', comments=ctop, submissions=stop, subreddit = subreddit, titles = titles)

@app.route('/<subreddit>/add')
def add_sub_from_url(subreddit):
	#create sessions
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	
	return render_template('error.html', subreddit=subreddit)

@app.route('/add')
def add_sub():
	#create sessions
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	
	return render_template('error.html')



if __name__ == '__main__':
    app.run(debug=True)