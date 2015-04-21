'''
SQL Alchemy database clases
'''

import os
import sys
import praw
import json
import pprint
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy import create_engine, exists, or_, and_, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import numpy


Base = declarative_base()


class Submissions(Base):
	__tablename__ = 'submission'
	id = Column(Text, primary_key=True)
	title = Column(Text)
	score = Column(Integer)
	author = Column(Text)
	comments = Column(Integer)
	url = Column(Text)
	gilded = Column(Integer)
	subreddit = Column(Text)

	@classmethod
	def addSubmissions(class_, subreddit, submissions):
		engine = create_engine('sqlite:///submissions.db')
		Base.metadata.bind = engine
		DBSession = sessionmaker(bind=engine)
		session = DBSession()

		#Store Submissions
		for submission in submissions:
			if session.query(exists().where(Submissions.id == submission.id)).scalar():
				print "Submission %s already exists!" % submission.id 
				continue
			new_submission = Submissions(id=submission.id, title=submission.title, score=submission.score, author=str(submission.author), comments=len(submission.comments), url=submission.url, gilded=submission.gilded, subreddit=subreddit)
			session.add(new_submission)
			print "Storing Submission %s" % submission.id

		session.commit() 

	@classmethod
	def checkSubmissions(class_, session, subreddit):
		if session.query(exists().where(Submissions.subreddit == subreddit)).scalar(): return True
		else: return False
	
	@classmethod
	def getSubmissions(class_, session, subreddit, gilded="both"):
		#todo: expand to multi subs

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

		top = session.query(Submissions).filter(Submissions.subreddit==subreddit).order_by(desc(Submissions.score)).all()

		return top, avg, std, floor



class Comments(Base):
	__tablename__ = 'comments'
	id = Column(Text, primary_key=True)
	body = Column(Text)
	score = Column(Integer)
	author = Column(Text)
	replies = Column(Integer)
	url = Column(Text)
	gilded = Column(Integer)
	#submission ID of the comment
	##Ask Abe if this should be a ForeignKey? 
	###sid = Column(String(250), ForeignKey('submission.id')) 
	sid = Column(Text)
	stitle = Column(Text)
	subreddit = Column(Text)

	
	@classmethod
	def addComments(class_, subreddit, comments):
		engine = create_engine('sqlite:///submissions.db')
		Base.metadata.bind = engine
		DBSession = sessionmaker(bind=engine)
		session = DBSession()

		#Store Submissions
		for comment in comments:
			if session.query(exists().where(Comments.id == comment.id)).scalar():
				print "Comment %s already exists!" % comment.id 
				continue
			new_comment = Comments(sid=comment.submission.id, stitle=comment.submission.title, id=comment.id, body=comment.body, score =int(comment.score), author=str(comment.author), replies=len(comment.replies), url =comment.permalink, gilded=comment.gilded, subreddit=subreddit)
			session.add(new_comment)
			print "Storing Comment %s" % comment.id

		session.commit()

	@classmethod
	def checkComments(class_, session, subreddit):
		if session.query(exists().where(Comments.subreddit == subreddit)).scalar(): return True
		else: return False

	@classmethod
	def getComments(class_, session, subreddit, gilded="both"):
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

		top = session.query(Comments).filter(and_(Comments.score > floor, filter_gilded, Comments.subreddit==subreddit)).order_by(desc(Comments.score)).all()

		return top, avg, std, floor	

if __name__ == '__main__':
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.create_all(engine)