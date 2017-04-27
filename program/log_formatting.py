# -*- coding: utf-8 -*-
import sys
import string
from datetime import datetime,timedelta
import calendar
import csv
import re

# ファイルオープン(fpは引数でログファイル，wfpは書き出すcsvファイルを指定)
fp = open(sys.argv[1],'r')
# logがローテートするタイミングが1日の間にある場合，/var/log/kern.logと/var/log/kern.log.1の両方を読み込む必要があるかもしれない
wfp = open('/path/to/program/csv_data/formatted.csv', 'a')
writer = csv.writer(wfp, lineterminator='\n')

# 昨日の日付を計算
yesterday =  datetime.now() + timedelta(days=-1)
print "下記の日時のログ整形データをformatted.csvに書き出します"
print yesterday.strftime('%Y %b %d %H:%M:%S')

# idと書き出し用リストの変数を作成
i = 0
w = [0] * 7

# csvヘッダの作成
#w[0] = "id"
#w[1] = "weekday"
#w[2] = "hour"
#w[3] = "smacaddr"
#w[4] = "dipaddr"
#w[5] = "proto"
#w[6] = "spt"
# ファイルに1行出力
#writer.writerow(w)

# ログファイルのEOFまで
for line in fp.readlines():
    # フォワーディングパケットで，内部ネットから出るログを指定
    if line.find("FORWARD_F IN=eth1") >= 0:
        # kernel:の数値の[の後に空白が入ると，後のsplitでうまくきれないため，[を削除する
        line = line.replace('[','')
        line = line.replace(' DF ','    ')
        # 0文字以上の文字をsplitで切り出し
        l = filter(lambda x: len(x)>0, re.split(r" ", line))
        #昨日の日時と一致するログを出力
        if l[0] == yesterday.strftime('%b') and int(l[1], 10) == int(yesterday.strftime('%d'), 10):
            # print l
            # id
            w[0] = i
            # 昨日の曜日(Mon:0,Tue;1,Wed:2,Thu:3,FRI:4,SAT:5,SUN:6)
            w[1] = yesterday.weekday()
            # 時刻(時のみ)
            w[2] = int(l[2][:2], 10)
            # 送信元MACアドレス
            w[3] = l[9][4:]
            # 送信先IPアドレス
            w[4] = l[11][4:]
            # プロトコル
            w[5] = l[17][6:]
            # 送信先ポート番号
            # プロトコルがICMPなら，送信先ポート番号を0に
            if l[17][6:] == "ICMP":
                l[19] = 0
                w[6] = l[19]
            else:
                w[6] = l[19][4:]
            i += 1
            # ファイルに1行出力
            writer.writerow(w)

# ファイルクローズ
fp.close()
wfp.close()
