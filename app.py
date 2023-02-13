import flask
from flask import Flask, request, abort,jsonify,render_template,url_for,redirect
from flask_cors import CORS
import threading
import os
import cv2
import numpy as np
from os.path import isfile, isdir, join
from pathlib import Path
import time

app = flask.Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

CORS(app)

app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False

mouse_tab = {"X":0,"Y":0}

print(os.getcwd())

print(os.getcwd())
# files = os.listdir("static/iPad (2)")
# for filename in files:
#     print(filename)

#製作影片縮圖
def process_image(dirs,o):
    keyshot = 120
    savepath = "static/allvid"
    raw = cv2.VideoCapture(f"{dirs}/{o}")
    # frames_num = int(raw.get(7)/2)
    fCount = 0
    min_side = 608
    while 1:
        # 影片轉圖片
        ret, img = raw.read()
        fCount += 1
        if (ret == True):
            if fCount == keyshot:
                size = img.shape
                h, w = size[0], size[1]
                scale = max(w, h) / float(min_side)
                new_w, new_h = int(w / scale), int(h / scale)
                resize_img = cv2.resize(img, (new_w, new_h), cv2.INTER_AREA)  # 變更尺寸
                if new_w % 2 != 0 and new_h % 2 == 0:
                    top, bottom, left, right = (min_side - new_h) // 2, (min_side - new_h) // 2, (
                                min_side - new_w) // 2 + 1, (min_side - new_w) // 2
                elif new_h % 2 != 0 and new_w % 2 == 0:
                    top, bottom, left, right = (min_side - new_h) // 2 + 1, (min_side - new_h) // 2, (
                                min_side - new_w) // 2, (min_side - new_w) // 2
                elif new_h % 2 == 0 and new_w % 2 == 0:
                    top, bottom, left, right = (min_side - new_h) // 2, (min_side - new_h) // 2, (
                                min_side - new_w) // 2, (min_side - new_w) // 2
                else:
                    top, bottom, left, right = (min_side - new_h) // 2 + 1, (min_side - new_h) // 2, (
                                min_side - new_w) // 2 + 1, (min_side - new_w) // 2
                img_pad = cv2.copyMakeBorder(resize_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
                print(dirs.split('/')[-1])
                cv2.imencode('.jpg', img_pad)[1].tofile(
                    '{0}/{2}{1}.mp4.jpg'.format(savepath, os.path.splitext(f"{o}")[0], dirs.split('/')[-1]))
                # cv2.imencode('.jpg', img_pad)[1].tofile(f'{savepath}/{os.path.splitext(f"{o}")[0]}.mp4.jpg')
                break
        else:
            break

@app.route('/', methods=['GET'])
def home():
    # 指定要列出所有檔案的目錄
    mypath = "static/"

    # 取得所有檔案與子目錄名稱
    files = os.listdir(mypath)
    abl = []
    fTree = os.walk(mypath, topdown=True)
    for dirs, subdirs, files in fTree:
        if subdirs != []:
            if dirs == mypath:
                # print(dirs.replace('\\','/'))
                abl = subdirs

    # # 以迴圈處理
    # for f in files:
    #     # 產生檔案的絕對路徑
    #     fullpath = join(mypath, f)
    #     # 判斷 fullpath 是檔案還是目錄
    #     if isfile(fullpath):
    #         print("檔案：", f)
    #     elif isdir(fullpath):
    #         abl.append(f)
    #         print("目錄：", f)
    return render_template(f'index.html',dir=abl)
#
@app.route('/scr', methods=['GET','POST'])
def scr():
    id = request.args.get('id')
    print(id)
    files = os.listdir("static/iPad (2)")
    fname = files[int(id)]
    img = cv2.imread(f"static/iPad (2)/{fname}")
    h,w = img.shape[:2]
    rate = w/h
    if w>h:
        width = 800
        height = int(width/rate)
    else:
        height= 800
        width = int(height * rate)

    print(img.shape)
    return render_template(f'single.html',fname=fname,H=height,W=width,imgs = 0)

@app.route('/long', methods=['GET','POST'])
def long():
    id = request.args.get('id')
    print(id)
    files = os.listdir("static/iPad")
    # fname = files[int(id)]
    imgs = []
    i = range(1, 10)
    j = range(1, 10)

    for o in range(1000):
        imgs.append(f"""static/iPad (2)/{files[o]}""")
    return render_template(f'single.html',vari=10,imgs = imgs,var_i=i,var_j=j)

@app.route('/show', methods=['GET','POST'])
def show():
    isum = 0
    jsum = 0
    num = 0
    dir = "iPad"
    if request.args.get('dir') != None:
        dir = request.args.get('dir')
    if request.args.get('i') != None:
        isum = int(request.args.get('i'))
    if request.args.get('j') != None:
        jsum = int(request.args.get('j'))
    if request.args.get('n') != None:
        num = int(request.args.get('n'))

    k = 100

    if jsum!=0 and isum!=0:
        k = isum*jsum

    # int(request.args.get('i'))
    # print(id)
    files = os.listdir(f"static/{dir}")
    # fname = files[int(id)]
    imgs = []
    imglen = []
    if num != 0:
        if(isum != 0):
            i = range(0, isum)#總數量
        if (isum != 0):
            j = range(0, jsum)  # 單排數量
        else:
            i = range(num, 10)  # 總數量
            j = range(0, 10)  # 單排數量
    else:
        if (isum != 0):
            i = range(0, isum)  # 總數量
        if (isum != 0):
            j = range(0, jsum)  # 單排數量
        else:
            i = range(0, 10)  # 總數量
            j = range(0, 10)  # 單排數量

    files.sort(key=lambda x: len(x.split('.')) > 1)
    for o in range(len(files)):
        imgs.append(f"""static/{dir}/{files[o]}""")


        if os.path.isdir(f"""static/{dir}/{files[o]}"""):
            imglen.append("1")
        else:
            if os.path.splitext(f"""static/{dir}/{files[o]}""")[1] == ".mp4":
                imglen.append("2")
            else:
                imglen.append("0")

    return render_template(f'show.html',varj=jsum,imgs = imgs,lens=imglen,var_i=i,var_j=j,num=num)

@app.route('/php_demo', methods=['GET'])
def menu():
    mypath = "static/"

    # 取得所有檔案與子目錄名稱
    files = os.listdir(mypath)
    abl = []
    # 以迴圈處理
    for f in files:
        # 產生檔案的絕對路徑
        fullpath = join(mypath, f)
        # 判斷 fullpath 是檔案還是目錄
        if isfile(fullpath):
            print("檔案：", f)
        elif isdir(fullpath):
            abl.append(f)
            print("目錄：", f)
    return render_template(f'menu.html',dir=abl)

@app.route('/allfile', methods=['GET'])
def allfile():
    mypath = "static/"

    # 取得所有檔案與子目錄名稱
    files = os.listdir(mypath)
    abl = []
    # 以迴圈處理
    for f in files:
        # 產生檔案的絕對路徑
        fullpath = join(mypath, f)
        # 判斷 fullpath 是檔案還是目錄
        if isfile(fullpath):
            print("檔案：", f)
        elif isdir(fullpath):
            abl.append(f)
            print("目錄：", f)
    return render_template(f'menu.html',dir=abl)

#Google搜尋並下載圖片
@app.route('/search', methods=['GET','POST'])
def search():
    # Instagram搜尋並下載圖片
    para = request.args.get('co')
    if request.method == 'POST':
        # key = request.args.get('key')
        key = request.values['keyword']
        # num = request.args.get('num')
        num = request.values['num']
        if para == None:
            if num == None  or num != '' :
                num = 200
            # print(os.system(f"""python google_images_download.py -k "{key}" -l {num} --chromedriver="C:/chromedriver" """))
            if key != None or key != '' :
                print(os.system(f"""python google_images_download.py -k "{key}" -l {num} --chromedriver="C:/chromedriver" """))

            return redirect(url_for('home'))
        else:
            print(os.system(
                f"""python instaloader/instaloader.py {key} --no-compress-json --no-metadata-json --no-captions --igtv --dirname-pattern "static/IG/{key}" """))


            return redirect(url_for('home'))
    else:
        return render_template(f'download.html')


#上傳圖片
@app.route('/upload', methods=['GET','POST'])
def upload_file():
    root_path = f"static/uploads/"
    if request.method == 'POST':

        file_up = request.files.getlist("file[]")#['filename']
        # print( request.values['folder'])
        select_save = request.values['folder']

        #遍歷資料夾內的檔案
        dtree = os.walk(root_path, topdown=True)
        dirs = []#資料夾
        for path, dir, files in dtree:
            if dir != []:
                dirs = dir
        print(dirs)
        dirs.append("新增資料夾")

        if select_save != None:#html oprion選擇的index
            if select_save == str(len(dirs)-1):
                save_dir = f"{root_path}/{request.values['foldername']}"
                if not Path(save_dir).exists():
                    #創建資料夾
                    Path(save_dir).mkdir(parents=True, exist_ok=True)
                    save_path = os.path.join(root_path,request.values['foldername']).replace("\\","/")

                    print("新增")
            else:
                save_path = os.path.join(root_path, dirs[int(select_save)]).replace("\\","/")

        # print(file_up)
        #影片、照片存檔
        if file_up != []:
            for i in file_up:
                formats = i.filename[i.filename.index('.'):]
                fileName = str(time.time()).replace('.','')
                if formats in ('.jpg', '.png', '.jpeg', '.HEIC', '.jfif'):
                    formats = '.jpg'
                    i.save(os.path.join(save_path, f"{fileName}{formats}"))
                else:
                    formats = '.mp4'
                    i.save(os.path.join(save_path, f"{fileName}{formats}"))
                    process_image(save_path,f"{fileName}{formats}")

                # print(i)
            return redirect(url_for('home'))
        else:

            return render_template('upload.html',dirs=dirs)
    else:
        dtree = os.walk(root_path, topdown=True)
        dirs = []
        for path, dir, files in dtree:
            if dir != []:
                dirs = dir
        print(dirs)
        dirs.append("新增資料夾")
        return render_template('upload.html', dirs=dirs)

if __name__ == "__main__":

    app.run(host='0.0.0.0',port=5000,debug=True)



