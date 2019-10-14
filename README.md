# Sound! Euphonium

素晴らしいラジオ番組を自動で録音するためのスクリプト。

スケジューラとTwitterでの録画完了通知機能付き。


## ENVIRONMENTS
以下の環境で動作確認済み。
* CentOS 6.10
* Python 2.6.8
* pip 18.1


## INSTALLATION
1. 最低限必要なものをインストール
  * python
  * pip
  * git
  
※HLSで配信されている番組を録音する場合、下記も必要

  * lame
  * ffmpeg(4.X)
    - lameとopensslを有効化すること(ビルド設定例: `./configure --enable-gpl --enable-shared --enable-nonfree --enable-openssl --enable-libmp3lame\`)

2. プロジェクトをクローン

    ~~~bash
    git clone git@github.com:zrn-ns/Sound-Euphonium.git
    ~~~

3. pip経由で依存するパッケージをインストール

    ~~~bash
    pip install -r requirements.txt
    ~~~


## HOW TO USE
* "downloadd.py" を実行すると、自動での録音が開始します。

    ~~~bash
    python downloadd.py
    ~~~

* Twitter通知を有効にしていると、自動録音が完了したタイミングでTwitterへ通知されます。


## CUSTOMIZE
* 録音する番組を変更したい場合は、user_settings.ymlの "channels" を書き換えてください。

    ~~~yaml
    # mp3で配信されている番組は番組のID（お便りの送り先のID）を指定
    channels: ["gurepa"]
    
    # HLSで配信されている番組は、番組のIDのあとにコロン区切りで数字のID(アプリから番組情報取得するときに投げてるやつ)を指定
    # また、HLSで配信されている番組を録音するには、ベアラー認証用のKeyが必要。アプリの通信ごにょごにょして手に入れる)
    channels: ["gurepa", "gurepap:562"]
    bearer_token: "hogehoge"
    ~~~

* Twitterでエラー、録画完了通知を受け取りたい場合は、user_settings.ymlの "twitter_settings" を書き換えてください。"in_reply_to" には、通知先のアカウントのTwitterIDを指定してください。
* 録音したファイルの保存場所を変更したい場合は、user_settings.ymlの "radio_save_path" を書き換えてください。


## LISENSE
* This software is released under the MIT License, see [LICENSE](https://github.com/aCetylAcid/Sound-Euphonium/blob/master/LICENSE).


## CHANGELOG
* v0.1
  - 最低限の機能を実装。
* v0.2
  - 定期実行の実装
  - Twitterでの完了通知を実装
* v1.0
  - HLSで配信されている番組の録音に対応
  
  
