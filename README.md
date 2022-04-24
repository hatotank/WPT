# WPT (WatchPet Twitter client)
こんな感じでEPSON TM-T88IV(有線LANモデル) を用いてTwitterのタイムラインを印刷。

※開発当時の画像なので若干古いです。

## 概要
指定アカウントのタイムラインを指定時間毎取得し、指定IPのサーマルプリンタ(TM-T88IV)で印刷。

タイムラインが絵文字で溢れているので、外字機能で絵文字を強引に印字します。
またTM-T88IVが第２水準文字までしか対応していないので、同じく外字機能でJIS X 2013まで対応。
絵文字や第３第４水準漢字の外字用元データは各フォントに依存。

タイムライン取得にはTweepyを使用するので、APIキーセット(要開発者登録)が必要になります。

アプリ名の予定は「TM Twitter client」でしたが、散々(https://twitter.com/kurumi_pgm)をテストに使用してたので、感謝と[ユーモア](https://ja.wikipedia.org/wiki/%E3%82%A6%E3%82%A9%E3%83%83%E3%83%81%E3%83%89%E3%83%83%E3%82%B0%E3%82%BF%E3%82%A4%E3%83%9E%E3%83%BC)を込めて…

## 制限事項
漢字コマンド使用のためプリンタは日本語(他に簡体字中国語/繁体字中国語モデル含む)限定
動作は多分Windowsのみ(seguiemj.ttfとGUIのタスクトレイ等)
ツイート系の処理は本質でなかったので適当になりました！ごめんな！

## 印字文字
|文字|使用フォント|
|:---|:---|
|日本語　第１、第２水準|内蔵|
|日本語　第３、第４水準|NotoSansJP-Medium.otf|
|絵文字|seguiemj.ttf|
|その他|unifont_jp-14.0.03.ttf|

## 必要な資産
- seguiemj.ttf (Windows 10 のフォント推奨)
- NotoSansJP-Medium.otf  (https://fonts.google.com/noto/specimen/Noto+Sans+JP)
- unifont_jp-14.0.03.ttf (https://unifoundry.com/pub/unifont/unifont-14.0.03/font-builds/unifont_jp-14.0.03.ttf)
- JIS0201.TXT (http://unicode.org/Public/MAPPINGS/OBSOLETE/EASTASIA/JIS/JIS0201.TXT)
- JIS0208.TXT (http://unicode.org/Public/MAPPINGS/OBSOLETE/EASTASIA/JIS/JIS0208.TXT)
- JIS0212.TXT (http://unicode.org/Public/MAPPINGS/OBSOLETE/EASTASIA/JIS/JIS0212.TXT)
- JIS0213-2004.TXT (リポジトリ参照)

## 作者
[hatotank](https://github.com/hatotank)

## ライセンス
MIT

## 必要なライブラリ
- python-escpos (https://github.com/python-escpos/python-escpos) ※2.2.0版のみ(pipからだと2.2.0版が最新だった)
- emoji (https://github.com/carpedm20/emoji/)
- Pillow (https://github.com/python-pillow/Pillow)
- tweepy (https://github.com/tweepy/tweepy)
- pystray (https://github.com/moses-palmer/pystray)

## その他
TM-T88IV
- https://www.epson.jp/support/portal/support_menu/tmt884e531.htm

TECH.REFERENCE
- https://reference.epson-biz.com/pos/reference/
- https://reference.epson-biz.com/pos/reference_ja/

参考
- python-escpos for Japanese (https://github.com/lrks/python-escpos)
- python-escpos japenese wrapper (https://github.com/iakyi/python-escpos-jp)
- 某氏の猫空 (https://blog2.k05.biz/2021/09/python-pystray.html)

---
## 使い方
1. 同フォルダの「tool_filedownload.py」にて各ファイルをダウンロード。
    ※出来ない場合は手動にてダウンロードを行ってください。
    1. JIS0201.TXT
    1. JIS0208.TXT
    1. JIS0212.TXT
    1. NotoSansJP-Medium.otf
    1. uniofnt_jp-14.0.0.ttf
1. 「seguiemj.ttf」を用意
    ※Windows10以降でしたら用意は必要ありません。
1. APIキーセットの入力(setting.ini)
1. 必要なライブラリをpip等でインストール
5. tmclient.pyを実行

## 説明画像(メイン)


## 説明画像(タスクトレイ)


## フォルダ構成
```txt
WPT
├img_list.png
├img_tile.png
├img_wpt.ico
├img_wpt.png
├JIS0201.TXT ※要ダウンロード(tool_filedownload.py)
├JIS0208.TXT ※要ダウンロード(tool_filedownload.py)
├JIS0212.TXT ※要ダウンロード(tool_filedownload.py)
├JIS0213-2004.TXT
├NotoSansJP-Medium.otf ※要ダウンロード(tool_filedownload.py)
├README.md
├seguiemj.ttf ※要Windows10以降
├settings.ini ※要Twitter API Key記述
├tm88iv.py
├tmclient.py
├tmprint.py
├tmresource.py
├tmtemporarydownload.py
├tmtweets.py
├tool_filedownload.py
└uniofnt_jp-14.0.0.ttf ※要ダウンロード(tool_filedownload.py)
```

#### APIキーセット
setting.ini に記述

```ini
[APIKEY]
consumer_key = XXXXX
consumer_secret = XXXXX
access_token = XXXXX
access_token_secret = XXXXXX
```