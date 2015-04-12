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

class Comments(Base):
	__tablename__ = 'comments'
	c_id = Column(String(250), primary_key=True)
	c_body = Column(Text)
	c_score = Column(Integer)
	c_author = Column(String(250))
	c_replies = Column(Integer)
	c_url = Column(String(250))
	c_gilded = Column(Integer)
	#submission ID of the comment
	##Ask Abe if this should be a ForeignKey? 
	###c_sid = Column(String(250), ForeignKey('submission.id')) 
	c_sid = Column(String(250))


engine = create_engine('sqlite:///submissions.db')
Base.metadata.create_all(engine)