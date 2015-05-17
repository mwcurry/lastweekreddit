from flask import Flask, render_template, redirect, request, flash, get_flashed_messages, jsonify, url_for

from sqlalchemy import create_engine, exists, or_, and_, func, desc
from sqlalchemy.orm import sessionmaker

import engine as APIconnect
from celeryconfig import celapp
from celery.result import AsyncResult
import filters
import model
from model import Base




app = Flask(__name__)
app.jinja_env.filters['date'] = filters.format_datetime
app.jinja_env.filters['day'] = filters.format_day
app.jinja_env.filters['redditlink'] = filters.reddit_links
app.jinja_env.filters['nl2br'] = filters.nl2br
app.jinja_env.filters['str'] = filters.str
app.secret_key = 'some_secret'


@app.route('/')
def main():
	#create sessions
	engine = create_engine('sqlite:///submissions.db')
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	#menu items
	menuitems = model.Subreddits.getSubredditsUnique(session)
	
	subreddits = model.Subreddits.getSubreddits(session)
	
	#view
	return render_template('home.html', headername = 'subreddits', subreddits = subreddits, menuitems = menuitems)

@app.route('/refresh/')
def refresh():
	return render_template('refresh.html')

@app.route('/refreshAPI', methods=['POST'])
def refreshAPI():
		task = APIconnect.updateAllSubreddits.delay()
		#return task.id
		return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = APIconnect.updateAllSubreddits.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@app.route('/r/<subreddit>/')
def sub(subreddit):
	#create sessions
	engine = create_engine('sqlite:///submissions.db')
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	
	
	#check if we have subreddit in database
	if not (model.Subreddits.checkSubreddit(session, subreddit)):
		return redirect("r/" + subreddit + "/add", code=302)
	
	#menu items
	subreddits = model.Subreddits.getSubredditsUnique(session)
	sub = model.Subreddits.getSubreddit(session, subreddit)

	
	#check if subreddit has content, if not let user know there is no content
	if not (model.Submissions.checkSubreddit(session, subreddit) and model.Comments.checkSubreddit(session, subreddit)):
		flash('Retrieving content from Reddit', 'alert-warning')
		return render_template('content.html', headername = sub.title, subreddit=sub, menuitems = subreddits, progress = True)

	#get info from model

	stop, savg, sstd, sfloor = model.Submissions.getSubmissions(session,subreddit)
	ctop, cavg, cstd, cfloor = model.Comments.getComments(session,subreddit)

	titles = {} # submission title: [submission id, # of comments]

	for c in ctop:
		if c.stitle in titles:
			titles[c.stitle][1] += 1
			continue
		titles[c.stitle] = [c.sid, 1]
	
	#view
	return render_template('content.html', comments=ctop, submissions=stop, headername = sub.title, subreddit = sub, titles = titles, menuitems = subreddits)

@app.route('/r/<subreddit>/add', methods=['GET', 'POST'])
@app.route('/add', methods=['GET', 'POST'])
def add_sub(subreddit=None):
	engine = create_engine('sqlite:///submissions.db')
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	#check if we have subreddit in database and foward to subreddit page
	if  (model.Subreddits.checkSubreddit(session, subreddit)):
		return redirect('r/' + subreddit, code=302)

	#menu items
	subreddits = model.Subreddits.getSubredditsUnique(session)

	if request.method == 'POST':
		subreddit = str(request.form['to_add'])
		if (model.Subreddits.checkSubreddit(session, subreddit)):
			flash('Subreddit already tracked.', 'alert-warning')
			return redirect(subreddit)
		else:
			model.Subreddits.quickAddSubreddit(session, subreddit)
			APIconnect.queryContent.delay(None, subreddit)
			return redirect(subreddit)
	else:
		return render_template('error.html', subreddit=subreddit, menuitems = subreddits, headername = 'subreddits')


if __name__ == '__main__':
    app.run(debug=True)