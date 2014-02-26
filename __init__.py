from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html', test='HURRAH')

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

if __name__ == "__main__":
    app.run(debug=True, threaded=True)