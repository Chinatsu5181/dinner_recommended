import pandas as pd
import numpy as np
from gensim.models import KeyedVectors
import scipy.spatial.distance
from janome.tokenizer import Tokenizer
import re #正規表現を実装
import json #QiitaAPIから渡されるjsonを処理するため
from gensim.models import KeyedVectors
import scipy.spatial.distance

#model = KeyedVectors.load_word2vec_format('model.vec', binary=False)
#model.save("model.kv")
model = KeyedVectors.load('model.kv', mmap='r')




def devide(df): #この関数つかわれてない
        symbol = re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]')#正規表現
        table = {'\n': '','\r': '','\t':''}
        for i in range(len(df)):
            text = str(df.iloc[i,11]) #dfの"total"列(13列目)がいいけど、list型になっててできないから仮でpr列つかう
            text = text.translate(str.maketrans(table)) #記号を除去
            text = symbol.sub('', text)
            
            l = []
            t = Tokenizer()
            for token in t.tokenize(text):
                pos = token.part_of_speech.split(',') 
                if '形容詞' in pos or '名詞' in pos: #名詞と形容詞だけを抽出
                    l.append(token.surface) #.surfaceで単語だけを表示（他の情報は取り込まない）
            df.iloc[i,14] = l
        return df


#ベクトルの計算
def calculate_language_vector(words):
    features = 300
    feature_vec = np.zeros((features),dtype = "float32")
    for word in words:
        try:
            feature_vec = np.add(feature_vec, model[word])
        #例外処理.辞書にない文字が出たときは処理をスキップする
        except KeyError:
            pass
    if len(words) > 0:
        feature_vec = np.divide(feature_vec, len(words))
    return feature_vec

#最も類似したものを探す
def search_most_similar(emotion_vector,df,choice_number):
    #本来は df = pd.read_csv('word_model.csv')をここに入れる
    recommendation = df.iloc[0,0:]    #欲しい情報の範囲に変更
    tmp_max =0
    for i in range(len(df)):
        if i==choice_number:
            continue
        vect = calculate_language_vector(df.iloc[i,15])     #15列目のdivided列で判定ではなく、"img"列にdividedをリストに直したものいれたからそれつかう。
        score = 1-scipy.spatial.distance.cosine(emotion_vector, vect)
        if score > tmp_max:            #暫定より近かったら更新
            recommendation = df.iloc[i,0:]   #欲しい情報の範囲に変更
            tmp_max = score
    return recommendation

#入力された選択肢のベクトルを計算する
def calculate_emotion_vector(key_list):
    feature_vec = np.zeros((300),dtype = "float32")  #すべての要素を0とする配列を生成 個数変更する？
    for word in key_list:
        try:
            feature_vec = np.add(feature_vec, model[word])
        except:
            pass
    return feature_vec
 #np.add 配列の要素の和
                            
                               
 