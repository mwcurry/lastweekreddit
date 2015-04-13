'''
SQL Alchemy database clases
'''

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Submissions(Base):
	__tablename__ = 'submission'
	id = Column(String(250), primary_key=True)
	title = Column(String(250))
	score = Column(Integer)
	author = Column(String(250))
	comments = Column(Integer)
	url = Column(String(250))
	gilded = Column(Integer)
	subreddit = Column(String(250))

class Comments(Base):
	__tablename__ = 'comments'
	id = Column(String(250), primary_key=True)
	body = Column(Text)
	score = Column(Integer)
	author = Column(String(250))
	replies = Column(Integer)
	url = Column(String(250))
	gilded = Column(Integer)
	#submission ID of the comment
	##Ask Abe if this should be a ForeignKey? 
	###sid = Column(String(250), ForeignKey('submission.id')) 
	sid = Column(String(250))
	subreddit = Column(String(250))


engine = create_engine('sqlite:///submissions.db')
Base.metadata.create_all(engine)