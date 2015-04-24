from flask import Flask, render_template

from sqlalchemy import create_engine, exists, or_, and_, func, desc
from sqlalchemy.orm import sessionmaker

import engine as APIconnect

import sqlalchemy_declarative as model
from sqlalchemy_declarative import Base


app = Flask(__name__)

@app.route('/')
def main():
	#create sessions
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	subreddit = 'fitness'

	#check if we have content for subreddit

	if not model.Submissions.checkSubmissions(session, subreddit) or not model.Comments.checkComments(session, subreddit):
		APIconnect.queryContent(session, subreddit)

	#get info from model
	stop, savg, sstd, sfloor = model.Submissions.getSubmissions(session,subreddit)
	ctop, cavg, cstd, cfloor = model.Comments.getComments(session,subreddit)
	
	#view
	return render_template('content.html', comments=ctop, submissions=stop, subreddit = subreddit)
	


if __name__ == '__main__':
    app.run(debug=True)