from bs4 import BeautifulSoup
import requests, os, re, threading, time, random, itertools

session = requests.session()
cookies = 'SINAGLOBAL=6087263830616.329.1470624981105; un=withkarlkarl@sina.com; wvr=6; SCF=Au1BWirJ3i9F0xLXT53SY4g6oReD_QCzlmJu4Jf302ASvRPX8sSeyS0_3PFngDCl9SR9rKwYjbnmvqXbMr5wXPY.; SUB=_2A256wljuDeTxGedN6lEX8SnEyTmIHXVZts0mrDV8PUNbmtBeLVTVkW8AmZnaXzwETcpZBOv-Uv75uWQ1JA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFPiQSYxV3HvSaJCBTePcSf5JpX5KMhUgL.Fo20eKeceKMReo-2dJLoIpShi--ci-2Ei-2ci--fiK.7iKLF; SUHB=0wnEqtB8A5UD4C; ALF=1504140348; SSOLoginState=1472604350; _s_tentry=login.sina.com.cn; UOR=www.jianshu.com,service.weibo.com,login.sina.com.cn; Apache=5788149204163.788.1472604254398; ULV=1472604254421:38:38:3:5788149204163.788.1472604254398:1472524429783; USRANIME=usrmdinst_5; WBStore=0e9767219e7dbe35|undefined'
# 把cookies变成字典
cookies = dict((l.split('=') for l in cookies.split('; ')))
# 相册地址，这个地址是在XHR里面找的
album_url = [
    r'http://photo.weibo.com/photos/get_all?uid=2604615115&album_id=3562694494772340&count=30&page={}&type=3&__rnd=1472540314106'.format(
        str(i)) for i in range(1, 15)]
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}

# 保存路径
SAVE_PATH = "image" + 'Eric1' + "/"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)
proxies = [{'http': '120.27.24.27:8088'}, {'http': '60.212.196.88:8118'}, {'http': '171.37.134.245:8123'}]


# 获取图片id，最后图片的地址是用id拼凑的
def get_photo_id(url):
    try:
        response = session.get(url, headers=headers, cookies=cookies).text
        photo_ids = re.findall(r'"photo_id":"(\d*?)"', response)
        print(photo_ids)
        with open(r'./photo_add.txt', 'a+') as txt:
            for i in photo_ids:
                txt.write(i + '\n')
            txt.close()

    except UnicodeDecodeError as e:
        print('-----UnicodeDecodeError url:', url)

    except socket.timeout as e:
        print("-----socket timout:", url)

# 获取图片链接
def get_photo_url(ids):
    time.sleep(2)
    id_url = 'http://photo.weibo.com/2604615115/wbphotos/large/photo_id/{}/album_id/3562694494772340'.format(
        str(ids))
    web_data = session.get(id_url, headers=headers, cookies=cookies).text
    # 有时候爬不到"id=pic"怀疑是get没有获取到网页
    soup = BeautifulSoup(web_data, 'lxml')
    sina_image_url = soup.select('#pic')
    if len(sina_image_url) >= 1:
        sina_image_url = sina_image_url[0].get('src')
        print(sina_image_url)
        with open(r'./photo_urls400.txt', 'a+') as txt:
            txt.write(sina_image_url + '\n')
            txt.close()
    else:
        with open(r'./left3.txt', 'a+') as txt:
            txt.write(ids + '\n')
            txt.close()

# 保存图片
def save_image(line):
    time.sleep(20)
    try:
        response = session.get(line, stream=True)
        image = response.content
        print(line)
        with open(SAVE_PATH + line.split('/')[-1] + '.jpg', "wb") as image_object:
            image_object.write(image)
            return
    except Exception as e:
        print(e)
        with open(r'./left1.txt', 'a+') as txt:
            txt.write(line + '\n')
            txt.close()
        return

# 收集图片id
# for url in album_url:
#     print(url)
#     get_photo_id(url)

# 多线程获取图片链接
# threads = []
# txt = open(r'./left2.txt', 'a+')
# txt.seek(0)
# for i in itertools.islice(txt, None):
#     threads.append(threading.Thread(target=get_photo_url, args=(i.strip(),)))
# for t in threads:
#     t.start()
# txt.close()

# 多线程下载图片
threads = []
with open(r'./photo_urls100.txt', 'r') as txt:
    for line in txt:
        # print(line.strip())
        threads.append(threading.Thread(target=save_image, args=(line.strip(),)))
    for t in threads:
        t.start()

