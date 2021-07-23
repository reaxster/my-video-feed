from application import app
from flask import render_template, redirect, url_for, flash, request, Response
from authlib.integrations.flask_client import OAuth


###iMPORT FOR VIDEO#############
import cv2 as cv
from time import sleep
import numpy as np
import struct
import socket
import pickle

#############AUTH0################
from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from six.moves.urllib.parse import urlencode

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='NxpoAUxjjfUOijqaeNQ15dn1MY8owpTi',
    client_secret='OixgJzBw9yFghJGV6Khe1aWeQDxIen1U5nJEuMV1smws_yoLCnQ10hk1Szejhy_9',
    api_base_url='https://dev-wgyt7hl7.us.auth0.com',
    access_token_url='https://dev-wgyt7hl7.us.auth0.com/oauth/token',
    authorize_url='https://dev-wgyt7hl7.us.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

# Here we're using the /callback route.
@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
    }
    return redirect(url_for('videoScreen'))

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

############End of AUTH0#######################

##############VIDEO STREAMING - CREATED BY RICHAR MARSHALL##################

cap = cv.VideoCapture(0)
fourcc = cv.VideoWriter_fourcc(*'vp80')
#video=cv.VideoWriter('static/myvideo.webm',fourcc ,6,(320,240))
currentframe=0

def gen():
	#print(cap.read())

	while(cap.isOpened()):
		ret, img = cap.read()
		if ret == True:
			name = str(currentframe)+ '.png'
			img = cv.resize(img, (0,0), fx=0.5, fy=0.5)

			#print(img.shape)
			cv.imwrite(name, img)

			k=(cv.imread(str(currentframe)+'.png'))
			#video.write(k)
			frame = cv.imencode('.png', img)[1].tobytes()
			yield (b'--frame\r\n'b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')
			sleep(0)
		else: 
			break

###################

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/video")
@requires_auth
def videoScreen():
    cap.open(0)
    return render_template("videoScreen.html")

@app.route('/video_feed')
@requires_auth
def video_feed():
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='https://thawing-island-66760.herokuapp.com/callback')

#http://127.0.0.1:5000/callback
#https://thawing-island-66760.herokuapp.com/callback


@app.route("/logout")
def logout():
    cap.release()
    session.clear()
    params = {'returnTo': url_for('index', _external=True), 'client_id': 'r6U31gP9D21vR2fVOJINLRxLUzCzNlZ1'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

if __name__ == "__main__":
    	app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
