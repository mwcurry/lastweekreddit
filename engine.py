'''
Script to summarize the top submissions & comments for a subreddit in the past week

'''

import praw
import json
import pprint
from operator import itemgetter
from sqlalchemy import create_engine, exists, or_, and_, func, desc
from sqlalchemy.orm import sessionmaker
import numpy
 
from sqlalchemy_declarative import Submissions, Comments, Base

def getSubmissions(subreddit):
	#todo: expand to multi subs
	#>>> submissions = r.get_subreddit('python').get_top(limit=10)
	user_agent = "Weekly Subreddit Summary by /u/iwasdaydreamnation"
	r = praw.Reddit(user_agent=user_agent)
	sub = r.get_subreddit(subreddit)
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	#Get Top Submissions & Comments
	for submission in sub.get_top_from_week(limit=10):
		if session.query(exists().where(Submissions.id == submission.id)).scalar():
			print "Submission %s already exists!" % submission.id 
			continue
		new_submission = Submissions(id=submission.id, title=submission.title, score=submission.score, author=str(submission.author), comments=len(submission.comments), url=submission.url, gilded=submission.gilded, subreddit=subreddit)
		session.add(new_submission)
		session.commit()
		print "Adding Submission %s" % submission.id
		
		# Get Top Comments
		##submission.replace_more_comments(limit=None, threshold =0) #http://praw.readthedocs.org/en/latest/pages/code_overview.html#praw.objects.Submission.replace_more_comments
		
		for comment in submission.comments:
			if not isinstance(comment, praw.objects.Comment): continue
			if session.query(exists().where(Comments.id == comment.id)).scalar(): 
				print "Comment %s already exists!" % comment.id
				continue
			new_comment = Comments(sid=submission.id, id=comment.id, body=comment.body, score =int(comment.score), author=str(comment.author), replies=len(comment.replies), url =comment.permalink, gilded=comment.gilded, subreddit=subreddit)
			session.add(new_comment)
			session.commit()
			print "Adding Comment %s" % comment.id
	session.close()


def getGilded(subreddit):
	user_agent = "Weekly Subreddit Summary by /u/iwasdaydreamnation"
	r = praw.Reddit(user_agent=user_agent)
	sub = r.get_comments(subreddit, gilded_only = True, limit=20)
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	for item in sub:
		#check if gilded item is comment
		if hasattr(item,'_submission'):
			if session.query(exists().where(Comments.id == item.id)).scalar(): 
				print "Comment %s already exists!" % item.id
				continue
			new_gilded_comment = Comments(sid=item.link_id, id=item.id, body=item.body, score =int(item.score), author=str(item.author), replies=len(item.replies), url =item.permalink, gilded=item.gilded, subreddit=subreddit)
			session.add(new_gilded_comment)
			session.commit()
			print "Adding Comment %s" % item.id

		if hasattr(item,'_comments'):
			if session.query(exists().where(Submissions.id == item.id)).scalar(): 
				print "Submission %s already exists!" % item.id
				continue
			new_gilded_submission = Submissions(id=item.id, title=item.title, score=item.score, author=str(item.author), comments=len(item.comments), url=item.url, gilded=item.gilded, subreddit=subreddit)
			session.add(new_gilded_submission)
			session.commit()
			print "Adding Submission %s" % item.id
	session.close()



def TopComments(subreddit, gilded="both"):
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	#Check if comments exist for subreddit
	if not session.query(exists().where(Comments.subreddit == subreddit)).scalar():
		print "Does not exist in db"
		getGilded(subreddit)

	#Check if submissions exist for subreddit
	if not session.query(exists().where(Submissions.subreddit == subreddit)).scalar():
		print "Does not exist in db"
		getSubmissions(subreddit)

	
	#Define Top Comments as those that are at least 1 standard deviation above the average gilded commentan

	## Determine if we need to return all comments, gilded only, or non gilded depending on what user passes in	
	if gilded == True:
		filter_gilded = "Comments.gilded == 1"
	elif gilded == False:
		filter_gilded = "Comments.gilded == 0"
	elif gilded == "both":
		filter_gilded = True

	## Actual score calculations

	all_scores = session.query(Comments).filter(filter_gilded).with_entities(Comments.score)
	
	list_all_scores =  list(all_scores)
	avg =  numpy.average(list_all_scores)
	std = numpy.std(list_all_scores)
	floor = round(avg + std, 0)

	top = session.query(Comments).filter(and_(Comments.score > floor, filter_gilded, Comments.subreddit==subreddit)).all()

	return top, avg, std, floor
	session.close()


## Todo, combine TopSubmisisons & TopComments
def TopSubmissions(subreddit, gilded="both"):
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	#Check if comments exist for subreddit
	if not session.query(exists().where(Comments.subreddit == subreddit)).scalar():
		print "Does not exist in db"
		getGilded(subreddit)

	#Check if submissions exist for subreddit
	if not session.query(exists().where(Submissions.subreddit == subreddit)).scalar():
		print "Does not exist in db"
		getSubmissions(subreddit)

	
	## Determine if we need to return all comments, gilded only, or non gilded depending on what user passes in	
	if gilded == True:
		filter_gilded = "Submissions.gilded == 1"
	elif gilded == False:
		filter_gilded = "Submissions.gilded == 0"
	elif gilded == "both":
		filter_gilded = True

	## Actual score calculations

	all_scores = session.query(Submissions).filter(filter_gilded).with_entities(Submissions.score)
	
	list_all_scores =  list(all_scores)
	avg =  numpy.average(list_all_scores)
	std = numpy.std(list_all_scores)
	floor = round(avg + std, 0)

	top = session.query(Submissions).filter(Submissions.subreddit==subreddit).all()

	return top, avg, std, floor
	session.close()



def print_break():
	print "\n" * 2, "*"*40, "\n" * 2
		


if __name__=='__main__': 
	user_agent = "Subreddit Analyzer by /u/iwasdaydreamnation"
	r = praw.Reddit(user_agent=user_agent)
	TopComments('fitness', 'both')
	#getSubmissions('fitness')
	#getGilded('fitness')