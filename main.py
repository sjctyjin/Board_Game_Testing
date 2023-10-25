import flask
from flask import Flask, request, abort,jsonify,render_template,url_for,redirect,Response,session
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
app.secret_key = 'diskey'
app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False

usernum = []
usernum_list = {}
@app.route('/', methods=['GET'])
def home():
    return render_template(f'AEAS.html')

@app.route('/Join', methods=['GET'])
def room():

    return render_template(f'Room.html')


@app.route('/user', methods=['POST'])
def user():
    global usernum
    data_res = request.get_json()
    print(data_res)
    if usernum != []:
        for i in usernum:
            if i == data_res['user']:
                usernum.remove(data_res['user'])
                return Response('you like shit')

    usernum.append(data_res['user'])
    return Response('you like shit')
#TODO 從querystring中確認 選擇腳色的是哪位玩家，進而紀錄該玩家的操作動作
#取得玩家人數
@app.route('/menber', methods=['GET'])
def menber():
    global usernum
    print(usernum)
    return jsonify({f"menber":usernum})
#清空人員
@app.route('/clear_user', methods=['POST'])
def clear_menber():
    global usernum
    usernum = []
    return jsonify({f"menber":usernum})
#獲取使用者最初進入時間
@app.route('/usertime', methods=['POST'])
def usertime():
    global usernum_list
    data_res = request.get_json()
    print(data_res)
    usernum_list[data_res['set_time']] = ""
    print(usernum_list)
    return render_template(f'Room.html')
if __name__ == "__main__":

    app.run(host='0.0.0.0',port=5000,debug=True)



