# -*- coding: utf-8 -*-
import sys
import string
from datetime import datetime,timedelta
import calendar
import csv
from operator import itemgetter
import math
from scipy import stats

# ファイルオープン(fpは引数でログファイル，wfpは書き出すcsvファイルを指定)
fp = open('/path/to/program/csv_data/counted.csv','r')
wfp = open('/path/to/program/csv_data/application.csv', 'w')
writer = csv.writer(wfp, lineterminator='\n')

weekday = ["月","火","水","木","金","土","日"]
# 今日の日付を計算
today =  datetime.now()
print "本日" + today.strftime('%Y %b %d') + "のアクセス閾値を計算します"
print "本日は" + weekday[today.weekday()] + "曜日です"

# idと書き出し用リストの変数を作成
i = 0
w = [0] * 7

# 同じ曜日のデータを格納する二次元配列
sameweek = [[0,0,0,0,0,0,0]]

# ファイルのEOFまで
for line in fp:
    line = line.strip('\n')
    l = line.split(",")
    # 曜日の一致するログを出力
    if int(l[1], 10) == today.weekday():
    #if int(l[1], 10) == 5:
        sameweek.append([l[0],int(l[1]),int(l[2]),l[3],int(l[4]),l[5],int(l[6])])

# sameweekの初期化用配列を消す
del sameweek[0]

# 時間，送信元MACアドレス，カウントタイプ，IPアドレス or ポート番号の順でソート
sameweek.sort(key=itemgetter(2,3,4,5))

# 適用用csvに格納するための配列
application = [[0,0,0,0,0,0,0]]
# 閾値計算用に，カウント値をストックする配列
stock = [0]
# id用変数
j = 0
# 先読み時の添字計算用変数
k = 1 
i = 0
# sameweekが終わるまで
while True:
    if i >= len(sameweek):
        break
    # データが最終行なら
    if i + 1 >= len(sameweek):
        # 適用用配列に格納
        application.append([j,sameweek[i][1],sameweek[i][2],sameweek[i][3],sameweek[i][4],sameweek[i][5],sameweek[i][6]])
        break
    # 今のsameweek[i]の値が複数ない場合
    if sameweek[i][2] != sameweek[i+1][2] or sameweek[i][3] != sameweek[i+1][3] or sameweek[i][4] != sameweek[i+1][4] or sameweek[i][5] != sameweek[i+1][5]:
        # 適用用配列に格納
        application.append([j,sameweek[i][1],sameweek[i][2],sameweek[i][3],sameweek[i][4],sameweek[i][5],sameweek[i][6]])
        j = j + 1
        i = i + 1
    # 今のsameweek[i]の値が複数ある場合
    else:
        while True:
            if i + k >= len(sameweek):
                i = i + k
                break
            if sameweek[i][2] != sameweek[i+k][2] or sameweek[i][3] != sameweek[i+k][3] or sameweek[i][4] != sameweek[i+k][4] or sameweek[i][5] != sameweek[i+k][5]:
                # stockのソート
                stock.sort()
                # 閾値の計算
                applyed = int(math.ceil(stats.scoreatpercentile(stock,75)))
                # 適用用配列に格納
                application.append([j,sameweek[i][1],sameweek[i][2],sameweek[i][3],sameweek[i][4],sameweek[i][5],applyed])
                j = j + 1
                # iにkを足して，次の項目に移す
                i = i + k
                # 添字,stockの初期化
                k = 1
                stock = [0]
                # while True: を抜け出す
                break
            else:
                # 初回ループのみ添字iの場合のカウント値をstockに格納
                if k == 1:
                    stock.append(sameweek[i][6])
                    # 初期値の消去
                    del stock[0]
                # 添字i+kの場合のカウント値をstockに格納
                stock.append(sameweek[i+k][6])
                k += 1

# 初期値の消去
del application[0]
# ファイルに書き込み
writer.writerows(application)
# ファイルクローズ
fp.close()
wfp.close()
