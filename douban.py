import requests  #用于向网站发送请求
import logging
from bs4 import BeautifulSoup
import os
import util
import json
import re

# 豆瓣处理完成后默认添加的tag
DOU_BAN_TAG="RADARR"

# 豆瓣域名
DOUBAN_DOUMAN="https://movie.douban.com"

# 豆瓣 Cookie
DOUBAN_COOKIE=os.environ.get("BASE_DOUBAN_COOKIE")

logging.info(DOUBAN_COOKIE)

# 豆瓣请求头
DOU_BAN_REQUEST_HEADERS = {
    'User-Agent':util.DEFAULT_USER_AGENT,
    'Cookie': DOUBAN_COOKIE
}

# 登陆方法
def login():
    pass

# 请求我想看地址
def requestWishMoives(requesturl):
    if(requesturl is None):
        return None
        
    logging.info("开始请求豆瓣我想看地址:"+requesturl)
    response = requests.get(requesturl, headers=DOU_BAN_REQUEST_HEADERS, timeout=util.DEFAULT_REQUEST_TIME_OUT)

    soup=BeautifulSoup(response.text,'lxml')
    if(response.status_code==200):
        logging.info("请求豆瓣我想看页面成功！")
    else:
        util.logHtml("请求豆瓣我想看页面失败！",response.text)

    items = soup.select('.grid-view>.item')

    # 待处理的电影集合
    doubanMovies=[]
    # 循环解析
    for item in items:
        movie=parseWishMovieElement(item)
        if(movie is not None):
            doubanMovies.append(movie)


    nextUrl=findNextPageUrl(soup)
    if(nextUrl is not None):
        nextUrl=f"{DOUBAN_DOUMAN}{nextUrl}"
    return {
        "nextUrl":nextUrl,
        "movies":doubanMovies
    }
   

# 解析我想看电影
def parseWishMovieElement(element):
    # 当前电影对应的tag
    tagElement=element.select(".info>ul>li>.tags")
    tags=None
    if(tagElement and len(tagElement)>0):
        tags=tagElement.pop().text
        if(tags):
            tags = tags.replace("标签: ","")
        
    href=element.select(".pic>a").pop().get("href")
    title=element.select(".info>ul>.title>a>em").pop().text
    if(title.find("/")!=-1):
        title= title.split("/")[0]
    date=element.select(".info>ul>li>.date").pop().text
            
    doubanId=None
    foldcollect=None
    delElement=element.select(".info>ul>li>div>.d_link")

    if(delElement and len(delElement) >0):
        rel = delElement.pop().get("rel")
    if(rel):
        doubanId=rel[0].split(":")[0]
        foldcollect=rel[0].split(":")[1]
    return {
        'date':date,
        'detailHref':href,
        'title':title,
        'tags':tags,
        'doubanId':doubanId,
        'foldcollect':foldcollect
        }

# 获取下一页地址
def findNextPageUrl(page):
    nextElements=page.select(".paginator>.next>a")
    if(nextElements and len(nextElements)>0):
        nextElement = nextElements.pop()
        if(nextElement and nextElement.has_attr("href")):
            return nextElement.get("href")


# 获取豆瓣添加tag数据
def getDoubanTagPostData(self,postUrl):
    requests.get(postUrl,headers=self.DOU_BAN_REQUEST_HEADERS,timeout=util.DEFAULT_REQUEST_TIME_OUT)
    return


# 从豆瓣获取电影详情
def getMovieDetail(movie):
    title=movie["title"]
    href=movie["detailHref"]

    logging.info("开始从豆瓣抓取"+title+"详情")

    
    response = requests.get(href, headers=DOU_BAN_REQUEST_HEADERS, timeout=util.DEFAULT_REQUEST_TIME_OUT)
    html = response.text
    soup=BeautifulSoup(html,'lxml')
    imdbList = soup.select('#info')[0].find_all(text=re.compile("tt([0-9]{5,10})"))
    
    # 电影 imdbId
    if(len(imdbList)>0):
        movie["imdbId"]=imdbList.pop().strip()
    else:
        movie["imdbId"]=""

    # 电影年份
    years = soup.select("h1>.year")
    if(years and len(years)>0):
        movie["year"]=years.pop().getText().replace("(","").replace(")","")
    else:
        movie["year"]=""

    ck=soup.select("[name=ck]")
    if(ck is not None and len(ck)>0):
        movie["ck"]=ck.pop().get(key="value")

    logging.info("豆瓣电影结果："+json.dumps(movie))
    return movie

# 添加豆瓣tag
def addDoubanTag(movie,tag):
    if(tag is None or tag.strip() == ""):
        return

    postUrl=f'{DOUBAN_DOUMAN}/j/subject/{movie.get("doubanId")}/interest'
    tags=movie.get("tags")
    if(tags is None):
        tags=""
    tags=f"{tags} {tag}"

    postData={
        'ck': movie.get("ck"),
        'interest':"wish",
        'rating':"",
        'foldcollect':movie.get("foldcollect"),
        'tags':tags,
        'comment':''
    }

    logging.info("电影"+movie["title"]+"准备添加TAG")
    res= requests.post(postUrl,data=postData,headers=DOU_BAN_REQUEST_HEADERS,timeout=20)
    logging.info("电影"+movie["title"]+"准备添加TAG返回结果："+res.text)
    return

