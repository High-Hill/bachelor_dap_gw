# -*- coding: utf-8 -*-
import sys
import string
from datetime import datetime,timedelta
import calendar
import csv
import os

# ファイルオープン
fp = open('/path/to/program/csv_data/formatted.csv','r')
wfp = open('/path/to/program/csv_data/counted.csv','a')
writer = csv.writer(wfp, lineterminator='\n')

# 値を一時的に保存する二次元配列
temp_ip = [[0,0,0,0,0,0,0]]
j = 0
print "送信先IPアドレス格納モード"
if os.path.getsize('/home/k196336/sotsuron_program/csv_data/formatted.csv') == 0:
    print "This formatted.csv is empty!"
# ファイルが終わるまで繰り返す
for line in fp:
    # ,でsplit
    l = line.split(",")
    # 現在カウントできている値の中でlineと同じ値があるか探す
    for i in range(len(temp_ip)):
        # 時間，送信元MACアドレス，送信先IPアドレスが同じなら
        if temp_ip[i][2] == l[2] and temp_ip[i][3] == l[3] and temp_ip[i][5] == l[4]:
            temp_ip[i][6] += 1
            break
        i = i + 1
    # カウント済の値の中に同じ値がなかったら
    if i == len(temp_ip):
        # 配列を追加
        temp_ip.append([j,l[1],l[2],l[3],0,l[4],1])
        # 初期化用の配列を消す
        if j == 0:
            del temp_ip[0]
        j += 1
print "file end."
fp.close()


fp = open('/home/k196336/sotsuron_program/csv_data/formatted.csv','r')

# 値を一時的に保存する二次元配列
temp_pp = [[0,0,0,0,0,0,0]]
proto = ["","ICMP","UDP","TCP"]
dict_proto = {"ICMP":1, "UDP":2, "TCP":3}
k = 0
print "送信先プロトコル・ポート番号格納モード"
# ファイルが終わるまで繰り返す
for line in fp:
    # ,でsplit
    l = line.split(",")

    # 現在カウントできている値の中でlineと同じ値があるか探す
    for i in range(len(temp_pp)):
        # 時間，送信元MACアドレス，プロトコル，送信先ポート番号が同じなら
        if temp_pp[i][2] == l[2] and temp_pp[i][3] == l[3] and proto[temp_pp[i][4]] == l[5] and temp_pp[i][5] == int(l[6]):
            temp_pp[i][6] += 1
            break
        i = i + 1
    # カウント済の値の中に同じ値がなかったら
    if i == len(temp_pp):
        # 配列を追加
        temp_pp.append([j+k,l[1],l[2],l[3],dict_proto[l[5]],int(l[6]),1])
        # 初期化用の配列を消す
        if k == 0:
            del temp_pp[0]
        k += 1
print "file end."
# 送信先IPが同一のテーブルと，プロトコル・送信先ポート番号が同一のテーブルを結合
temp_ip.extend(temp_pp)
# counted.csvに格納
writer.writerows(temp_ip)
fp.close()
wfp.close()

