import flask
from flask import Flask, request, abort,jsonify,render_template,url_for,redirect
from flask_cors import CORS
import threading
import os
import numpy as np
from os.path import isfile, isdir, join
from pathlib import Path
import time

app = flask.Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

CORS(app)

app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False

@app.route('/', methods=['GET'])
def home():
    return render_template(f'AEAS.html')

if __name__ == "__main__":

    app.run(host='0.0.0.0',port=5000,debug=True)



