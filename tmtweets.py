from dataclasses import dataclass
from typing import List
from enum import Enum
import datetime
import tweepy
import pprint
import collections

C_GET_COUNT = 30

@dataclass
class Tweet:
    """ Data Class """
    status_id: str          # ツイートID
    status_type: int        # ツイートタイプ(0:tweet, 1:retweet, 2:quotetweet, 3:reply, 4:mention, 5:other)
    status_text: str        # ツイートタイプ表示名
    source_id: str          # ソースID(リツイートや引用)
    user_id: str            # ユーザーID
    user_name: str          # ユーザー名(表示名)
    user_screen_name: str   # ユーザー名(アルファベット)
    time_jst: str           # 投稿時間(日本時間)
    icon_url: str           # アイコンURL
    favorite_count: str     # いいね数
    retweet_count: str      # リツイート数
    original_full_text: str # オリジナルツイート内容
    full_text: str          # 最終的なツイート内容
    media_count: int        # 画像件数
    media_urls: List[str]   # 画像URLリスト
    url_count: int          # URL件数
    urls: List[str]         # URLリスト
    video_info: bool        # 動画添付があるか
    mention_count: str      # メンション数
    debug_status: str       # 取得したStatusオブジェクト

class Type(Enum):
    """ Status Type """
    Normal     = 0 # tweet
    Retweet    = 1 # retweet
    Quotetweet = 2 # quotetweet
    Replay     = 3 # reply
    Mention    = 4 # mention
    Original   = 5 # other

class TMTweets:

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        """

        Parameters
        ----------
        consumer_key : str
            consumer_key
        consumer_secret : str
            consumer_secret
        access_token : str
            access_token
        access_token_secret : str
            access_token_secret
        """
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.order_tweets = collections.OrderedDict()


    def _isaddtweet(self, id, sid, check_sid=False):
        """ 引数に指定されたIDのツイートが既に追加されているか確認、追加されている場合は削除して追加
        
        Parameters
        ----------
        id : str
            チェックするID
        sid : str
            チェックするソースID
        check_sid : bool
            ソースIDをチェックするか

        Returns
        -------
        (id, sid, status_type) : tuple
            id : int
                ツイートID
            sid : int
                ソースID(リツイート元、引用元、リプライ元)
            status_type : int (default value -1)
                ツイートタイプ
        """
        if self.order_tweets.get(id) == None:
            if check_sid:
                for k, v in self.order_tweets.items():
                    if v.source_id == sid:
                        self.order_tweets.pop(k) # 削除
                        return (0, int(sid), v.status_type)
            return (0,0,-1)
        else:
            self.order_tweets.pop(id) # 削除
            return (int(id),0,-1)


    def _getmedia(self, full_text, xx_status):
        """ 拡張メディアリンクを取得し、ツイート内容に反映

        Parameters
        ----------
        full_text : str
            full_text
        xx_status : List[Status]
            retweeted_statusやquoted_status

        Returns
        -------
        (full_text, media_count, media_urls, video_info:) : tuple
            full_text : str
                ツイート内容
            media_count : int
                メディア件数
            media_urls: List[str]
                メディアurlリスト
            video_info : bool
                ビデオの有無
        """
        media_count = 0
        media_urls = []
        video_info = False
        for m in xx_status.extended_entities['media']:
            # URLを除去
            full_text = full_text.replace(m['url'], '')
            media_count += 1
            media_urls.append(m['media_url_https'])
            # 動画判定
            if hasattr(m, "video_info"):
                video_info = True
        return (full_text, media_count, media_urls, video_info)


    def _geturl(self, full_text, xx_status, exclude_url=''):
        """ 拡張リンクを取得し、ツイート内容に反映

        Parameters
        ----------
        full_text : str
            ツイート内容
        xx_status : List[Status]
            retweeted_statusやquoted_status
        exclude_url : str
            ツイート内容から除外するurlリンク(引用用)
        
        Returns
        -------
        (full_text, count, urls) : tuple
            full_text: str
                url含むツイート内容
            count : int
                url件数
            urls : List[str]
                urlリスト
        """
        count = 0
        urls = []
        for u in xx_status.entities['urls']:
            if exclude_url != u['expanded_url']:
                full_text = full_text.replace(u['url'],u['expanded_url'])
                count += 1
                urls.append(u['expanded_url'])
            else:
                full_text = full_text.replace(u['url'],'')
        return (full_text, count, urls)


    def _addtweet(self, xx, id_str, status_type, status_text, full_text, media_count, media_urls, url_count, urls, video_info, mention_count, status):
        """ ツイート追加 """
        time_jst = xx.created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y年%m月%d日 %H:%M JST")
        t = Tweet(
                id_str,                          # status_id
                status_type,                     # status_type
                status_text,                     # status_text
                xx.id_str,                       # source_id
                xx.user.id_str,                  # user_id
                xx.user.name,                    # user_name
                xx.user.screen_name,             # user_screen_name
                time_jst,                        # time_jst
                xx.user.profile_image_url_https, # icon_url
                xx.favorite_count,               # favorite_count
                xx.retweet_count,                # retweet_count
                xx.full_text,                    # original_full_text
                full_text,                       # full_text
                media_count,                     # media_count
                media_urls,                      # media_urls
                url_count,                       # url_count
                urls,                            # urls
                video_info,                      # video_info : bool
                mention_count,                   # mention_count
                status                           # debug_status
            )
        self.order_tweets[xx.id_str] = t


    def gettweets(self, since_id=1, user_id=0, screen_name='', include_rts=True, include_reps=True):
        """ ツイートを取得(取得ツイートはクラス変数の「order_tweets」に格納)

        Parameters
        ----------
        since_id : int
            指定ID以降を取得
        user_id : int
            ユーザーID
        screen_name : str
            スクリーン名
        include_rts : bool
            リツイートを含むか
        include_reps : bool
            リプライを含むか

        Returns
        -------
        max_id : int
            取得したツイートの最大ID
        """
        max_id = 0
        api = tweepy.API(self.auth)
        self.order_tweets = collections.OrderedDict()

        # exclude_replies true:除外、false:含める
        if include_rts:
            i_rts = True
        else:
            i_rts = False
        # include_rts true:含める、false:含めない
        if include_reps:
            i_reps = False
        else:
            i_reps = True


        if user_id != 0:
            if since_id > 1:
                public_user_tweets = api.user_timeline(user_id=user_id,count=C_GET_COUNT,since_id=since_id,tweet_mode='extended',exclude_replies=i_reps,include_rts=i_rts)
            else:
                public_user_tweets = api.user_timeline(user_id=user_id,count=C_GET_COUNT,tweet_mode='extended',exclude_replies=i_reps,include_rts=i_rts)
        elif screen_name != '':
            if since_id > 1:
                public_user_tweets = api.user_timeline(screen_name=screen_name,count=C_GET_COUNT,since_id=since_id,tweet_mode='extended',exclude_replies=i_reps,include_rts=i_rts)
            else:
                public_user_tweets = api.user_timeline(screen_name=screen_name,count=C_GET_COUNT,tweet_mode='extended',exclude_replies=i_reps,include_rts=i_rts)

        # ツイート解析
        for tweet in public_user_tweets:
            status = tweet
            if status.id > max_id:
                max_id = status.id

            # -----------------------------------------------------------------
            # リツイート
            if hasattr(status, "retweeted_status"):
                rt = status.retweeted_status
                # 引用
                if hasattr(rt, "quoted_status"):
                    qu = rt.quoted_status
                    status_text = rt.user.screen_name # 引用者
                    full_text = qu.full_text
                    media_count = 0
                    media_urls = []
                    url_count = 0
                    urls = []
                    video_info = False

                    # 引用元パーマリンク
                    quote_url = ''
                    if hasattr(rt, "quoted_status_permalink"):
                        quote_url = rt.quoted_status_permalink['expanded']
                    # リンク検索
                    if hasattr(qu, "entities"):
                        (full_text, url_count, urls) = self._geturl(full_text, qu, quote_url)
                    # 画像検索
                    if hasattr(qu, "extended_entities"):
                        (full_text, media_count, media_urls, video_info) = self._getmedia(full_text, qu)
                    # 追加(引用は追加チェックしない)
                    self._addtweet(qu, rt.quoted_status_id_str, Type.Quotetweet.value, status_text, full_text, media_count, media_urls, url_count, urls, video_info, 0, status)

                # リツイート
                status_text = status.user.screen_name
                full_text   = rt.full_text
                media_count = 0
                media_urls  = []
                url_count   = 0
                urls        = []
                video_info  = False

                (id, oid, type) = self._isaddtweet(rt.id_str,0,False)
                if id == 0:
                    # 引用元パーマリンクチェック
                    quote_url = ''
                    if hasattr(rt, "quoted_status_permalink"):
                        quote_url = rt.quoted_status_permalink['expanded']
                        if rt.quoted_status_id == None:
                            status_text += " (引用元なし)"
                    # リンク検索
                    if hasattr(rt, "entities"):
                        (full_text, url_count, urls) = self._geturl(full_text, rt, quote_url)
                    # 画像検索
                    if hasattr(rt, "extended_entities"):
                        (full_text, media_count, media_urls, video_info) = self._getmedia(full_text, rt)
                    # 追加
                    self._addtweet(rt, tweet.id_str, Type.Retweet.value, status_text, full_text, media_count, media_urls, url_count, urls, video_info, 0, status)

            # -----------------------------------------------------------------
            # リツイート以外
            else:
                st = status
                full_text = st.full_text
                # 引用
                if hasattr(st, "quoted_status"):
                    qu = st.quoted_status
                    status_text = st.user.screen_name # 引用者
                    full_text = qu.full_text
                    media_count = 0
                    media_urls = []
                    url_count = 0
                    urls = []
                    video_info = False

                    # 引用元パーマリンク
                    quote_url = ''
                    if hasattr(st, "quoted_status_permalink"):
                        quote_url = st.quoted_status_permalink['expanded']
                    # リンク検索
                    if hasattr(qu, "entities"):
                        (full_text, url_count, urls) = self._geturl(full_text, qu, quote_url)
                    # 画像検索
                    if hasattr(qu, "extended_entities"):
                        (full_text, media_count, media_urls, video_info) = self._getmedia(full_text, qu)
                    # 追加(引用は追加チェックしない)
                    self._addtweet(qu, tweet.id_str, Type.Quotetweet.value, status_text, full_text, media_count, media_urls, url_count, urls, video_info, 0, status)

                # 通常
                status_type = Type.Normal.value
                status_text = st.user.screen_name
                full_text = st.full_text
                media_count = 0
                media_urls = []
                url_count = 0
                urls = []
                video_info = False

                # リプライ判断
                if st.in_reply_to_status_id != None or st.in_reply_to_user_id != None:
                    status_type = Type.Replay.value
                    users = []
                    for u in st.entities['user_mentions']:
                        users.append(u['screen_name'])
                        full_text = full_text.replace('@' + u['screen_name'] + ' ','')
                    status_text = st.in_reply_to_screen_name
                    if len(users) > 1:
                        status_text += "＋他"
                    # 削除判定
                    if st.in_reply_to_status_id == None and st.in_reply_to_user_id != None:
                        status_text += " (リプライ元なし)"

                # 引用元パーマリンクチェック
                quote_url = ''
                if hasattr(st, "quoted_status_permalink"):
                    quote_url = st.quoted_status_permalink['expanded']
#                    status_type = Type.Quotetweet.value
                    if st.quoted_status_id == None:
                        status_text += " (引用元なし)"
                # リンク検索
                if hasattr(st, "entities"):
                    (full_text, url_count, urls) = self._geturl(full_text, st, quote_url)
                # 画像検索
                if hasattr(st, "extended_entities"):
                    (full_text, media_count, media_urls, video_info) = self._getmedia(full_text, st)
                # 追加
                (id, oid, type) = self._isaddtweet(tweet.id_str, 0, False)
                if id == 0:
                    self._addtweet(st, tweet.id_str, status_type, status_text, full_text, media_count, media_urls, url_count, urls, video_info, 0, status)

            # -----------------------------------------------------------------
            # リプライ先
            if status.in_reply_to_status_id != None:
                try:
                    re = api.get_status(status.in_reply_to_status_id,trim_user=False,tweet_mode="extended",include_ext_alt_text=True,include_card_uri=True)
                except tweepy.TweepyException:
                    continue

                # リプライ先引用
                if hasattr(re, "quoted_status"):
                    # 初期化
                    qu = re.quoted_status
                    status_text = re.user.screen_name # 引用者
                    full_text = qu.full_text
                    media_count = 0
                    media_urls = []
                    url_count = 0
                    urls = []
                    video_info = False

                    # 引用元パーマリンク
                    quote_url = ''
                    if hasattr(re, "quoted_status_permalink"):
                        quote_url = re.quoted_status_permalink['expanded']
                    # リンク検索
                    if hasattr(re, "entities"):
                        (full_text, url_count, urls) = self._geturl(full_text, re, quote_url)
                    # 画像検索
                    if hasattr(qu, "extended_entities"):
                        (full_text, media_count, media_urls, video_info) = self._getmedia(full_text, qu)
                    # 追加(引用は追加チェックしない)
                    self._addtweet(qu, tweet.id_str, Type.Quotetweet.value, status_text, full_text, media_count, media_urls, url_count, urls, video_info, 0, status)

                # リプライ先
                status_type = Type.Replay.value
                status_text = ''
                full_text = re.full_text
                media_count = 0
                media_urls = []
                url_count = 0
                urls = []
                video_info = False

                # リプライ先が自身の場合は追加しない
                if re.in_reply_to_status_id == None and (re.user.id_str == str(user_id) or re.user.screen_name == screen_name):
                    status_type = Type.Original.value
                    continue
                # 引用元パーマリンクチェック
                quote_url = ''
                if hasattr(re, "quoted_status_permalink"):
                    quote_url = re.quoted_status_permalink['expanded']
                    status_text += " (引用元なし)"
                # リンク検索
                if hasattr(re, "entities"):
                    (full_text, url_count, urls) = self._geturl(full_text, re, quote_url)
                # 画像検索
                if hasattr(re, "extended_entities"):
                    (full_text, media_count, media_urls, video_info) = self._getmedia(full_text, re)
                # ステータス名処理
                if re.in_reply_to_status_id != None:
                    # 複数メンション
                    users = []
                    for u in re.entities['user_mentions']:
                        users.append(u['screen_name'])
                        full_text = full_text.replace('@' + u['screen_name'] + ' ','')

                    status_text = re.in_reply_to_screen_name
                    if len(users) > 1:
                        status_text += "＋他"
                else:
                    status_type = Type.Original.value
                    status_text = "リプライ元:" + re.user.screen_name

                # 追加
                (id, oid, type) = self._isaddtweet(re.id_str, re.id_str, True)
                if id == 0:
                    self._addtweet(re, re.id_str, status_type, status_text, full_text, media_count, media_urls, url_count, urls, video_info, 0, re)
                if oid > 0:
                    if type == Type.Retweet.value:
                        self.order_tweets[re.id_str].status_type = Type.Original.value
                        self.order_tweets[re.id_str].status_text = "リツイート＋" + status_text
        return max_id


"""
    def test(self):
        max_id = 0
        sc_name = ''
        since_id = 1
        
        if since_id > 1:
            max_id = tw.gettweets(user_id=0,screen_name=sc_name,since_id=since_id,include_reps=True,include_rts=False)
        else:
            max_id = tw.gettweets(user_id=0,screen_name=sc_name,include_reps=True,include_rts=False)

        for v,t in tw.order_tweets.items():
            print("Tweet Type:"  + str(t.status_type))
            print("Source ID:"   + t.source_id)
            print("Status ID:"   + t.status_id)
            print("User ID:"     + t.user_id)
            print("User Name:"   + t.user_name)
            print("Screen Name:" + t.user_screen_name)
            print("Time:"        + t.time_jst)
            print("Status Text:" + t.status_text)
            print("Url Count:"   + str(t.url_count))
            print("Media Count:" + str(t.media_count))
            print("Video:"       + str(t.video_info))
            print("Full Text:"   + "\n" + t.full_text)
            print("------------------------------------------")
            pprint.pprint(t.debug_status._json)
            print("------------------------------------------")
        print("\nMax ID:" + str(max_id))

tw = TMTweets('', # consumer_key
              '', # consumer_secret
              '', # access_token
              '') # access_token_secret
tw.test()
"""