import urllib.request
import zipfile

# Noto_Sans_JP
print("Noto_Sans_JPをダウンロード")
url = "https://fonts.google.com/download?family=Noto%20Sans%20JP"
urllib.request.urlretrieve(url, "Noto_Sans_JP.zip")

print("Noto_Sans_JP.zipからNotoSansJP-Medium.otfを抽出")
zp = zipfile.ZipFile("Noto_Sans_JP.zip", "r")
zp.extract(member="NotoSansJP-Medium.otf")

# unifont_jp
print("unifont_jp-14.0.03.ttfをダウンロード")
url = "https://unifoundry.com/pub/unifont/unifont-14.0.03/font-builds/unifont_jp-14.0.03.ttf"
urllib.request.urlretrieve(url, "unifont_jp-14.0.03.ttf")

# JIS0201.TXT
print("JIS0201.TXTをダウンロード")
url = "http://unicode.org/Public/MAPPINGS/OBSOLETE/EASTASIA/JIS/JIS0201.TXT"
urllib.request.urlretrieve(url, "JIS0201.TXT")

# JIS0208.TXT
print("JIS0208.TXTをダウンロード")
url = "http://unicode.org/Public/MAPPINGS/OBSOLETE/EASTASIA/JIS/JIS0208.TXT"
urllib.request.urlretrieve(url, "JIS0208.TXT")

# JIS0212.TXT
print("JIS0212.TXTをダウンロード")
url = "http://unicode.org/Public/MAPPINGS/OBSOLETE/EASTASIA/JIS/JIS0212.TXT"
urllib.request.urlretrieve(url, "JIS0212.TXT")
