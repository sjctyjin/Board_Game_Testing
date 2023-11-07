import flask
from flask import Flask, request, abort,jsonify,render_template,url_for,redirect,Response,session
from flask_cors import CORS
from flask_session import Session
import threading
import os
import numpy as np
from os.path import isfile, isdir, join
from pathlib import Path
import time
import random

app = flask.Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

CORS(app)
# app.secret_key = 'diskey'
app.config['SECRET_KEY'] = 'diskey'
app.config['SESSION_TYPE'] = 'filesystem'
app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False
Session(app)
usernum = []

# usernum_list = {}#記錄使用者及其選擇星球
usernum_list = {'WiWi': 'M6', 'Ken': 'M4', 'Omozon': 'M2', 'Edge_keven': 'M3'}
#記錄使用者及其選擇星球
start_game = 0 #當開始遊戲時，所有玩家一同進入大廳
Order_shuffled = {} #玩家洗牌後存放區
Order_control = 0#控制玩家順序
random_change = 0 #檢查是否已經過亂數排定
#初始任務牌-初階任務
Preliminary = [
    {'mission': "A1A1", "Payload": "BF1", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 6},
    {'mission': "A1A2", "Payload": "BF2", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 6},
    {'mission': "A1B1", "Payload": "BF3", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 12},
    {'mission': "A1B2", "Payload": "BF4", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 8},
    {'mission': "B1A1", "Payload": "BF5", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 8},
    {'mission': "B1A2", "Payload": "BF6", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 8},
    {'mission': "B1B1", "Payload": "BF1", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 6},
    {'mission': "B1B2", "Payload": "BF2", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 11},
    {'mission': "B1C1", "Payload": "BF3", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 12},
    {'mission': "B1C2", "Payload": "BF4", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 11},
    {'mission': "C1B1", "Payload": "BF5", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 10},
    {'mission': "C1B2", "Payload": "BF6", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 11},
    {'mission': "C1C1", "Payload": "BF1", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 7},
    {'mission': "C1C2", "Payload": "BF2", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 10},
    {'mission': "C1D1", "Payload": "BF3", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 6},
    {'mission': "C1D2", "Payload": "BF4", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 7},
    {'mission': "D1C1", "Payload": "BF5", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 6},
    {'mission': "D1C2", "Payload": "BF6", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 12},
    {'mission': "D1D1", "Payload": "BF1", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 11},
    {'mission': "D1D2", "Payload": "BF2", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 10},
    {'mission': "D1E1", "Payload": "BF3", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 11},
    {'mission': "D1E2", "Payload": "BF4", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 7},
    {'mission': "E1D1", "Payload": "BF5", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 8},
    {'mission': "E1D2", "Payload": "BF6", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 9},
    {'mission': "E1E1", "Payload": "BF1", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 12},
    {'mission': "E1E2", "Payload": "BF2", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 9},
    {'mission': "E1F1", "Payload": "BF3", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 12},
    {'mission': "E1F2", "Payload": "BF4", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 7},
    {'mission': "F1E1", "Payload": "BF5", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 6},
    {'mission': "F1E2", "Payload": "BF6", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 12},
    {'mission': "F1F1", "Payload": "BF1", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 9},
    {'mission': "F1F2", "Payload": "BF2", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 10},
    {'mission': "F1A1", "Payload": "BF3", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 9},
    {'mission': "F1A2", "Payload": "BF4", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 7},
    {'mission': "A1F1", "Payload": "BF5", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 9},
    {'mission': "A1F2", "Payload": "BF6", "Body": ["SUS_5", "AL_4", "ACM_3"], "Furl": 12},

]
@app.route('/', methods=['GET'])
def home():
    global start_game
    global usernum_list
    global Order_shuffled
    global random_change
    if start_game == 1:
        if random_change == 0:
            print(usernum_list)
            buffer_user = list(usernum_list.items())
            random.shuffle(buffer_user)
            # 將洗牌後的列表轉換回字典
            Order_shuffled = dict(buffer_user)
            random_change = 1


        return render_template(f'AEAS.html',Orderlen=len(list(Order_shuffled.values())),Order=list(Order_shuffled.values()))
    else:
        return redirect('/Join')

#當人數超過限制則阻止進入
@app.route('/Join', methods=['GET'])
def room():
    global usernum_list
    value = session.get('jim')


    print(value)
    if len(usernum_list) == 6:
        return redirect('/blcok_area')
    else:
        return render_template(f'Room.html')

@app.route('/blcok_area', methods=['GET'])
def blcok():
    global usernum_list
    print(usernum_list)
    return render_template(f'Block_A.html')

#加入使用者
@app.route('/user', methods=['POST'])
def user():
    global usernum
    global usernum_list

    data_res = request.get_json()
    # print(data_res)
    # if len(usernum_list) != 0:
    value = session.get('jim')
    print(value)
    print(data_res['user'])
    if len(usernum_list) == 0:
        usernum_list[data_res['user']] = ""
    if usernum_list[data_res['user']] == "":
        usernum_list[data_res['user']] = data_res['selected']
        return Response('done')
    else:
        usernum_list[data_res['user']] = ""
        return jsonify({'result':'done'})
    # return Response('you like shit')
#TODO 從querystring中確認 選擇腳色的是哪位玩家，進而紀錄該玩家的操作動作
#取得玩家人數
@app.route('/menber', methods=['GET'])
def menber():
    global usernum
    global usernum_list
    #
    print("使用者:", usernum)
    print(usernum_list)
    print(len(usernum_list))

    return jsonify({f"menber":usernum_list,"userlog":usernum,"states":start_game})
#清空人員
@app.route('/clear_user', methods=['POST'])
def clear_menber():
    global usernum
    global usernum_list
    global start_game

    usernum = []
    usernum_list = {}
    start_game = 2 #重置遊戲人數，所有人重新載入
    return jsonify({f"menber":usernum})
#重置遊戲後進入頁面，關閉重置狀態
@app.route('/closestate', methods=['GET'])
def closestate():
    global start_game
    start_game = 0 #關閉重置狀態
    return redirect('/Join')
#獲取使用者最初進入時間
@app.route('/usertime', methods=['POST'])
def usertime():
    global usernum_list
    global usernum


    data_res = request.get_json()
    print("接收到 : ",data_res)
    for i in usernum_list:
        if i == data_res['set_time']:
            return jsonify({'result': 'R'})
    usernum_list[data_res['set_time']] = ""
    usernum.append(data_res['set_time'])
    print("使用者:",usernum)

    return render_template(f'Room.html')
#開始訊號
@app.route('/start', methods=['POST'])
def start():
    global start_game
    global usernum_list

    start_game = 1
    items = list(usernum_list.items())
    # 對列表進行隨機排列
    random.shuffle(items)
    # 將洗牌後的列表轉換回字典
    shuffled_dict = dict(items)
    print(shuffled_dict)
    return Response('done')

#玩家回合訊號
@app.route('/round', methods=['POST'])
def round():
    global start_game
    global Order_shuffled
    global Order_control

    data_res = request.get_json()
    print(data_res["user_state"])
    if data_res["user_state"] == 1:
        Order_control += 1
        print(Order_control)
        if Order_control >= len(list(Order_shuffled.values())):
            Order_control = 0
    # print(Order_shuffled)
    # print(Order_shuffled.values())
    return jsonify({"userorder":list(Order_shuffled.values()),"order_now":Order_control})


if __name__ == "__main__":

    app.run(host='0.0.0.0',port=5000,debug=True)



