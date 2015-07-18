# Sound! Euphonium

素晴らしいラジオ番組を自動で録音するためのスクリプト。

スケジューラとTwitterでの録画完了通知機能付き。


## ENVIRONMENTS
以下の環境で動作確認済み。
* MacOSX 10.10.4
* Python 2.7.6
* pip 1.5.4


## INSTALLATION
1. 最低限必要なものをインストール
  * python(v2.7)
  * pip
  * git
2. pip経由で依存するパッケージをインストール

    ~~~bash
    pip install -r requirements.txt
    ~~~

3. プロジェクトをクローン

    ~~~bash
    git clone git@github.com:aCetylAcid/Sound-Euphonium.git
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
    channels: ["euphonium", "gg", "yryr"]
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
