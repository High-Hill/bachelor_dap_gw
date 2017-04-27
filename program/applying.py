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
mfp = open('/path/to/program/csv_data/most_threshold.csv','r')
wfp = open('/path/to/program/applying_iptables.sh', 'w')
hfp = open('/path/to/program/host_stock.txt','r')

weekday = ["月","火","水","木","金","土","日"]
# 今日の日付を計算
today =  datetime.now()
print "本日" + today.strftime('%Y %b %d') + "のルールをプリントします"
print "本日は" + weekday[today.weekday()] + "曜日です"
print "現在" + today.strftime('%H') + "時です"

# idと書き出し用リストの変数を作成
i = 0
j = 0
w = [0] * 7

temptime = 20
# 同じ曜日のデータを格納する二次元配列
sametime_ip = [[0,0,0,0,0,0,0]]
sametime_port = [[0,0,0,0,0,0,0]]

# ファイルのEOFまで
for line in fp:
    line = line.strip('\n')
    l = line.split(",")
    # 時間の一致するログを出力
    #if int(l[2]) == int(today.strftime('%H')):
    if int(l[2]) == temptime:
        if int(l[4]) == 0:
            sametime_ip.append([l[0],int(l[1]),int(l[2]),l[3],int(l[4]),l[5],int(l[6])])
        else:
            sametime_port.append([l[0],int(l[1]),int(l[2]),l[3],int(l[4]),l[5],int(l[6])])

# sametimeの初期化用配列を消す
del sametime_ip[0]
del sametime_port[0]

# 閾値の最大値のデータを格納する二次元配列
most_ip = [[0,0,0,0,0]]
most_port = [[0,0,0,0,0]]
# most threshold
# ファイルのEOFまで
for line in mfp:
    line = line.strip('\n')
    l = line.split(",")
    if int(l[2]) == 0:
        most_ip.append([l[0],l[1],int(l[2]),l[3],int(l[4])])
    else:
        most_port.append([l[0],l[1],int(l[2]),l[3],int(l[4])])

# 初期化用配列を消す
del most_ip[0]
del most_port[0]

# 時間，送信元MACアドレス，カウントタイプ，IPアドレス or ポート番号の順でソート
sametime_ip.sort(key=itemgetter(2,3,4,5))
sametime_port.sort(key=itemgetter(2,3,4,5))
most_ip.sort(key=itemgetter(1,2,3))
most_port.sort(key=itemgetter(1,2,3))

# 既に存在するルールのクリーンアップ
# host数に合わせて，rangeの中身を変える
for line in hfp:
    line = line.strip('\n')
    l = line.split(",")

for i in range(len(l)):
    rule = "iptables -D FORWARD 2 \n"
    print rule
    wfp.write(rule)
    rule = "iptables -F host" + str(i) + "\n"
    print rule
    wfp.write(rule)
    rule = "iptables -X host" + str(i) + "\n"
    print rule
    wfp.write(rule)

# id用変数
j = 0
# 先読み時の添字計算用変数
k = 0 
# ルール一行を格納する変数
rule = ''
# 送信元MACアドレスを格納する配列
stock = ['']
# rate値の格納
rate = 0
burst = 0
# chain name
chain_name = ''
# MACアドレスを格納する
mac = ''
# カウントタイプごとにルールを変更する
count_rule = ["icmp","udp --sport","tcp --sport"]
# sametime_portが終わるまで
for i in range(len(sametime_port)):
    l = 0
    while True:
        if l == len(stock):
            stock.append(sametime_port[i][3])
            if stock[0] == '':
                del stock[0]
            chain_name = "host" + str(len(stock) - 1)
            # ruleにiptablesの形式でルールを書く
            # 独自チェインの作成
            rule = "iptables -N " + chain_name + "\n"
            print rule
            # シェルスクリプトに追加
            wfp.write(rule)
            # iptables上のMACアドレスを普通のMACアドレスに変換
            mac = str(stock[len(stock) -1])
            mac = mac[18:-6]
            # ruleにiptablesの形式でルールを書く
            # 該当のMACアドレスを独自チェインに通す
            rule = "iptables -A FORWARD -m mac --mac-source " + mac + " -j " + chain_name + "\n"
            print rule
            # シェルスクリプトに追加
            wfp.write(rule)
            break
        else:
            if sametime_port[i][3] == str(stock[l]):
                chain_name = "host" + str(l)
                break
            l += 1
    # ポートの閾値の最大値を取ってくる
    for l in range(len(most_port)):
        # 送信元MACアドレス，カウントタイプ，ポート番号が一致すれば
        if sametime_port[i][3] == str(most_port[l][1]) and sametime_port[i][4] == most_port[l][2] and sametime_port[i][5] == str(most_port[l][3]):
            # rate値の計算
            rate = most_port[l][4] / 3600
            # rateが0になりそうな時は，強制的に1にする
            if rate <= 1:
                rate = 1
            burst = sametime_port[i][6]
            # burst値は10000より上の値を設定できない．そのため，10000を超えるようなら10000とする．
            if burst > 10000:
                burst = 10000

    #icmpなら，ポート番号指定がいらなくなる
    if sametime_port[i][4] == 1:
        # ruleにiptablesの形式でルールを書く
        rule = "iptables -A " + chain_name + " -p " + count_rule[sametime_port[i][4] - 1] + " -m limit --limit " + str(rate) + "/second --limit-burst " + str(burst) + " -j ACCEPT\n"
    else:
        # ruleにiptablesの形式でルールを書く
        rule = "iptables -A " + chain_name + " -p " + count_rule[sametime_port[i][4] - 1] + " " + sametime_port[i][5] + " -m limit --limit " + str(rate) + "/second --limit-burst " + str(burst) + " -j ACCEPT\n"
    print rule
    # シェルスクリプトに追加
    wfp.write(rule)

# 同一送信先IPアドレスへのアクセス最大値の計算
most_stock = [0] * len(stock)
for i in range(len(stock)):
    for j in range(len(most_ip)):
        if str(most_ip[j][1]) == str(stock[i]):
            if most_stock[i] < most_ip[j][4]:
                # 同一IPアドレスへの1時間の最大アクセス数
                most_stock[i] = most_ip[j][4] 
    print most_stock[i]
    print stock[i]
    # 何もアクセスのない時間帯だった場合
    if most_stock[i] / 3600 < 1:
        # rateに設定できる最小値
        rate = 1
    else:
        # rate(dst_ip) = 同一IPアドレスへの1時間の最大アクセス数/1時間の秒数
        rate = most_stock[i] / 3600
    if most_stock[i] <= 5:
        # hashlimitのデフォルトのburst
        burst = 5
    elif most_stock[i] > 10000:
        # hashlimitのデフォルトのburst
        burst = 10000
    else:
        # burst(dst_ip) = 同一IPアドレスへの1時間の最大アクセス数
        burst = most_stock[i]
    rule = "iptables -A host" + str(i) + " -m hashlimit --hashlimit " + str(rate) + "/sec --hashlimit-burst " + str(burst) + " --hashlimit-mode dstip --hashlimit-name sameip_filter --hashlimit-htable-expire 3600000 -j ACCEPT\n" 
    print rule
    wfp.write(rule)

     
rule = "iptables-save > /etc/iptables/iptables.rules \n"
wfp.write(rule)
hfp.close()
hfp = open('/home/k196336/sotsuron_program/host_stock.txt','w')
print stock
for i in range(len(stock)):
    hfp.write(stock[i] + ",")
# ファイルクローズ
fp.close()
mfp.close()
wfp.close()
hfp.close()
