import json
import soundcloud
from flask import Flask, Response, render_template, request, send_from_directory, redirect, url_for, jsonify, flash
from flask.json import JSONEncoder
from birdy.twitter import AppClient, TwitterAuthError
from werkzeug.contrib.cache import MemcachedCache
import time

class ApiResponse(Response):
    def __init__(self, payload=None, status_code=200, message='OK'):
        data = { 'status': status_code, 'message': message, 'payload': payload }
        encoded = json.dumps(data, cls=JSONEncoder, indent=4, separators=(',', ': '))
        Response.__init__(self, encoded, status=status_code, mimetype='application/json')


class TwitterClient(AppClient):
    @staticmethod
    def get_json_object_hook(data):
        return data


# Set up Flask app
app = Flask(__name__)
# Load configuration
app.config.from_pyfile('config.cfg')
# Set up cache
cache = MemcachedCache(['127.0.0.1:11211'])

@app.route("/")
def index():
    return render_template('index.html', test='HURRAH')


@app.route("/statuses")
def statuses():
    statuses = cache.get('statuses')

    if statuses is None:
        print 'Not Cached'
        consumer_key = app.config['TWITTER_CONSUMER_KEY']
        consumer_secret = app.config['TWITTER_CONSUMER_SECRET']

        # client = TwitterClient(consumer_key, consumer_secret)
        # access_token = client.get_access_token()

        # return jsonify({ 'key': access_token });

        access_token = app.config['TWITTER_ACCESS_TOKEN']

        try:
            client = TwitterClient(consumer_key, consumer_secret, access_token)
            response = client.api.statuses.user_timeline.get(screen_name='floodbanduk', 
                                                             count=3,
                                                             trim_user=True,
                                                             exclude_replies=True)
            statuses = response.data
            cache.set('statuses', statuses, timeout=1 * 60)
        except TwitterAuthError as e:
            return jsonify({ 'error': e._msg, 'error_code': e.error_code, 'status_code': e.status_code, 'headers': e.headers, 'resource_url': e.resource_url })

    # projection = [{ 'created_at': datetime.strftime('%Y-%m-%d %H:%M:%S', datetime.strptime(s['created_at'],'%a %b %d %H:%M:%S +0000 %Y')), 'text': s['text'] } for s in statuses]
    # projection = [{ 'created_at': datetime.strptime(s['created_at'],'%a %b %d %H:%M:%S +0000 %Y'), 'text': s['text'] } for s in statuses]
    # projection = [{ 'created_at': time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(s['created_at'],'%a %b %d %H:%M:%S +0000 %Y')), 'text': s['text'] } for s in statuses]

    projection = [{ 'created_at': s['created_at'], 'text': s['text'] } for s in statuses]

    return jsonify({ 'statuses': projection })



@app.route("/tracks")
def tracks():
    client = soundcloud.Client(client_id=app.config['SOUNDCLOUD_CLIENT_ID'],
                               client_secret=app.config['SOUNDCLOUD_CLIENT_SECRET'],
                               username=app.config['SOUNDCLOUD_USERNAME'],
                               password=app.config['SOUNDCLOUD_PASSWORD'])

    tracks = client.get('/me/tracks')

    return jsonify({ 'tracks': [{ 'id': t.id, 'title': t.title } for t in tracks] })


@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, request.path[1:])

if __name__ == "__main__":
    app.run(debug=True, threaded=True)