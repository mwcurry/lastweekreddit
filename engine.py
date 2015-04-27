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

def queryContent(session, subreddit):
	user_agent = "Weekly Subreddit Summary by /u/iwasdaydreamnation"
	r = praw.Reddit(user_agent=user_agent)
	gilded = r.get_comments(subreddit, gilded_only = True, limit=50)
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
		submissions.append(submission)
		forest_comments = submission.comments
		flat_comments = praw.helpers.flatten_tree(submission.comments)
		for comment in flat_comments:
			if not isinstance(comment, praw.objects.Comment): continue
			comments.append(comment)
		
		'''# Get Top Comments
		##submission.replace_more_comments(limit=None, threshold =0)
		#http://praw.readthedocs.org/en/latest/pages/code_overview.html#praw.objects.Submission.replace_more_comments
		for comment in submission.comments:
			if not isinstance(comment, praw.objects.Comment): continue
			comments.append(comment)'''

	# Store comments & submissions lists in database comments
	model.Submissions.addSubmissions(session, subreddit, submissions)
	model.Comments.addComments(session, subreddit, comments)
	model.Subreddits.addSubreddit(session, sub)


#Jinja filters
def format_datetime(value):
    date = time.strftime('%m-%d-%Y', time.gmtime(value))
    return date
def format_day(value):
    day = time.strftime("%A", time.gmtime(value/1000))
    return day


if __name__=='__main__': 
	engine = create_engine('sqlite:///submissions.db')
	model.Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	subreddit = "asoiaf"
	queryContent(session, subreddit)