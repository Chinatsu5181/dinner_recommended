#スクレイピング
import bs4
import traceback
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import random

# ドライバーのフルパス
CHROMEDRIVER = "C:\chromedriver.exe"
# 改ページ（最大）
PAGE_MAX = 4
# 遷移間隔（秒）
INTERVAL_TIME = 3


# ドライバー準備
def get_driver():
    # ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')
 
    # ブラウザーを起動
    driver = webdriver.Chrome(CHROMEDRIVER, options=options)
 
    return driver
 

 # 対象ページのソース取得
def get_source_from_page(driver, page):
    try:
        # ターゲット
        driver.get(page)
        driver.implicitly_wait(10)  # 見つからないときは、10秒まで待つ
        page_source = driver.page_source
 
        return page_source
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return None


 
# ソースからスクレイピングする
def get_data_from_source(src):
    # スクレイピングする
    soup = bs4.BeautifulSoup(src, features='lxml')

    try:
        info = []
        elems = soup.find_all(class_="list-rst")
 
        for elem in elems:
 
            shop = {}
            shop["rank"] = None
            shop["name"] = None
            shop["area"] = None
            shop["genre"] = None
            shop["star"] = None
            shop["rvw_count"] = None
            shop["dinner_budget"] = None
            shop["lunch_budget"] = None
            shop["holiday_data"] = None
            shop["search_word"] = None
            shop["pr"] = None
            shop["review"] = None
            shop["url"]=None
            shop["total"]=None
            shop["divided"]=None              #レコメンドの作業用


            #テキストの両端にスペース類がある場合は、get_text()のstrip引数にTrueを指定してスペース類をストリップ（削除）します。
            # 順位
            rank = elem.find(class_="list-rst__rank-badge-no").text
            if rank:
                shop["rank"] = rank
 
            # 店舗名
            name = elem.find(class_="list-rst__rst-name-target").text
            if name:
                shop["name"] = name
 
            # 地域とジャンル
            area_genre = elem.find(class_="list-rst__area-genre").text
            if area_genre:
                area_genre_list = area_genre.split("/")
                if len(area_genre_list) == 2:
                    shop["area"] = my_trim(area_genre_list[0])
 
                    tmp_genre = area_genre_list[1]
                    tmp_genre_list = tmp_genre.split("、")
                    genre_list = []
                    for genre in tmp_genre_list:
                        genre_list.append(my_trim(genre))
                    shop["genre"] = genre_list
 
            # 評価
            star = elem.find(class_="list-rst__rating-val").text
            if star:
                shop["star"] = star
 
            # 評価
            rvw_count = elem.find(class_="list-rst__rvw-count-num").text
            if rvw_count:
                shop["rvw_count"] = rvw_count
 
            # 予算
            budget_elems = elem.find_all(class_="c-rating-v3__val")
            if len(budget_elems) == 2:
                shop["dinner_budget"] = budget_elems[0]
                shop["lunch_budget"] = budget_elems[1]
 
 
            # 休日
            if elem.find(class_="list-rst__holiday-text"):
                holiday_data = elem.find(class_="list-rst__holiday-text")
                if holiday_data:
                    shop["holiday_data"] = holiday_data
 
            # 検索キーワード
            search_word_elems = elem.find_all(class_="list-rst__search-word-item")
 
            if len(search_word_elems) > 0:
                search_word_list = []
                for search_word_elem in search_word_elems:
                    search_word = search_word_elem.text
                    if my_trim(search_word):
                        search_word_list.append(my_trim(search_word))
                shop["search_word"] = search_word_list
 
            # 画像
            if elem.find(class_="list-rst__rst-photo"):
                photo_set_str = elem.find(class_="list-rst__rst-photo").attrs['data-photo-set']
 
                if photo_set_str:
                    tmp_photo_set = photo_set_str.split("、")
                    img_list = []
                    for img in tmp_photo_set:
                        img_list.append(img)
                    shop["img"] = img_list

            # pr文
            pr = elem.find(class_="list-rst__pr-title cpy-pr-title")
            if pr:
                shop["pr"] = pr.text

            # 口コミ
            review = elem.find(class_="list-rst__comment-text cpy-comment-text")
            if review:
                shop["review"] = review.text

            #ジャンル,pr,口コミ レコメンド用に内容分まとめる
            shop["total"]=shop["genre"]
            shop["total"].append(str(shop["pr"])+str(shop["review"]))

            #url 12retumr 

            # findを使ってリンク要素を取得
            link = soup.find(class_="list-rst")
            # getでリンク要素のhref属性の値を取得して出力
            shop["url"]=link.get('data-detail-url')



            info.append(shop)
            
        print(info)
        return info
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return None
 
 # 次のページへ遷移
def next_btn_click(driver):
    try:
        # 次へボタン
        elem_btn = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "c-pagination__arrow--next"))
        )
 
        actions = ActionChains(driver)
        actions.move_to_element(elem_btn)
        actions.click(elem_btn)
        actions.perform()
 
        # 間隔を設ける(秒単位）
        time.sleep(INTERVAL_TIME)
 
        return True
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return False
 
def my_trim(text):
    text = text.replace("\n", "")
    return text.strip()
 
def choosenumber(data):
  ns = []
  while len(ns) < 3:
    n = random.randrange(len(data))
    if not n in ns:
      ns.append(n)
  return ns


def getchoices(i,df):
  choice=[]
  choice.append(df.iloc[i,1])#名前
  choice.append(df.iloc[i,2])#場所
  choice.append(df.iloc[i,3])#ジャンル
  choice.append(df.iloc[i,4])#評価
  choice.append(df.iloc[i,12])#URL

  return choice