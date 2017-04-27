# -*- coding: utf-8 -*-
import sys
import string
from datetime import datetime,timedelta
import calendar
import csv
from operator import itemgetter
import math

# ファイルオープン(fpは引数でログファイル，wfpは書き出すcsvファイルを指定)
fp = open('/path/to/program/csv_data/application.csv','r')
wfp = open('/path/to/program/csv_data/most_threshold.csv', 'w')
most_writer = csv.writer(wfp, lineterminator='\n')

weekday = ["月","火","水","木","金","土","日"]
# 今日の日付を計算
today =  datetime.now()
print "各最大の閾値を計算します"
# idと書き出し用リストの変数を作成
i = 0
j = 0
w = [0] * 7

temptime = 6
# 同じ曜日のデータを格納する二次元配列
alldata = [[0,0,0,0,0,0,0]]
# 同一IP,ポートの中での最大の閾値を格納する配列
# id,MACアドレス,カウントタイプ，IPアドレスorポート番号，閾値
most_threshold = [[0,0,0,0,0]]

# ファイルのEOFまで
for line in fp:
    line = line.strip('\n')
    l = line.split(",")
    alldata.append([l[0],int(l[1]),int(l[2]),l[3],int(l[4]),l[5],int(l[6])])

del alldata[0]

alldata.sort(key=itemgetter(3,4,5))

i = 0
k = 0
count = 1
stock = 0
# データが終了するまで
while True:
    # 次のデータで終了なら
    if i + 1 == len(alldata):
        most_threshold.append([k,alldata[i][3],alldata[i][4],alldata[i][5],alldata[i][6]])
        break
    # 添字がデータ数を超えていれば
    elif i >= len(alldata):
        break

    # 次のデータが同じMACアドレス，カウントタイプ，IPアドレスorポート番号でないなら
    if alldata[i][3] != alldata[i+1][3] or alldata[i][4] != alldata[i+1][4] or alldata[i][5] != alldata[i+1][5]:
        most_threshold.append([k,alldata[i][3],alldata[i][4],alldata[i][5],alldata[i][6]])
        k += 1
        i += 1
    else:
        # 違う項目のデータが出てくるまで繰り返す
        while True:
            if i + count == len(alldata):
                i = i + count
                break

            # 次のデータが同じMACアドレス，カウントタイプ，IPアドレスorポート番号でないなら
            if alldata[i][3] != alldata[i+count][3] or alldata[i][4] != alldata[i+count][4] or alldata[i][5] != alldata[i+count][5]:
                # 閾値の最大値を追加する
                most_threshold.append([k,alldata[i][3],alldata[i][4],alldata[i][5],stock])
                stock = 0
                i = i + count
                count = 0
                k += 1
                break
            else:
                # 過去の閾値の最大値と現在ピックアップしている閾値を比べる
                if int(stock) < int(alldata[i+count][6]):
                    stock = int(alldata[i+count][6])
                count += 1

# sameweekの初期化用配列を消す
del most_threshold[0]

# 閾値の最大値をcsvに格納
most_writer.writerows(most_threshold)

# ファイルクローズ
fp.close()
wfp.close()
