from flask import Flask, render_template
import engine
from operator import itemgetter
app = Flask(__name__)

@app.route('/')
def main():
	subreddit = 'fitness'
	ctop, cavg, cstd, cfloor = engine.TopComments(subreddit, 'both')
	stop, savg, sstd, sfloor = engine.TopSubmissions(subreddit, 'both')
	return render_template('main.html', comments=ctop, submissions=stop, subreddit = subreddit)


if __name__ == '__main__':
    app.run(debug=True)