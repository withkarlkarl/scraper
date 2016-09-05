import requests
import re, collections


def get_movies(url):
    response = requests.get(url)
    content = re.findall(r'"rate":"(?P<rate>[0-9.]+)".*?"title":"(?P<title>\w+)".*?"url":"(?P<url>.+?)"', response.text)
    rates = [movie[0] for movie in content]
    all_movies = dict(zip(rates, content))
    order = collections.OrderedDict(sorted(all_movies.items(), reverse=True))
    for i in order.values():
        print(i)

get_movies('https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=20&page_start=0')
