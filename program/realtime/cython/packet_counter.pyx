# -*- coding: utf-8 -*-
import sys
import string
from datetime import datetime,timedelta
import calendar
import csv
import re
import os
import numpy as np
import math

def main(argv):
    # ファイルオープン
    fp = open(argv,'r')
    # 閾値が入ってるファイル
    afp = open('/path/to/program/csv_data/application.csv','r')
    # 既にbanしたホストの情報を入れるファイル
    bfp = open('/path/to/program/realtime/banned_host.dat','r')
    # idと書き出し用リストの変数を作成
    i = 0
    w = [0,0,0,0,0,0]
    # パケットカウンター
    # id，送信元MACアドレス，カウントタイプ，送信先IPアドレス，パケット数，超過パケット
    counter_ip = [[0,0,0,0,0,0]]
    # id，送信元MACアドレス，カウントタイプ，ポート番号，パケット数，超過パケット
    counter_port = [[0,0,0,0,0,0]]
    
    temptime = 20
    # 閾値を読み込む配列
    threshold_ip = [[0,0,0,0,0]]
    threshold_port = [[0,0,0,0,0]]
    # 閾値を読み込む
    for line in afp.readlines():
        line = line.strip('\n')
        l = line.split(',')
        # 時間の一致するログを出力
        #if int(l[2]) == int(date.strftime('%H')):
        if int(l[2]) == int(temptime):
            if int(l[4]) == 0:
                threshold_ip.append([l[0],l[3],l[4],l[5],l[6]])
            else:
                threshold_port.append([l[0],l[3],l[4],l[5],l[6]])
    del threshold_ip[0]
    del threshold_port[0]
    
    
    # application.csvをクローズ
    afp.close()
    
    # 既にbanされているホストのリスト
    banned_list = ['']
    # banned_host.datから既にbanされているホストの読み込み
    for line in bfp.readlines():
        line = line.strip('\n')
        banned_list = line.split(',')
    
    # プロトコルの判定用配列
    proto = ["","ICMP","UDP","TCP"]
    dict_proto = {"ICMP":1, "UDP":2, "TCP":3}
    
    # 新しくbanされるホストのリスト
    new_banned_list = ['']
    already_banned = 0
    ban_success = 1
    k = 0
    
    # 新たなパケットログを読み込む
    for line in fp.readlines():
        # kernel:の数値の[の後に空白が入ると，後のsplitでうまくきれないため，[を削除する
        line = line.replace('[','')
        line = line.replace(' DF ','    ')
        # 0文字以上の文字をsplitで切り出し
        l = filter(lambda x: len(x)>0, re.split(r" ", line))
        #昨日の日時と一致するログを出力
        # id
        w[0] = i
        # 時刻(時のみ)
        w[1] = int(l[2][:2])
        # 送信元MACアドレス
        w[2] = str(l[9][4:])
        # 送信先IPアドレス
        w[3] = str(l[11][4:])
        # プロトコル
        w[4] = l[17][6:]
        # 送信先ポート番号
        # プロトコルがICMPなら，送信先ポート番号を0に
        if l[17][6:] == "ICMP":
            l[19] = "0"
            w[5] = l[19]
        else:
            w[5] = l[19][4:]
        i += 1
        j = 0
        # counter_ipが終わるまで
        for j in xrange(len(counter_ip)):
            # パケットの送信元MACアドレスと送信先IPアドレスが一致したら
            if str(w[2]) == str(counter_ip[j][1]) and str(w[3]) == str(counter_ip[j][3]):
                # パケットをカウント
                counter_ip[j][4] = int(counter_ip[j][4]) + 1
                # 閾値と比べる 
                for k in xrange(len(threshold_ip)):
                    # パケットの送信元MACアドレスと送信先IPアドレスが一致したら
                    if threshold_ip[k][1] == counter_ip[j][1] and threshold_ip[k][3] == counter_ip[j][3]:
                        # limit値の設定
                        current_limit = math.ceil(int(threshold_ip[k][4]) / 60)
#                        print str(threshold_ip[k][3]) + " threshold: " + str(threshold_ip[k][4]) + " limit: " + str(current_limit)
                        if int(current_limit) < 1:
                            current_limit = 1
                        # 閾値をカウンタが超えていなかったら
                        if int(current_limit) > int(counter_ip[j][4]):
                            break
                        # 超過パケットのカウント
                        counter_ip[j][5] = int(counter_ip[j][5]) + 1
                        # パケットが超過するのが最初の時
                        if int(counter_ip[j][5]) == 1:
                            # 既にbanされたホストでないか調べる
                            if str(counter_ip[j][1][18:-6]) in banned_list:
                                print "already banned"
                            # 既にbanされたホストでない場合
                            else:
                                #該当ホストをブロック
                                rule = "iptables -I FORWARD 2 -m mac --mac-source " + counter_ip[j][1][18:-6] + " -j banned \n"
                                # 新しくbanされたホスト一覧に追加
                                new_banned_list.append(counter_ip[j][1][18:-6])
                                # 初期化配列の削除
                                if new_banned_list[0] == '':
                                    del new_banned_list[0]
                                # 既にbanされたホスト一覧に追加
                                banned_list.append(counter_ip[j][1][18:-6])
                                # 初期化配列の削除
                                if banned_list[0] == '':
                                    del banned_list[0]
                                print counter_ip[j][1][18:-6] + " is banned!"
                                print "ip ban. destination ip  is " + counter_ip[j][3]
                                #print str(current_limit) + " : " + str(counter_port[j][4])
                                print str(current_limit) + " : " + str(counter_ip[j][4])
                                print rule
                                ban_success = os.system(rule)
                                if ban_success == 0:
                                    #print "ban success"
                                    ban_success = 1
                        break
                    k += 1
                # for jのループから抜ける
                if k == len(threshold_ip) or int(counter_ip[j][5]) > 0:
                    #if k == len(threshold_ip):
                        #print "no host"
                    break
            j +=1
        if j == len(counter_ip) and k == 0:
            # id，送信元MACアドレス，カウントタイプ，送信先IPアドレス，パケット数，超過パケット
            counter_ip.append([int(j),str(w[2]),int(0),str(w[3]),int(1),int(0)])
        j = 0
        # counter_portが終わるまで
        for j in xrange(len(counter_port)):
            # パケットの送信元MACアドレスと送信先プロトコル，ポート番号が一致したら
            if w[2] == counter_port[j][1] and w[4] == proto[int(counter_port[j][2])] and w[5] == counter_port[j][3]:
                # パケットをカウント
                counter_port[j][4] = int(counter_port[j][4]) + 1
                # 閾値と比べる 
                for k in xrange(len(threshold_port)):
                    # パケットの送信元MACアドレスと送信先プロトコル，ポート番号が一致したら
                    if str(threshold_port[k][1]) == str(counter_port[j][1]) and int(threshold_port[k][2]) == int(counter_port[j][2]) and int(threshold_port[k][3]) == int(counter_port[j][3]):
                        # limit値の設定
                        current_limit = math.ceil(int(threshold_port[k][4]) / 60)
                        if int(current_limit) < 1:
                            current_limit = 1
                        # 閾値をカウンタが超えていたら
                        if int(current_limit) > int(counter_port[j][4]):
                            break
                        # 超過パケットのカウント
                        counter_port[j][5] = int(counter_port[j][5]) + 1
                        # パケットが超過するのが最初の時
                        if int(counter_port[j][5]) == 1:
                            # 既にbanされたホストでないか調べる
                            if str(counter_port[j][1][18:-6]) in banned_list:
                                print "already banned."
                            # 既にbanされたホストでない場合
                            else:
                                #該当ホストをブロック
                                rule = "iptables -I FORWARD 2 -m mac --mac-source " + counter_port[j][1][18:-6] + " -j banned  \n"
                                # 新しくbanされたホスト一覧に追加
                                new_banned_list.append(counter_port[j][1][18:-6])
                                # 初期化配列の削除
                                if new_banned_list[0] == '':
                                    del new_banned_list[0]
                                # 既にbanされたホスト一覧に追加
                                banned_list.append(counter_port[j][1][18:-6])
                                # 初期化配列の削除
                                if banned_list[0] == '':
                                    del banned_list[0]
                                print counter_port[j][1][18:-6] + " is banned!"
                                print "port ban. using port is " + counter_port[j][3]
                                print str(current_limit) + " : " + str(counter_port[j][4])
                                print rule
                                ban_success = os.system(rule)
                                if ban_success == 0:
                                    #print "ban success"
                                    ban_success = 1
                        break
                    k += 1
                # for jのループから抜ける
                if k == len(threshold_port) or int(counter_port[j][5]) > 0:
                    #if k == len(threshold_port):
                        # print "no host"
                    break
            j += 1 
        if j == len(counter_port) and k == 0:
            # id，送信元MACアドレス，カウントタイプ，ポート番号，パケット数，超過パケット
            counter_port.append([j,w[2],dict_proto[w[4]],w[5],1,0])
    
    bfp.close()
    # banned_host.datの更新
    bfp = open('/path/to/program/realtime/banned_host.dat','a')
    # 新しくbanされたホストが0でないなら
    if new_banned_list[0] != '':
        for i in xrange(len(new_banned_list)):
            banned_host = new_banned_list[i] + ','
            bfp.write(banned_host)
            print "banned list reflesh"
    # ファイルクローズ
    fp.close()
    bfp.close()
    
if __name__ == "__main__":
    main(sys.argv[1])
