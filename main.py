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

usernum = {} #記錄使用者的手牌

usernum_list = {}#記錄使用者及其選擇星球
# usernum_list = {'WiWi': 'M6', 'Ken': 'M4', 'Omozon': 'M2',}
#記錄使用者及其選擇星球
start_game = 0 #當開始遊戲時，所有玩家一同進入大廳
Order_shuffled = {} #玩家洗牌後存放區
Order_control = 0#控制玩家順序
random_change = 0 #檢查玩家是否已經過亂數排定(玩家順序)
random_check = 0 #檢查玩家是否已經給定排序編號(給定順序編號)
Source_random_check = 0 #檢查是否已經給定資源及任務亂數排序
Table_Source = {} #當前牌面(資源牌)
Table_Pre = {} #當前牌面(初階任務)
Table_Inter = {} #當前牌面(中階任務)
updTable = 0 #檢查有幾位玩家，當有玩家完成動作時，該值=玩家數量-1;每位玩家在各自更新完桌面資料後，去減去這數量，當值為0時則代表同步成功

#資源牌
SourceAray = [
            'BF1', 'BF2', 'BF3', 'BF4', 'BF5', 'BF6',
            'BF1', 'BF2', 'BF3', 'BF4', 'BF5', 'BF6',
            'BF1', 'BF2', 'BF3', 'BF4', 'BF5', 'BF6',
			'Delta11', 'Delta11', 'Delta11', 'Delta11', 'Delta11', 'Delta11', 'Delta11',
            'Delta12', 'Delta12', 'Delta12', 'Delta12', 'Delta12', 'Delta11', 'Delta12',
            'Delta13', 'Delta13', 'Delta13', 'Delta13', 'Delta13', 'Delta13', 'Delta13',
            'Delta14', 'Delta14', 'Delta14', 'Delta14', 'Delta14', 'Delta14', 'Delta14',
            'Delta15', 'Delta15', 'Delta15', 'Delta15', 'Delta15',
            'Delta16', 'Delta16', 'Delta16', 'Delta16', 'Delta16',
            'Delta17', 'Delta17', 'Delta17',
            'Delta18', 'Delta18', 'Delta18',
            'Delta19', 'Delta19',
            'Delta20', 'Delta20',
			'SUS_5', 'SUS_5', 'SUS_5', 'SUS_5', 'SUS_5', 'SUS_5', 'SUS_5', 'SUS_5', 'SUS_5', 'SUS_5', 'SUS_5',
			'AL_4', 'AL_4', 'AL_4', 'AL_4', 'AL_4', 'AL_4', 'AL_4', 'AL_4', 'AL_4',
			'ACM_3', 'ACM_3', 'ACM_3', 'ACM_3', 'ACM_3', 'ACM_3', 'ACM_3',
			'CMC_2', 'CMC_2', 'CMC_2', 'CMC_2', 'CMC_2',
			'Ti_1', 'Ti_1', 'Ti_1',
            'AF1', 'AF2', 'AF3', 'AF4', 'AF5', 'AF6',
            'AF1', 'AF2', 'AF3', 'AF4', 'AF5', 'AF6',
            'AF1', 'AF2', 'AF3', 'AF4', 'AF5', 'AF6',
        ];
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

Intermed = [
			{ 'tech': ["A1A1", "A1A2"], 'mission': "A1A", "Payload": "AF1", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 15 },
			{ 'tech': ["A1B1", "A1B2"], 'mission': "A1B", "Payload": "AF2", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 12 },
			{ 'tech': ["B1A1", "B1A2"], 'mission': "B1A", "Payload": "AF3", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 14 },
			{ 'tech': ["B1B1", "B1B2"], 'mission': "B1B", "Payload": "AF4", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 12 },
			{ 'tech': ["B1C1", "B1C2"], 'mission': "B1C", "Payload": "AF5", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 11 },
			{ 'tech': ["C1B1", "C1B2"], 'mission': "C1B", "Payload": "AF6", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 14 },
			{ 'tech': ["C1C1", "C1C2"], 'mission': "C1C", "Payload": "AF1", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 12 },
			{ 'tech': ["C1D1", "C1D2"], 'mission': "C1D", "Payload": "AF2", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 14 },
			{ 'tech': ["D1C1", "D1C2"], 'mission': "D1C", "Payload": "AF3", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 9 },
			{ 'tech': ["D1D1", "D1D2"], 'mission': "D1D", "Payload": "AF4", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 13 },
			{ 'tech': ["D1E1", "D1E2"], 'mission': "D1E", "Payload": "AF5", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 13 },
			{ 'tech': ["E1D1", "E1D2"], 'mission': "E1D", "Payload": "AF6", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 14 },
			{ 'tech': ["E1E1", "E1E2"], 'mission': "E1E", "Payload": "AF1", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 15 },
			{ 'tech': ["E1F1", "E1F2"], 'mission': "E1F", "Payload": "AF2", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 16 },
			{ 'tech': ["F1E1", "F1E2"], 'mission': "F1E", "Payload": "AF3", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 12 },
			{ 'tech': ["F1F1", "F1F2"], 'mission': "F1F", "Payload": "AF4", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 16 },
			{ 'tech': ["F1A1", "F1A2"], 'mission': "F1A", "Payload": "AF5", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 16 },
			{ 'tech': ["A1F1", "A1F2"], 'mission': "A1F", "Payload": "AF6", "Body": ["AL_4", "ACM_3", "CMC_2"], "Furl": 11 },

        ]
@app.route('/', methods=['GET'])
def home():
    global start_game
    global usernum_list
    global Order_shuffled
    global random_change
    global usernum

    if start_game == 1:
        # if random_change == 0:
        #     print(usernum_list)
        #     buffer_user = list(usernum_list.items())
        #     random.shuffle(buffer_user)
        #     # 將洗牌後的列表轉換回字典
        #     Order_shuffled = dict(buffer_user)
        #     random_change = 1#將此段移至start處


        return render_template(f'AEAS.html',Orderlen=len(list(Order_shuffled.values())),Order=list(Order_shuffled.values()))
    else:
        shuff = 0
        if usernum == {}:#若為空 代表無玩家登入
            shuff = 1 #檢查是否有玩家，若無玩家則前端直接刷新session
        return render_template(f'Room.html',shuff=shuff)


#當人數超過限制則阻止進入
@app.route('/Join', methods=['GET'])
def room():
    global usernum_list
    # value = session.get('jim')
    #
    #
    # print(value)
    if len(usernum_list) == 4:
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
    print("User選角")
    print(data_res['user'])

    if len(usernum_list) == 0:
        usernum_list[data_res['user']] = ""
        return jsonify({'result':'done'})
    if usernum_list[data_res['user']] == "":
        usernum_list[data_res['user']] = data_res['selected']
        return jsonify({'result':'done'})
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
    global Order_shuffled
    global start_game
    global random_check

    print("使用者:", usernum)
    print(usernum_list)
    print(Order_shuffled)
    print(len(usernum_list))
    # if start_game == 1:
    #     if random_check == 0:
    #         print("5"*1000)
    #         count = 0
    #         for va in Order_shuffled:
    #             Order_shuffled[va] = [Order_shuffled[va],count]
    #             count+=1
    #             print(va)
    #         random_check = 1
    #         print("亂數完成 : ",Order_shuffled)
    #         return jsonify(
    #             {f"menber": usernum_list, "userlog": usernum, "states": start_game, "ordershu": Order_shuffled})

    return jsonify({f"menber":usernum_list,"userlog":usernum,"states":start_game,"ordershu":Order_shuffled})
#清空人員
@app.route('/clear_user', methods=['POST'])
def clear_menber():
    global usernum
    global usernum_list
    global start_game

    usernum = {}
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
    usernum[data_res['set_time']] = {'Hand':'','Tech':'','Build':''}
    print("使用者:",usernum)

    return render_template(f'Room.html')
#開始訊號
@app.route('/start', methods=['POST'])
def start():
    global start_game
    global usernum_list
    global random_check
    global Order_shuffled
    global random_change

    start_game = 1
    items = list(usernum_list.items())
    # 對列表進行隨機排列
    random.shuffle(items)
    # 將洗牌後的列表轉換回字典
    shuffled_dict = dict(items)
    print(shuffled_dict)
    if random_change == 0:
        buffer_user = list(usernum_list.items())
        random.shuffle(buffer_user)
        # 將洗牌後的列表轉換回字典
        Order_shuffled = dict(buffer_user)
        random_change = 1
    if random_check == 0:
        print("5" * 1000)
        count = 0
        print(Order_shuffled)
        for va in Order_shuffled:
            Order_shuffled[va] = [Order_shuffled[va], count]
            count += 1
            print(va)
        random_check = 1
        print("亂數完成 : ", Order_shuffled)

        # return jsonify(
        #     {f"menber": usernum_list, "userlog": usernum, "states": start_game, "ordershu": Order_shuffled})
    return Response('done')

#玩家回合訊號
@app.route('/round', methods=['POST'])
def round():
    global start_game
    global Order_shuffled
    global Order_control#當前玩家順序
    global SourceAray   #資源牌
    global Preliminary  #初階任務
    global Intermed     #中階任務
    global Table_Source  # 桌面資源牌
    global Table_Pre     # 桌面初階任務
    global Table_Inter   # 桌面中階任務
    global updTable   # 玩家桌面更新狀態


    data_res = request.get_json()
    # print(data_res["user_state"])#確認玩家是否已完成該回合動作
    if data_res["user_state"] == 1 and int(data_res["user_id"]) == Order_control:
        Order_control += 1
        print("當前順序",Order_control)
        if Order_control >= len(list(Order_shuffled.values())):
            Order_control = 0
    # print(Order_shuffled)
    # print(list(Order_shuffled.values())[0])
    return jsonify({"userorder":list(Order_shuffled.values()),"order_now":Order_control,'resource':SourceAray,'Pre':Preliminary,'Inter':Intermed,'Table_Source': Table_Source, 'Table_Pre': Table_Pre, 'Table_Inter': Table_Inter,'updTable':updTable})

#資源牌庫
@app.route('/resource', methods=['POST','GET'])
def resource():
    global SourceAray   #資源牌
    global Preliminary  #初階任務
    global Intermed     #中階任務
    global Source_random_check     #確認
    global Table_Source  # 桌面資源牌
    global Table_Pre     # 桌面初階任務
    global Table_Inter   # 桌面中階任務
    global usernum   # 玩家手牌
    global updTable   # 玩家桌面更新狀態
    if request.method == 'GET':
        if Source_random_check == 0:#若牌堆還未洗牌
            print(SourceAray)
            random.shuffle(SourceAray)
            random.shuffle(Preliminary)
            random.shuffle(Intermed)
            Source_random_check = 1
            return jsonify({'resource':SourceAray,'Pre':Preliminary,'Inter':Intermed})
        if updTable != 0:
            updTable -= 1
        return jsonify({'resource':SourceAray,'Pre':Preliminary,'Inter':Intermed,'Table_Source': Table_Source, 'Table_Pre': Table_Pre, 'Table_Inter': Table_Inter,'User_Hand':usernum})

    else:
        data_res = request.get_json()
        print("資源牌 : ",data_res["SourceAray"])
        print("初階任務 : ",data_res["Preliminary"])
        print("中階任務 : ",data_res["Intermed"])
        print("使用者 : ",data_res["user"])
        print("手牌 : ",data_res["userHands"])
        print("技術 : ",data_res["userTech"])
        print("建設 : ",data_res["userBuild"])
        print("資源牌(桌面) : ", data_res["SourceAray"])
        print("初階任務(桌面)  : ", data_res["Preliminary"])
        print("中階任務(桌面)  : ", data_res["Intermed"])
        print(usernum[data_res["user"]])
        #玩家手牌更新
        usernum[data_res["user"]]['Hand'] = data_res["userHands"]
        usernum[data_res["user"]]['Tech'] = data_res["userTech"]
        usernum[data_res["user"]]['Build'] = data_res["userBuild"]
        #資源、任務牌更新
        SourceAray = data_res["SourceAray"]
        Preliminary = data_res["Preliminary"]
        Intermed = data_res["Intermed"]
        #桌面牌更新
        Table_Source = data_res["Table_Source"]
        Table_Pre = data_res["Table_Pre"]
        Table_Inter = data_res["Table_Inter"]

        print(usernum[data_res["user"]]['Hand'])
        print(usernum[data_res["user"]]['Tech'])
        print(usernum[data_res["user"]]['Build'])

        if data_res["upd"] == 1:
            if updTable == 0:
                updTable = len(usernum_list)-1
        # usernum[data_res['set_time']] = {'Hand': '', 'Tech': '', 'Build': ''}

        return jsonify({'result':"pass",'resource':SourceAray,'Pre':Preliminary,'Inter':Intermed})
#所有資訊
@app.route('/all_info', methods=['GET'])
def info_ALL():
    global usernum #記錄使用者的手牌
    global usernum_list#記錄使用者及其選擇星球
    global start_game #當開始遊戲時，所有玩家一同進入大廳
    global Order_shuffled #玩家洗牌後存放區
    global Order_control #控制玩家順序
    global random_change #檢查是否已經過亂數排定
    global random_check  #檢查玩家是否已經給定排序編號
    global Source_random_check #檢查是否已經給定資源及任務亂數排序
    global SourceAray  # 資源牌
    global Preliminary  # 初階任務
    global Intermed  # 中階任務
    global Table_Source  # 桌面資源牌
    global Table_Pre     # 桌面初階任務
    global Table_Inter   # 桌面中階任務
    global updTable   # 確認玩家是否同步更希桌面牌

    return jsonify({'usernum(使用者的手牌)': usernum,
                    'usernum_list(用者及其選擇星球)':usernum_list,
                    'start_game':start_game,
                    'Order_shuffled(玩家洗牌後存放區)':Order_shuffled,
                    'Order_control(控制玩家順序)':Order_control,
                    'random_change(檢查玩家是否已經過亂數排定)':random_change,
                    'random_check(檢查玩家是否已經給定排序編號)':random_check,
                    'Source_random_check(檢查是否已經給定資源及任務亂數排序)':Source_random_check,
                    'SourceAray_資源牌':SourceAray,
                    'Preliminary_初階任務':Preliminary,
                    'Intermed_中階任務':Intermed,
                    'Table_Source_資源牌(桌面)': Table_Source,
                    'Table_Pre_初階任務(桌面)': Table_Pre,
                    'Table_Inter_中階任務(桌面)': Table_Inter,
                    'AupdTable_(桌面同步更新-常駐為0)': updTable,
                    })
if __name__ == "__main__":

    app.run(host='0.0.0.0',port=5000,debug=True)



