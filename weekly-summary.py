'''
Script to summarize the top submissions & comments for a subreddit in the past week

'''

import praw
import json
import pprint
from operator import itemgetter
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
 
from sqlalchemy_declarative import Submissions, Comments, Base

def getSubmissions(subreddit):
	#todo: expand to multi subs
	#>>> submissions = r.get_subreddit('python').get_top(limit=10)
	sub = r.get_subreddit(subreddit)
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	#Get Top Submissions & Comments
	for submission in sub.get_top_from_week(limit=3):
		if session.query(exists().where(Submissions.id == submission.id)).scalar():
			print "Submission %s already exists!" % submission.id 
			continue
		new_submission = Submissions(id=submission.id, title=submission.title, score=submission.score, author=str(submission.author), comments=len(submission.comments), url=submission.url, gilded=submission.gilded)
		session.add(new_submission)
		session.commit()
		print "Adding Submission %s" % submission.id
		
		# Get Top Comments
		##submission.replace_more_comments(limit=None, threshold =0) #http://praw.readthedocs.org/en/latest/pages/code_overview.html#praw.objects.Submission.replace_more_comments
		
		for comment in submission.comments:
			if not isinstance(comment, praw.objects.Comment): continue
			if session.query(exists().where(Comments.c_id == comment.id)).scalar(): 
				print "Comment %s already exists!" % comment.id
				continue
			new_comment = Comments(c_sid=submission.id, c_id=comment.id, c_body=comment.body, c_score =int(comment.score), c_author=str(comment.author), c_replies=len(comment.replies), c_url =comment.permalink, c_gilded=comment.gilded)
			session.add(new_comment)
			session.commit()
			print "Adding Comment %s" % comment.id


def getGilded(subreddit):
	sub = r.get_comments(subreddit, gilded_only = True, limit=3)
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	for item in sub:
		#check if gilded item is comment
		if hasattr(item,'_submission'):
			new_gilded_comment = Comments(c_sid=item.link_id, c_id=item.id, c_body=item.body, c_score =int(item.score), c_author=str(item.author), c_replies=len(item.replies), c_url =item.permalink, c_gilded=item.gilded)
			session.add(new_gilded_comment)
			session.commit()

		if hasattr(item,'_comments'):
			new_gilded_submissions = Submissions(id=item.id, title=item.title, score=item.score, author=str(item.author), comments=item.comments, url=item.url, gilded=item.gilded)
			session.add(new_gilded_comment)
			session.commit()



def sortComments(submissions, comments):
	sorted_top_comments = sorted(comments, key=itemgetter(3), reverse=True)
	sorted_top_convos = sorted(comments, key=itemgetter(5), reverse=True)
	sorted_top_submissions = sorted(submissions, key=itemgetter(2), reverse=True)
	

	pprint.pprint(sorted_top_comments[0:10])
	print_break()
	for x in range(15):
		if sorted_top_convos[x] in sorted_top_comments[0:10]: continue
		pprint.pprint(sorted_top_convos[x])


def print_break():
	print "\n" * 2, "*"*40, "\n" * 2
		



if __name__=='__main__': 
	user_agent = "Subreddit Analyzer by /u/iwasdaydreamnation"
	r = praw.Reddit(user_agent=user_agent)
	#submissions, comments = getSubmissions('fitness')
	#sortComments(submissions, comments)
	getSubmissions('fitness')