'''
Script to summarize the top submissions & comments for a subreddit in the past week

'''

import praw
import json
import pprint
from operator import itemgetter


def getSubmissions(subreddit):
	#todo: expand to multi subs
	#>>> submissions = r.get_subreddit('python').get_top(limit=10)
	sub = r.get_subreddit(subreddit)

	top_comments = []
	top_submissions = []

	#Get Top Submissions & Comments
	for submission in sub.get_top_from_week(limit=2):
		top_submissions.append([submission.id, submission.title, submission.score, submission.author, len(submission.comments), submission.url, submission.gilded])

		# Get Top Comments
		##submission.replace_more_comments(limit=None, threshold =0) #http://praw.readthedocs.org/en/latest/pages/code_overview.html#praw.objects.Submission.replace_more_comments
		
		for comment in submission.comments:
			if not hasattr(comment, 'body'): continue
			top_comments.append([submission.id, comment.id, comment.body, int(comment.score), comment.author, len(comment.replies), comment.permalink, comment.gilded])
			print comment.body, comment.gilded

	return top_submissions, top_comments


def getGilded(subreddit):
	sub = r.get_comments(subreddit, gilded_only = True, limit=15)
	gilded_comments = []
	gilded_submissions = []

	for item in sub:
		#check if gilded item is comment
		if hasattr(item,'_submission'):
			gilded_comments.append([item.link_id, item.id, item.body, int(item.score), item.author, len(item.replies), item.permalink, item.gilded])

		#check if gilded item is submission
		if hasattr(item,'_comments'):
			gilded_submissions.append([item.id, item.title, item.score, item.author, len(item.comments), item.url, item.gilded])

	s_c = sorted(gilded_comments, key=itemgetter(7, 3), reverse=True)
	pprint.pprint(s_c)

	#return gilded_comments, gilded_submissions


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
	getGilded('fitness')