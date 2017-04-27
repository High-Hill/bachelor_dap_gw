# 攻撃側ネットワークの制御によるDoS攻撃への加担を防ぐ研究

## このリポジトリについて
このリポジトリは，弊研究室で卒業論文提出後に卒論生個人個人が必ず作成しなくてはならない *卒論フォルダ* を，外部に公開できるように少々変更を加えたものです．もしかしたら，データを消しすぎていたり反対に残りすぎたりしているかもしれません．

## ディレクトリ構造
- program/  
	卒論のプログラム本体  
    - realtime/  
		リアルタイムフィルタリングの本体  
        - cython/  
		cythonで書かれたpacket_counter.pyの本体とコンパイル用セット  
- thesis/
    - bachelor_thesis.pdf  
        卒論本体

## セットアップ

### 事前に準備して欲しいもの
- Python  
	2.7系で準備して欲しいです．3系では動きません...  
- iptables  
	基本的にはLinux系OSにプリインストールされているもので大丈夫です．  
- 環境  
	卒論本論30ページの実験環境のように，攻撃対象と攻撃者のノードがルータをまたいで繋がっていれば大丈夫です．  

### セットアップ手順
ルータにセットアップしていきます．
1. ログの採取  
    `/var/log/kern.log`に，iptablesのログが書き込まれるようにします．  
    基本的には，卒論本論の9ページにある4.2節の方法でできると思います．  
    リスト4.1のlog_prefixに設定されている`"FORWARD_F  "`がその後のプログラムのトリガになっているので，その部分だけ変えないようにお願いします．  
    また，13ページのリスト4.5のルールも先に設定しておいてください．  
    下記のように設定します．  
    ```
    # iptables -N banned
    # iptables -t filter -A banned -j LOG --log-prefix "BANNED_USER_PACKET " --log-level alert --log-tcp-sequence --log-tcp-options --log-ip-options
    # iptables -t filter -A banned -j DROP
    ```
    私はこのサイト様を参考させていただき設定しました．(2017/03/16確認）  
    http://wokowa.net/blog/archives/63  

2. ログの整形・蓄積  
    どこかのディレクトリに`program`ディレクトリのコピーを設置します．  
    設置後，crontabで定期的に実行されるようにします．  
    crontabには以下のように設定しています．一般ユーザで設置しました．  
    ```
    1 0 * * * (ファイルパス)/program/crontab/log_formatting_and_count.sh
    ```

3. applying系プログラムの設置と稼動  
    基本的に，`program`ディレクトリをそのままコピーした状態で，crontabの設定をします  
    crontabには以下のように設定しています．一般ユーザと，スーパーユーザの両方使います．  
    [一般ユーザ]  
    ```
    0 0 * * * (ファイルパス)/program/crontab/threshold_calc_and_apply.sh
    0 * * * * python (ファイルパス)/program/applying.py
    ```
    [スーパーユーザ]  
    ```
    1 * * * * (ファイルパス)/program/applying_iptables.sh
    ```

4. realtime系プログラムの設置と稼動  
    これも，`program`ディレクトリをそのままコピーしてもらえたらと思います．  
    本体は`/program/realtime/cython`の中にある`packet_counter.pyx`です．  
    これを，一度コンパイルする必要があります．下記のコマンドを打ってください．  
    `$`はプロンプトを表します．  
    ```
    $ (ファイルパス)/program/realtime/cython/setup.sh
    $ cp (ファイルパス)/program/realtime/cython/packet_counter* (ファイルパス)/program/realtime/
    $ cp -r (ファイルパス)/program/realtime/cython/build (ファイルパス)/program/realtime
    ```
    コンパイルできたら，`realtime.sh`を実行します．実行には管理者権限が必要です．  
    下記のように実行します．  
    ```
    $ sudo (ファイルパス)/program/realtime/realtime.sh &
    ```
     `banned_host.dat` がいっぱい（ルータ以下の全ノードがアクセス禁止されたことを表す）の場合，何もブロックしません．初めて動かす場合は， `banned_host.dat` が空になっているかチェックしてください．また，realtimeディレクトリに `banned_host.dat` がない場合は，作っていただきたいです．  

### 実験
 `realtime.sh` が動いている間に攻撃ノードから攻撃を行います．  
私は攻撃ツールとしてLOICとtgnを用いました．    
	- LOIC:https://sourceforge.net/projects/loic/  
	- tgn:http://manpages.ubuntu.com/manpages/trusty/man1/tgn.1.html  
注意すべきは，LOICはWindows向けの攻撃ツールで，tgnはLinux向けの攻撃ツールというところです．使いたいツールに合わせてノードを構築いただければと思います．  

## 最後に
このプログラムはまだまだ不十分で，至る所にバグがあります．  
正直なところを言うと，思った通りの動作をしない部分が殆どです．  
卒論本論で最適なqパーセント点を73としましたが，  
それも定かかどうか実験が足りていない状態です．  
また，iptablesの仕様が未だわかっていない部分があるため，  
流量制限フィルタがどの時点でかかっているのか定かでないところがあります．  
（ここが分かればもっと良い数値が出そうです）  
また，実はログファイルを何日分使うかは明確に決めていません．ログを適宜削除するプログラムを用意していないので，ずっと動かしていたらかなりログがたまってしまいます．マシンの容量がピンチの時はログデータを1週間ごとに削除するようなプログラムを動かして対処してください．（用意できていなくてごめんなさい）  

卒論も十分な添削を受けられるほどの時間がなかったので読みにくい点が多々あると思います．
疑問点やご質問等ありましたらissueやTwitterアカウント *@HighHigh_hill* までご連絡いただけますと幸いです．

