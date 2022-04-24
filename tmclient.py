from math import trunc
import tkinter as tk
from tkinter import messagebox
import datetime
import re
import configparser
import os
import threading
import base64
from io import BytesIO

import pystray
import tmresource
from pystray import Menu, MenuItem
from PIL import Image
from tmprint import TMPrint

is_running   = False
is_firsttime = True
maxid  = 1
tmprint = None
old_id = ''


def tm_execute():
    """ ツイッター情報印刷 """
    global tmprint
    global maxid
    global old_id
    global is_firsttime

    if tmprint is None:
        try:
            tmprint = TMPrint(tbx_host.get(),consumer_key,consumer_secret,access_token,access_token_secret)
        except Exception as e:
            messagebox.showerror("Error",e)
            thread_quit()

    maxid = tmprint.print(maxid, tbx_twid.get(), chk_retweet_var.get(), chk_reply_var.get(), rdo_viewtype_var.get())

    old_id = tbx_twid.get()
    is_firsttime = False


def tm_execute_cut():
    """ 日付変更時の用紙カット """
    global tmprint

    if tmprint is None:
        try:
            tmprint = TMPrint(tbx_host.get(),consumer_key,consumer_secret,access_token,access_token_secret)
        except Exception as e:
            messagebox.showerror("Error",e)
            thread_quit()

    tmprint.cut() # 用紙カット


def btn_run_click(from_timer=False):
    """ 実行/停止ボタンクリック """
    global is_running
    global schedule
    global nextday
    global is_firsttime
    global maxid
    global old_id

    # ウィジェットの状態取得
    # Host簡易チェック
    fillter = "[a-zA-Z0-9_.+]"
    if tbx_host.get() != "" and re.match(fillter, tbx_host.get()):
        pass
    else:
        messagebox.showwarning("警告","ホスト名が入力されていないか、使用できない文字が指定されています。")
        return
    # TwitterID簡易チェック
    if tbx_twid.get() != "" and re.match(fillter, tbx_twid.get()):
        pass
    else:
        messagebox.showwarning("警告","TwitterIDが入力されていないか、使用できない文字が指定されています。")
        return
    
    # インターバル時間を求める
    next_minute = (datetime.datetime.now() + datetime.timedelta(minutes=rdo_m_var.get())).minute
    diff = abs(next_minute % rdo_m_var.get())
    schedule = datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(minutes=rdo_m_var.get() - diff)).strftime("%Y-%m-%d %H:%M") + ":00","%Y-%m-%d %H:%M:%S")    

    # IDが変更されたらMAXID初期化
    if not is_firsttime and tbx_twid.get() != old_id:
        maxid = 1
        old_id = tbx_twid.get()
        is_skyes = messagebox.askyesno("確認","IDが変更されました。\n初回印字を実行しますか？")
        if is_skyes: # Yes
            is_firsttime = True
            chk_ft_exec_var.set(True)
        else:        # No
            chk_ft_exec_var.set(False)

    if trunc((schedule - datetime.datetime.now()).seconds / 60) < 5:
        # 初回印字
        if is_firsttime and chk_ft_exec_var.get():
            schedule = datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(minutes=rdo_m_var.get() - diff + rdo_m_var.get())).strftime("%Y-%m-%d %H:%M") + ":00","%Y-%m-%d %H:%M:%S")

    # 用紙カット日付
    nextday = datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d") + " 00:00:00","%Y-%m-%d %H:%M:%S")

    # ボタン等の使用可否セット
    if is_running == True and from_timer == False:
        is_running = False
        tbx_host.configure(state="normal")
        tbx_twid.configure(state="normal")
        chk_ft_exec.configure(state="normal")
        rdo_m05.configure(state="normal")
        rdo_m10.configure(state="normal")
        rdo_m15.configure(state="normal")
        rdo_m20.configure(state="normal")
        rdo_m30.configure(state="normal")
        chk_datechange.configure(state="normal")
        chk_retweet.configure(state="normal")
        chk_reply.configure(state="normal")
        rdo_tile.configure(state="normal")
        rdo_list.configure(state="normal")
        
        btn_run["text"] = "実行"
        lbl_statusbar["text"] = "待機中　次回取得:"
        root.after_cancel(timerid)
    else:
        is_running = True
        tbx_host.configure(state="readonly")
        tbx_twid.configure(state="readonly")
        chk_ft_exec.configure(state="disable")
        rdo_m05.configure(state="disable")
        rdo_m10.configure(state="disable")
        rdo_m15.configure(state="disable")
        rdo_m20.configure(state="disable")
        rdo_m30.configure(state="disable")
        chk_datechange.configure(state="disable")
        chk_retweet.configure(state="disable")
        chk_reply.configure(state="disable")
        rdo_tile.configure(state="disable")
        rdo_list.configure(state="disable")

        btn_run["text"] = "停止"
        lbl_statusbar["text"] = "実行中　次回取得:" + schedule.strftime("%Y-%m-%d %H:%M:%S")
        if is_firsttime and chk_ft_exec_var.get():
            tm_execute()
        root.after(1000, timer)


def is_exist_file(target_file):
    """ ファイルの存在チェックし、存在しなかったら終了 """
    if not os.path.isfile(target_file):
        messagebox.showerror("エラー", target_file + "が見つかりません。")
        exit()


#参考 (某氏の猫空 https://blog2.k05.biz/2021/09/python-pystray.html)
#===========================
# タイマーイベント関数
#===========================
def timer():
    global schedule
    global timerid
    global nextday

    if is_running == True:
        now = datetime.datetime.now()
        if schedule < now:
            tm_execute()
            # スケジュール更新
            btn_run_click(True)
        
        if nextday < now:
            nextday = datetime.datetime.strptime((now + datetime.timedelta(days=1)).strftime("%Y-%m-%d") + " 00:00:00","%Y-%m-%d %H:%M:%S")
            tm_execute_cut()

        timerid = root.after(1000, timer)


#===========================
# スレッド関係の関数
#===========================
def thread_st():
    global icon
    global root

    #-----------------------
    # メニュー
    #-----------------------
    options_map = {'再表示': lambda:[root.after(0,root.deiconify)], '終了': lambda: root.after(1, thread_quit)} #変更 update

    items = []
    for option, callback in options_map.items():
        items.append(MenuItem(option, callback, default=True if option == 'Show' else False))

    menu = Menu(*items)
   
    #-----------------------
    # アイコン表示
    #-----------------------
    image = Image.open(BytesIO(base64.b64decode(tmresource.img_wpt_png)))
    icon = pystray.Icon("name", image, "WPT", menu)
    icon.run()

def thread_quit():
    global icon
    global root

    icon.stop()
    root.destroy()

#===========================
# メイン 関数
#===========================
def main():
    global root
    global tbx_host
    global tbx_twid
    global btn_run
    global chk_ft_exec
    global chk_ft_exec_var
    global rdo_m_var
    global rdo_m05
    global rdo_m10
    global rdo_m15
    global rdo_m20
    global rdo_m30
    global chk_datechange
    global chk_datechange_var
    global chk_retweet
    global chk_retweet_var
    global chk_reply
    global chk_reply_var
    global rdo_list
    global rdo_tile
    global rdo_viewtype_var
    global lbl_statusbar
    global consumer_key
    global consumer_secret
    global access_token
    global access_token_secret

    #-----------------------
    # ウィジェット表示
    #-----------------------
    root = tk.Tk()
    #root.title("tmtwitterclient")
    root.title("WPT")
    root.geometry("300x300")
    root.resizable(False, False)
    root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(data=tmresource.img_wpt_png))

    # ラベル(host)
    lbl_host = tk.Label(root)
    lbl_host["text"] = "サーマルプリンタのホスト名 または IPアドレス"
    lbl_host.place(x=12, y=6)
    # テキストボックス
    tbx_host = tk.Entry(root)
    tbx_host["width"] = 44
    tbx_host.place(x=12, y=27)
    # ラベル(TwitterID)
    lbl_twid = tk.Label(root)
    lbl_twid["text"] = "Twitter ID か ユーザー名 (例:@lindsay → lindsay)"
    lbl_twid.place(x=12, y=48)
    # テキストボックス
    tbx_twid = tk.Entry(root)
    tbx_twid["width"] = 44
    tbx_twid.place(x=12, y=69)
    # ボタン
    btn_run = tk.Button(root)
    btn_run["text"] = "実行"
    btn_run["width"] = 16
    btn_run.place(x=83, y=94)
    btn_run["command"] = btn_run_click
    # 初回印字
    chk_ft_exec_var = tk.BooleanVar()
    chk_ft_exec_var.set(True)
    chk_ft_exec = tk.Checkbutton(root,variable=chk_ft_exec_var)
    chk_ft_exec["text"] = "初回印字"
    chk_ft_exec.place(x=210, y=154)
    # ラベル(取得間隔)
    lbl_interval = tk.Label(root)
    lbl_interval["text"] = "取得間隔(分)"
    lbl_interval.place(x=12, y=132)
    # ラジオボタン(インターバル間隔)
    rdo_m_var = tk.IntVar()
    rdo_m_var.set(20)
    rdo_m05 = tk.Radiobutton(root, variable=rdo_m_var, value=5)
    rdo_m05["text"] = "5"
    rdo_m05.place(x=90, y=132)
    rdo_m10 = tk.Radiobutton(root, variable=rdo_m_var, value=10)
    rdo_m10["text"] = "10"
    rdo_m10.place(x=130, y=132)
    rdo_m15 = tk.Radiobutton(root, variable=rdo_m_var, value=15)
    rdo_m15["text"] = "15"
    rdo_m15.place(x=170, y=132)
    rdo_m20 = tk.Radiobutton(root, variable=rdo_m_var, value=20)
    rdo_m20["text"] = "20"
    rdo_m20.place(x=210, y=132)
    rdo_m30 = tk.Radiobutton(root, variable=rdo_m_var, value=30)
    rdo_m30["text"] = "30"
    rdo_m30.place(x=250, y=132)
    # チェックボックス(日付変更用紙カット)
    chk_datechange_var = tk.BooleanVar()
    chk_datechange_var.set(True)
    chk_datechange = tk.Checkbutton(root,variable=chk_datechange_var)
    chk_datechange["text"] = "日付が変わったら用紙をカット"
    chk_datechange.place(x=12, y=154)
    # チェックボックス(リツイート含む)
    chk_retweet_var = tk.BooleanVar()
    chk_retweet = tk.Checkbutton(root, variable=chk_retweet_var)
    chk_retweet["text"] = "リツイートを含む"
    chk_retweet.place(x=12, y=176)
    # チェックボックス(リプライを含む)
    chk_reply_var = tk.BooleanVar()
    chk_reply = tk.Checkbutton(root, variable=chk_reply_var)
    chk_reply["text"] = "リプライを含む"
    chk_reply.place(x=12, y=198)
    # ラベル(画像表示タイプ)
    lbl_viewtype = tk.Label(root)
    lbl_viewtype["text"] = "画像表示タイプ"
    lbl_viewtype.place(x=12, y=220)
    # ラジオボタン(タイル表示、リスト表示)
    rdo_viewtype_var = tk.IntVar()
    rdo_viewtype_var.set(0)
    rdo_tile = tk.Radiobutton(root, variable=rdo_viewtype_var, value=0)
    rdo_tile["text"] = "タイル表示"
    rdo_tile.place(x=22, y=242)
    rdo_list = tk.Radiobutton(root, variable=rdo_viewtype_var, value=1)
    rdo_list["text"] = "リスト表示"
    rdo_list.place(x=160, y=242)
    # キャンパス(タイル表示、リスト表示)
    img_rdolist = tk.PhotoImage(data=tmresource.img_list_png)
    img_rdotile = tk.PhotoImage(data=tmresource.img_tile_png)
    cvs_tile = tk.Canvas(width=32,height=32)
    cvs_tile.place(x=100,y=238)
    cvs_tile.create_image(0,0,image=img_rdotile,anchor=tk.NW)
    cvs_list = tk.Canvas(width=32,height=32)
    cvs_list.place(x=240,y=238)
    cvs_list.create_image(0,0,image=img_rdolist,anchor=tk.NW)
    # ステータスバーもどき
    lbl_statusbar = tk.Label(root, bd=1, relief=tk.SUNKEN, anchor=tk.W)
    lbl_statusbar["text"] = "待機中　次回取得:"
    lbl_statusbar.pack(sid=tk.BOTTOM, fill=tk.X)

    # Twitter API key 読み込み
    try:
        config = configparser.ConfigParser()
        config.read("settings.ini")
        consumer_key = config['APIKEY']['consumer_key']
        consumer_secret = config['APIKEY']['consumer_secret']
        access_token = config['APIKEY']['access_token']
        access_token_secret = config['APIKEY']['access_token_secret']
        if not (len(consumer_key) > 0 and len(consumer_secret) > 0 and len(access_token) > 0 and len(access_token_secret) > 0):
            raise Exception
    except Exception as e:
        messagebox.showerror("設定の読み込みに失敗", "settings.iniを確認してください。")
        exit()

    # 各ファイル確認
    # text
    is_exist_file("JIS0201.TXT")
    is_exist_file("JIS0208.TXT")
    is_exist_file("JIS0212.TXT")
    is_exist_file("JIS0213-2004.TXT")
    # font
    is_exist_file("NotoSansJP-Medium.otf")
    is_exist_file("unifont_jp-14.0.03.ttf")

    #-----------------------
    # Xボタンを押された時の処理
    #-----------------------
    root.protocol('WM_DELETE_WINDOW', lambda:root.withdraw())

    #-----------------------
    # スレッド開始
    #-----------------------
    threading.Thread(target=thread_st).start()

    #-----------------------
    # イベント待機
    #-----------------------
    root.mainloop()

#===========================
# 実行
#===========================
main()