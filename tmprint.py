from tm88iv import TM88IV
from tmtweets import TMTweets
from tmtemporarydownload import TemporaryDownload
from PIL import Image,ImageDraw
import datetime

class TMPrint:
    """ TMPrint

    Twitter printing for TM88IV
    """

    def __init__(self, host, consumer_key, consumer_secret, access_token, access_token_secret):
        """

        Parameters
        ----------
        host : str
            Printer's hostname or IP address
        consumer_key : str
            consumer_key
        consumer_secret : str
            consumer_secret
        access_token : str
            access_token
        access_token_secret : str
            access_token_secret
        """
        self.p = TM88IV(host)
        self.t = TMTweets(consumer_key, consumer_secret, access_token, access_token_secret)
        self.tmp = TemporaryDownload()


    # カウント丸め ------------------------------------------------------------------
    def _twround(self, count):
        """ カウント丸め

        カウント数をK,M,G単位で丸めて、5桁の文字列(スペース埋め)で返却(カウント数1000未満は単位なし)

        Parameters
        ----------
        count : int
            カウント数

        Returns
        -------
        str
            丸めたカウント数(xxx,xxxK,xxxM,xxxG)
        """
        if   count >= 1000000000: # G
            round_text = str(divmod(count, 1000000000)[0]) + 'G'
        elif count >= 1000000:    # M
            round_text = str(divmod(count, 1000000)[0]) + 'M'
        elif count >= 1000:       # K
            round_text = str(divmod(count, 1000)[0]) + 'K'
        else:
            round_text = str(count)
        return round_text.ljust(5)


    # 区切り線出力 ------------------------------------------------------------------
    def _twht(self, tw_type):
        """ 区切り線出力

        Parameters
        ----------
        tw_type : int
            ツイートタイプ(0:通常、1:メンション,引用)
        """
        if tw_type == 1:
            self.p._raw(b'\x1D\x4C\x18\x00') # GS L 左マージンの設定
            self.p.jptext2("────────────────────\n")
            self.p._raw(b'\x1D\x4C\x00\x00') # GS L 左マージンの設定
        else:
            self.p.jptext2("─────────────────────\n")


    # 取得時のタイムスタンプ出力 ----------------------------------------------------------
    def _twht_timestamp(self):
        """ 取得時のタイムスタンプ出力 """
        str = "  " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "   \n"
        self.p.jptext2("\n")
        self.p.jptext2(str, dw=True,dh=True,wbreverse=True,bflg=True)


    # 新しい画像サイズ取得 --------------------------------------------------------------
    def _twgetnewsize(self, img_height, img_width, max_height, max_width):
        """ 新しい画像サイズ取得

        Parameters
        ----------
        img_height : int
            画像の高さ
        img_width : int
            画像の幅
        max_height : int
            最大の高さ
        max_width : int
            最大の幅

        Returns
        -------
        (nh,nw,dh,dw) : tuple
            nh:高さ,nw:幅,dh:高さオフセット,dw:幅オフセット
        """
        nh = max_height
        nw = round(img_width * nh / img_height)
        dh = 0
        dw = round((nw - max_width) / 2)
        if nw < max_width:
            nw = max_width
            nh = round(img_height * nw / img_width)
            dh = round((nh - max_height) / 2)
            dw = 0

        return nh,nw,dh,dw


    # 画像出力 --------------------------------------------------------------------
    def _twimage(self, img_ary, tw_type, output_type=0):
        """ 画像出力

        Parameters
        ----------
        img_ary : str[]
            画像ファイル名配列
        tw_type : int
            ツイートタイプ(0:通常、1:メンション,引用)
        output_type : int
            出力タイプ(0:Twitterと大体同じ,1:そのまま出力)
        """
        img_count = len(img_ary)
        if img_count < 1:
            return

        h_max_tm88iv = 1662
        w_max_tm88iv = 512

        if tw_type == 1:
            w  = 481 # -24 = 481 -3 -> 239
            h  = 269 #     = 269 -3 -> 133
            w2 = 239
            h2 = 269
            w3 = 239
            h3 = 133
            w4 = 239
            h4 = 133
        else:
            w  = 505
            h  = 284
            w2 = 251
            h2 = 284
            w3 = 251
            h3 = 140
            w4 = 251
            h4 = 141

        """
        <--             505             --> 
        +----------------+----------------+ ^
        |<--   251    -->| ^ <--  251  -->| |
        |                | | 140          |   ^
        |                | v              | 2 |
        +----------------|----------------+ 8 3
        |                | ^              | 4 |
        |                | | 141          |   v
        |                | v              | |
        +----------------+----------------+ v
                    <-3-> 
        """

        if img_count > 4 or img_count == 1:
            output_type = 1

        if output_type == 0:
            # 画像4枚
            if img_count == 4:
                base = Image.new("L", (w,h), 0).convert("L")
                img1 = Image.open(img_ary[0])
                nh,nw,dh,dw = self._twgetnewsize(img1.height,img1.width,h3,w3)
                img1 = img1.resize((nw,nh))
                base.paste(img1.crop((dw, dh, dw+w3, dh+h3)),(0,0))
                img2 = Image.open(img_ary[1]).convert("L")
                nh,nw,dh,dw = self._twgetnewsize(img2.height,img2.width,h4,w4)
                img2 = img2.resize((nw,nh))
                base.paste(img2.crop((dw, dh, dw+w4, dh+h4)),(0,h4+3))
                img3 = Image.open(img_ary[2]).convert("L")
                nh,nw,dh,dw = self._twgetnewsize(img3.height,img3.width,h3,w3)
                img3 = img3.resize((nw,nh))
                base.paste(img3.crop((dw, dh, dw+w3, dh+h3)),(w3+3,0))
                img4 = Image.open(img_ary[3]).convert("L")
                nh,nw,dh,dw = self._twgetnewsize(img4.height,img4.width,h4,w4)
                img4 = img4.resize((nw,nh))
                base.paste(img4.crop((dw, dh, dw+w4, dh+h4)),(w4+3,h4+3))
                self.p.image(img_source=base,high_density_horizontal=True,high_density_vertical=True,fragment_height=h_max_tm88iv)
            # 画像3枚
            elif img_count == 3:
                base = Image.new("L", (w,h), 0)
                img1 = Image.open(img_ary[0]).convert("L")
                nh,nw,dh,dw = self._twgetnewsize(img1.height,img1.width,h2,w2)
                img1 = img1.resize((nw,nh))
                base.paste(img1.crop((dw, dh, dw+w2, dh+h2)),(0,0))
                img2 = Image.open(img_ary[1]).convert("L")
                nh,nw,dh,dw = self._twgetnewsize(img2.height,img2.width,h3,w3)
                img2 = img2.resize((nw,nh))
                base.paste(img2.crop((dw, dh, dw+w3, dh+h3)),(w3+3,0))
                img3 = Image.open(img_ary[2]).convert("L")
                nh,nw,dh,dw = self._twgetnewsize(img3.height,img3.width,h4,w4)
                img3 = img3.resize((nw,nh))
                base.paste(img3.crop((dw, dh, dw+w4, dh+h4)),(w3+3,h3+3))
                self.p.image(img_source=base,high_density_horizontal=True,high_density_vertical=True,fragment_height=h_max_tm88iv)
            # 画像2枚
            elif img_count == 2:
                base = Image.new("L", (w,h), 255)
                img1 = Image.open(img_ary[0]).convert("L")
                nh,nw,dh,dw = self._twgetnewsize(img1.height,img1.width,h2,w2)
                img1 = img1.resize((nw,nh))
                base.paste(img1.crop((dw, dh, dw+w2, dh+h2)),(0,0))
                img2 = Image.open(img_ary[1]).convert("L")
                nh,nw,dh,dw = self._twgetnewsize(img2.height,img2.width,h2,w2)
                img2 = img2.resize((nw,nh))
                base.paste(img2.crop((dw, dh, dw+w2, dh+h2)),(w2+3,0))
                self.p.image(img_source=base,high_density_horizontal=True,high_density_vertical=True,fragment_height=h_max_tm88iv)
        else:
            for im in img_ary:
                img = Image.open(im).convert("L")
                if w < img.width:
                    nh = round(img.height * w / img.width)
                    img = img.resize((w,nh))
                    self.p.image(img_source=img,high_density_horizontal=True,high_density_vertical=True,fragment_height=h_max_tm88iv)
                elif h_max_tm88iv < img.height:
                    nw = round(img.width * h_max_tm88iv / img.height)
                    img = img.resize((h_max_tm88iv,nw))
                    self.p.image(img_source=img,high_density_horizontal=True,high_density_vertical=True,fragment_height=h_max_tm88iv)
                else:
                    self.p.image(img_source=img,high_density_horizontal=True,high_density_vertical=True,fragment_height=h_max_tm88iv)
    

    # フッター出力 ------------------------------------------------------------------
    def _twfooter(self, mention, retweet, favorite):
        """ フッター出力(メンション、リツイート、お気に入り)

        Parameters
        ----------
        mention : int
            メンション数
        retweet : int
            リツイート数
        favorite : int
            お気に入り数
        """
        self.p._raw(b'\x1B\x61\x02') # ESC a 2 右揃え
        #self.p.jptext2('💬 ' + self._twround(mention) + '🔃 ' + self._twround(retweet) + '🤍 ' + self._twround(favorite) + '\n') # メンション数面倒…
        self.p.jptext2('🔃 ' + self._twround(retweet) + '🤍 ' + self._twround(favorite) + '\n')
        self.p._raw(b'\x1B\x61\x00') # ESC a 0 左揃え


    # ヘッダー出力 ------------------------------------------------------------------
    def _twheader(self, icon_img, display_name, post_time, tw_type, type_text):
        """ ヘッダー出力

        Parameters
        ----------
        icon_img : str
            アイコンファイル名
        display_name : str
            表示名
        post_time : str
            投稿時間
        tw_type : int
            ツイートタイプ(0:通常、1:メンション,引用)
        type_text : str
            ツイートタイプの表示名
        """
        # ディスプレイ名の省略処理
        dplen = 0.0
        dplen_max = 15.5 - tw_type
        dpname = ""
        for c in display_name:
            if c.isascii():
                dplen += 0.5
            else:
                dplen += 1
            if dplen >= dplen_max:
                c = "…"
                dpname += c
                break
            dpname += c
        # アイコン画像処理
        icon = Image.open(icon_img).convert("RGBA")
        icon = icon.resize((100,100))
        mask = Image.new("1", (100,100), 1)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0,0, 100,100), fill=0)
        icon_tmp = Image.new("1", (100,100), 1)
        icon_out = Image.composite(icon_tmp,icon,mask)

        # --- ESC/POS ---
        self.p._raw(b'\x1B\x4C') # ESC L ページモード選択
        self.p._raw(b'\x1D\x50\x00\x00') # GS P
        self.p._raw(b'\x1B\x54\x00') # ESC 54 0
        """
        +----------------------------------+
        | (x,y)                            |
        |  +----------------------------+  |
        |  |                            |  |
        |  |                            |  |
        |  +----------------------------+  |
        |                          (dx,dy) |
        +----------------------------------+
        """
        #         ESC   W  xL  xH  yL  yH dxL dxH dyL dyH
        #                       x       y      dx      dy
        #                       0       0     512     400
        self.p._raw(b'\x1B\x57\x00\x00\x00\x00\x00\x02\xE0\x00') # ESC W ページモードにおける印字領域の設定
        #                  nL  nH
        self.p._raw(b'\x1D\x5C\xA0\x00') # GS \ ページモードにおける縦方向相対位置の指定

        if tw_type == 0:
            # icon_img
            self.p.image(img_source=icon_out,impl="graphics",high_density_horizontal=True,high_density_vertical=True)
            # -144
            self.p._raw(b'\x1D\x5C\x70\xFF') # GS \ ページモードにおける縦方向相対位置の指定
            # display_name
            self.p._raw(b'\x1B\x5C\x78\x00') # ESC \ 相対位置の指定
            self.p.jptext2(dpname + "\n")
            # time
            self.p._raw(b'\x1B\x5C\x78\x00') # ESC \ 相対位置の指定
            self.p.jptext2(post_time + "\n")
            # type_text
            self.p._raw(b'\x1B\x5C\x78\x00') # ESC \ 相対位置の指定
            self.p.jptext2(type_text + "\n")
        else:
            self.p._raw(b'\x1B\x5C\x18\x00') # ESC \ 相対位置の指定
            # icon_img
            self.p.image(img_source=icon_out,impl="graphics",high_density_horizontal=True,high_density_vertical=True)
            # -144
            self.p._raw(b'\x1D\x5C\x70\xFF') # GS \ ページモードにおける縦方向相対位置の指定
            # display_name
            self.p._raw(b'\x1B\x5C\x78\x00') # ESC \ 相対位置の指定
            self.p.jptext2(dpname + "\n")
            # post_time
            self.p._raw(b'\x1B\x5C\x90\x00') # ESC \ 相対位置の指定
            self.p.jptext2(post_time + "\n")
            # type_text
            self.p._raw(b'\x1B\x5C\x90\x00') # ESC \ 相対位置の指定
            self.p.jptext2(type_text + "\n")

        self.p._raw(b'\x1B\x0C') # ESC FF ページモードのデータ印字
        self.p._raw(b'\x1B\x53') # ESC S スタンダードモードの選択


    # パーシャルカット --------------------------------------------------------------
    def cut(self):
        """ パーシャルカット """
        self.p.open()
        self.p.cut()


    # 印字 --------------------------------------------------------------------------
    def print(self, maxid, twid, prt_retweet, prt_replay, prt_viewtype):
        """ 印字

        Parameter
        ---------
        maxid : int
            maxid
        twid : str
            twitter id
        prt_retweet : bool
            リツイートを含むか
        prt_replay : bool
            リプライを含むか
        prt_viewtype : int
            画像表示タイプ
        
        Return
        ------
        maxid : int
            maxid
        """
        self.p.open()
        # user_id と screen_name 判定
        if twid.isdecimal():
            rtn_maxid = self.t.gettweets(since_id=maxid,user_id=twid,include_rts=prt_retweet,include_reps=prt_replay)
        else:
            rtn_maxid = self.t.gettweets(since_id=maxid,screen_name=twid,include_rts=prt_retweet,include_reps=prt_replay)
 
        if len(self.t.order_tweets) < 1:
            self.p.close()
            return maxid

        self._twht_timestamp()
        self.p.jptext2("\n")

        # ツイート処理
        for k,v in reversed(list(self.t.order_tweets.items())):
            im = []
            if v.status_type == 0 or v.status_type != 0:
                icon_path = self.tmp.download(v.icon_url)
                if v.media_count > 0:
                    for m in v.media_urls:
                        media_path = self.tmp.download(m)
                        im.append(media_path)
                
                type = 0
                if v.status_type == 0:
                    type = 0
                    st = "通常:" + v.status_text
                if v.status_type == 1:
                    type = 0
                    st = "リツイート:" + v.status_text
                if v.status_type == 2:
                    type = 1
                    st = "引用:" + v.status_text
                if v.status_type == 3:
                    type = 0
                    st = "リプライ先:" + v.status_text
                if v.status_type == 5:
                    type = 0
                    st = v.status_text
                self._twht(type)

                self._twheader(icon_path, v.user_name, v.time_jst, type, st)
                if type > 0:
                    self.p._raw(b'\x1D\x4C\x18\x00') # GS L 左マージンの設定

                self.p.jptext2(v.full_text + "\n")
                self._twimage(im, type, prt_viewtype)
                self.p.jptext2("\n")

                if type > 0:
                    self.p._raw(b'\x1D\x4C\x00\x00') # GS L 左マージンの設定

                self._twfooter(0,v.retweet_count,v.favorite_count)

        return rtn_maxid


"""
    # 印字(TM印字なし) ----------------------------------------------------------------
    def _debugprint(self, maxid, twid, prt_retweet, prt_replay, prt_viewtype):
        if twid.isdecimal():
            self.t.gettweets(maxid, user_id=twid)
        else:
            self.t.gettweets(maxid, screen_name=twid)
        tweets = self.t.order_tweets
        for k,v in reversed(list(self.t.order_tweets.items())):
            print("----------------------------------------")
            print("id:" + str(k))
            print("name:" + v.user_name)
            print("status:" + str(v.status_type))
            print("status_text:" + v.status_text)
            print("full_text:" + v.full_text)
            print("----------------------------------------")
"""