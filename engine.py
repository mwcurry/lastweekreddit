'''
Script to summarize the top submissions & comments for a subreddit in the past week

'''

import praw
import json
import pprint
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import time
 
import model

from celeryconfig import celapp


@celapp.task
def queryContent(session, subreddit):
	engine = create_engine('sqlite:///submissions.db')
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	print "Connecting to Reddit"
	user_agent = "Weekly Subreddit Summary by /u/iwasdaydreamnation"
	r = praw.Reddit(user_agent=user_agent)
	start = time.time()
	gilded = r.get_comments(subreddit, gilded_only = True, limit=200)
	sub = r.get_subreddit(subreddit)

	comments = []
	submissions = []

	#Get Gold Comments & Submissions
	for item in gilded:
		#check if gilded item was posted within last 7 days
		if time.time() - item.created_utc < (60 * 60 * 24 * 7):
			#check if gilded item is comment
			if hasattr(item,'_submission'):
				comments.append(item)

			if hasattr(item,'_comments'):
				submissions.append(item)


	#Get Top Submissions & Comments
	for submission in sub.get_top_from_week(limit=10):
		item_time = time.time()
		submissions.append(submission)
		forest_comments = submission.comments
		flat_comments = praw.helpers.flatten_tree(submission.comments)
		for comment in flat_comments:
			if not isinstance(comment, praw.objects.Comment): continue
			comments.append(comment)
	

	# Store comments & submissions lists in database comments
	model.Submissions.addSubmissions(session, subreddit, submissions)
	model.Comments.addComments(session, subreddit, comments)
	model.Subreddits.updateSubreddit(session, sub)

@celapp.task
def updateAllSubreddits(session=None):
	if not session:
		engine = create_engine('sqlite:///submissions.db')
		model.Base.metadata.bind = engine
		DBSession = sessionmaker(bind=engine)
		session = DBSession()

	for subreddit in model.Subreddits.getSubredditsUnique(session):
		print "Updating %s" % subreddit
		model.Comments.removeComments(session, subreddit)
		model.Submissions.removeSubmissions(session, subreddit)
		print "Getting content"
		queryContent(session, subreddit)

@celapp.task
def updateSubreddit(subreddit, session=None):
	if not session:
		engine = create_engine('sqlite:///submissions.db')
		model.Base.metadata.bind = engine
		DBSession = sessionmaker(bind=engine)
		session = DBSession()

	print "Updating %s" % subreddit
	model.Comments.removeComments(session, subreddit)
	model.Submissions.removeSubmissions(session, subreddit)
	print "Getting content"
	queryContent(session, subreddit)
	

if __name__=='__main__': 
	engine = create_engine('sqlite:///submissions.db')
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	updateContent().delay()