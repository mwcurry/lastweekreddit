from flask import Flask, render_template
import engine
from operator import itemgetter
app = Flask(__name__)

@app.route('/')
def main():
	ctop, cavg, cstd, cfloor = engine.TopComments('fitness', 'both')
	stop, savg, sstd, sfloor = engine.TopSubmissions('fitness', 'both')
	return render_template('main.html', comments=ctop, submissions=stop)


if __name__ == '__main__':
    app.run(debug=True)