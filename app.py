from flask import Flask, render_template, request
from new import get_driver, get_source_from_page, get_data_from_source, next_btn_click, choosenumber, getchoices    #new.pyのdef scrayをimport
from show import devide,calculate_emotion_vector, search_most_similar
import pandas as pd
import requests
import numpy as np
from janome.tokenizer import Tokenizer
import re #正規表現を実装
import json #QiitaAPIから渡されるjsonを処理するため
from gensim.models import KeyedVectors
import scipy.spatial.distance
import ast

app = Flask(__name__)

# ドライバーのフルパス
CHROMEDRIVER = "C:\chromedriver.exe"
# 改ページ（最大）
PAGE_MAX = 4
# 遷移間隔（秒）
INTERVAL_TIME = 3


@app.route("/",methods=['GET',"POST"])  #index内でエリア指定
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        return render_template('index.html')



@app.route("/new",methods=['GET','POST'])
def new():       #このdef名は無関係よね？new.pyに入れる必要ないよね？
    if request.method == "GET":
        return render_template('new.html')
    elif request.method == "POST":
        csv=request.form.getlist("place") #これリストになってる["csv/ginza.csv"]っていう状況
        csv_show=csv[0]
        df = pd.read_csv(csv[0])
        df['genre'] = [ast.literal_eval(d) for d in df['genre']]
        choices=choosenumber(df) #リスト内に整数ランダムに3つ格納

       #↓これをnew.htmlに受け渡す
        choice1_number=int(choices[0])
        choice2_number=int(choices[1])
        choice3_number=int(choices[2])
        choice1=getchoices(int(choices[0]),df)
        choice2=getchoices(int(choices[1]),df)
        choice3=getchoices(int(choices[2]),df)
        #リスト内[2店舗名,3駅からなんm,4[ジャンル], 5評価,13URL]

        return render_template('new.html',csv_show=csv_show, choice1_number=choice1_number,choice2_number=choice2_number,choice3_number=choice3_number, choice1=choice1, choice2=choice2, choice3=choice3)
       # return render_template('new.html', choices=choices)



@app.route("/show",methods=['GET','POST'])
def show():
    if request.method == "GET":
        return render_template('show.html')
    elif request.method == "POST":
        #csv=request.form.getlist("place") #これリストになってる["csv/ginza.csv"]っていう状況だからcsv[0]でcsvを読み込める
        csv=request.form.getlist('hidden')
        csv_show=csv[0]
        df = pd.read_csv(csv[0])

        

        #好みの店を3つから1つ選ぶ
        select1 = request.form.getlist('choice')  #['0']  #何行目か。int(choices[0]),int(choices[1]),int(choices[2])がかえってくるはず
        choice_number=int(select1[0])
        
    
        #select.htmlから受け取って、recommend.py上で協調フィルタリング
        #recommendation = filtering(select1) 
        #return render_template('result.html', result=recommendation)  #result.htmlに結果を渡す


        df['img'] = [ast.literal_eval(d) for d in df['divided']]  #divided列の中身をリストに直してimg列にいれる
        df['genre'] = [ast.literal_eval(d) for d in df['genre']]
        key_list = df.iat[choice_number, 15]    #pr文をdibideしたdivided列→をリストに直したimg列
        emothion_vector = calculate_emotion_vector(key_list) 
        recommendation = search_most_similar(emothion_vector,df,choice_number)

        #return render_template('show.html', recommendation=recommendation)

        return render_template('show.html', select1=select1, choice_number=choice_number,key_list=key_list,recommendation=recommendation)


if __name__ == "__main__":
    app.run(debug=True)
