'''
SQL Alchemy database clases
'''

import os
import sys
import praw
from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime, ForeignKey
from sqlalchemy import create_engine, exists, or_, and_, func, desc, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import numpy

import time

Base = declarative_base()

class Subreddits(Base):
	__tablename__ = 'subreddits'
	id = Column(Text)
	title = Column(Text, primary_key=True)
	url = Column(Text)
	description = Column(Text)
	added = Column(DateTime)
	updated = Column(DateTime)

	@classmethod
	def addSubreddit(class_, session, subreddit):
		if session.query(exists().where(Subreddits.title == subreddit.display_name.lower())).scalar():
			print "Subreddit %s already exists!" % subreddit.display_name.lower() 
		else:
			new_subreddit = Subreddits(
								id=subreddit.id,
								title=subreddit.display_name.lower(),
								url=subreddit._url,
								description=subreddit.description,
								added=datetime.utcnow(),
								updated=datetime.utcnow())
			session.add(new_subreddit)
			session.commit()
			print "Storing Subreddit %s" % subreddit.display_name

	@classmethod
	def checkSubreddit(class_, session, subreddit):
		if session.query(exists().where(Subreddits.title == subreddit)).scalar(): return True
		else: return False

	@classmethod
	def getSubredditsUnique(class_, session):
		query = session.query(Subreddits.title.distinct().label("name"))
		subs = [row.name.lower() for row in query.all()]
		return subs

	@classmethod
	def updateSubreddit(class_, session, subreddit):
		if not (session.query(exists().where(Subreddits.title == subreddit.display_name.lower())).scalar()):
			print "Subreddit %s doesn't exists. Adding it." % subreddit.display_name.lower() 
			Subreddits.addSubreddit(session, subreddit)
		else:
			update(Subreddits).where(Subreddits.c.title==subreddit).values(
								id=subreddit.id,
								url=subreddit._url,
								description=subreddit.description,
								added=datetime.utcnow(),
								updated=datetime.utcnow())
			session.commit()
			print "Updating Subreddit %s" % subreddit.display_name


class Submissions(Base):
	__tablename__ = 'submissions'
	id = Column(Text, primary_key=True)
	title = Column(Text)
	score = Column(Integer)
	author = Column(Text)
	comments = Column(Integer)
	url = Column(Text)
	permalink = Column(Text)
	domain = Column(Integer)
	gilded = Column(Integer)
	subreddit = Column(Text, ForeignKey("subreddits.title"))
	created_utc = Column(Integer)

	@classmethod
	def addSubmissions(class_, session, subreddit, submissions):
		#Store Submissions
		for submission in submissions:
			if session.query(exists().where(Submissions.id == submission.id)).scalar():
				print "Submission %s already exists!" % submission.id 
				continue
		
			new_submission = Submissions(id=submission.id,
										title=submission.title,
										score=submission.score,
										author=str(submission.author),
										comments=len(submission.comments),
										url=submission.url,
										permalink=submission.permalink,
										domain = submission.domain,
										gilded=submission.gilded,
										subreddit=subreddit,
										created_utc=submission.created_utc)
			session.add(new_submission)
			print "Storing Submission %s" % (submission.id)

		session.commit() 

	@classmethod
	def checkSubmissions(class_, session, subreddit):
		if session.query(exists().where(Submissions.subreddit == subreddit)).scalar(): return True
		else: return False

	@classmethod
	def checkSubreddit(class_, session, subreddit):
		if session.query(exists().where(Submissions.subreddit == subreddit)).scalar(): return True
		else: return False
	
	@classmethod
	def getSubmissions(class_, session, subreddit):
		#todo: expand to multi subs

		## Actual score calculations
		all_scores = session.query(Submissions).with_entities(Submissions.score)
		
		list_all_scores =  list(all_scores)
		avg =  numpy.average(list_all_scores)
		std = numpy.std(list_all_scores)
		floor = round(avg + std, 0)

		top = session.query(Submissions).filter(Submissions.subreddit==subreddit).order_by(desc(Submissions.score)).all()

		return top, avg, std, floor

	@classmethod
	def removeSubmissions(class_, session, subreddit):
		session.query(Submissions).filter(Submissions.subreddit==subreddit).delete()
		session.commit()



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
	subreddit = Column(Text, ForeignKey("subreddits.title"))
	created_utc = Column(Integer)

	
	@classmethod
	def addComments(class_, session, subreddit, comments):
		#Store Submissions
		for comment in comments:
			if session.query(exists().where(Comments.id == comment.id)).scalar():
				print "Comment %s already exists!" % comment.id 
				continue

			new_comment = Comments(	sid=comment.submission.id, 
									stitle=comment.submission.title,
									id=comment.id,
									body=comment.body,
									score =int(comment.score),
									author=str(comment.author),
									replies=len(comment.replies),
									url =comment.permalink,
									gilded=comment.gilded,
									subreddit=subreddit,
									created_utc=comment.created_utc)
			session.add(new_comment)
			print "Storing Comment %s" % (comment.id)

		session.commit()

	@classmethod
	def checkComments(class_, session, subreddit):
		if session.query(exists().where(Comments.subreddit == subreddit)).scalar(): return True
		else: return False

	@classmethod
	def checkSubreddit(class_, session, subreddit):
		if session.query(exists().where(Comments.subreddit == subreddit)).scalar(): return True
		else: return False

	@classmethod
	def getComments(class_, session, subreddit):

		## Actual score calculations
		all_scores = session.query(Comments).with_entities(Comments.score)
		
		list_all_scores =  list(all_scores)
		avg =  numpy.average(list_all_scores)
		std = numpy.std(list_all_scores)
		floor = round(avg + std, 0)

		top = session.query(Comments).filter(and_(Comments.score > floor, Comments.subreddit==subreddit)).order_by(desc(Comments.score)).all()

		query = session.query(Comments.stitle.distinct().label("submission_title")).filter(Comments.score > floor)
		titles = [row.submission_title for row in query.all()]

		return top, avg, std, floor, titles
	
	@classmethod
	def removeComments(class_, session, subreddit):
		session.query(Comments).filter(Comments.subreddit==subreddit).delete()
		session.commit()

if __name__ == '__main__':
	engine = create_engine('sqlite:///submissions.db')
	Base.metadata.create_all(engine)



