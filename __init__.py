import re
import json
import soundcloud
from flask import Flask, Response, render_template, request, send_from_directory, redirect, url_for, jsonify, flash
from flask.json import JSONEncoder
from birdy.twitter import AppClient, TwitterAuthError
from werkzeug.contrib.cache import MemcachedCache
import time
from createsend import *
from flask.ext.assets import Environment, Bundle
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


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
# Set up asset bundling
assets = Environment(app)
js = Bundle('js/tinynav.js', 'js/moment.js', 'js/main.js', filters='jsmin', output='js/all.js')
css = Bundle('css/reset.css', 'css/pocketgrid.css', 'css/main.css', filters='cssmin', output='css/all.css')
assets.register('js_all', js)
assets.register('css_all', css)
# Set up cache
cache = MemcachedCache(['127.0.0.1:11211'])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/music')
def music():
    return render_template('music.html')


@app.route('/links')
def links():
    return render_template('links.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/gigs')
def gigs():
    return render_template('gigs.html')


@app.route('/statuses')
def statuses():
    statuses = cache.get('statuses')

    if statuses is None:
        consumer_key = app.config['TWITTER_CONSUMER_KEY']
        consumer_secret = app.config['TWITTER_CONSUMER_SECRET']

        # Uncomment if we need to get a new access token
        # client = TwitterClient(consumer_key, consumer_secret)
        # access_token = client.get_access_token()
        # return jsonify({ 'key': access_token });

        access_token = app.config['TWITTER_ACCESS_TOKEN']

        try:
            client = TwitterClient(consumer_key, consumer_secret, access_token)
            response = client.api.statuses.user_timeline.get(screen_name='floodbanduk', 
                                                             count=10,
                                                             trim_user=True,
                                                             exclude_replies=True)
            statuses = response.data
            cache.set('statuses', statuses, timeout=1 * 60)
        except TwitterAuthError as e:
            return jsonify({ 'error': e._msg, 'error_code': e.error_code, 'status_code': e.status_code, 'headers': e.headers, 'resource_url': e.resource_url })

    for s in statuses:
        s['text'] = re.sub(r"(@([^\s\:\,\.]+))", r'<a href="https://twitter.com/\2">\1</a>', s['text'], 0, re.IGNORECASE | re.MULTILINE)
        for u in s['entities']['urls']:
            s['text'] = re.sub(u['url'], r'<a href="' + u['expanded_url'] + '">' + u['display_url'] + '</a>', s['text'], 0, re.IGNORECASE | re.MULTILINE)
        if 'media' in s['entities']:
            for u in s['entities']['media']:
                s['text'] = re.sub(u['url'], '', s['text'], 0, re.IGNORECASE | re.MULTILINE)

    projection = [{ 'created_at': s['created_at'], 'text': s['text'].strip() } for s in statuses]

    return jsonify({ 'statuses': projection[:4] })


@app.route('/tracks')
def tracks():
    client = soundcloud.Client(client_id=app.config['SOUNDCLOUD_CLIENT_ID'],
                               client_secret=app.config['SOUNDCLOUD_CLIENT_SECRET'],
                               username=app.config['SOUNDCLOUD_USERNAME'],
                               password=app.config['SOUNDCLOUD_PASSWORD'])

    tracks = client.get('/me/tracks')

    return jsonify({ 'tracks': [{ 'id': t.id, 'title': t.title } for t in tracks] })


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    subscriber = Subscriber({'api_key': app.config['CM_CLIENT_API_KEY']})
    result = subscriber.add(app.config['CM_LIST_ID'], email, '', [], True)
    return jsonify({ 'success': True })


@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(os.environ['HTTP_PLATFORM_PORT'])
    loop = IOLoop.instance()
    loop.start()
