from cmath import log
import json
from pydoc import html
import re
from urllib import request
import requests  #用于向网站发送请求
from bs4 import BeautifulSoup
import os
import logging

# 豆瓣tag，如果脚本成功处理了当前tag，那么当前脚本会将此TAG添加到当前电影上
DOU_BAN_TAG="RADARR"

def logHtml(msg,html):
    try:
        html=html.strip().replace(" ","").replace('\n','').replace('\t','').replace('\r','') 
    except:
        html=html
    logging.info(msg+":"+html)
    return


def init():
    os.environ.setdefault("BASE_RADARR_URL","http://mf.frp.renjilin.top")
    os.environ.setdefault("BASE_RADARR_API_KEY","fcbc9a39e08940808dab2dcd52c2c4a3")
    os.environ.setdefault("BASE_DOUBAN_COOKIE","douban-fav-remind=1; bid=_x_1Ziqaz0I; ll=\"118163\"; ap_v=0,6.0; __utmz=30149280.1646626056.3.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmz=223695111.1646626056.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _vwo_uuid_v2=DC613AB0118D08B1A9809B07CF8F38F65|83254670f47ca1a4eb6422ff2fdc91e1; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1646627907%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3Dx-8axkKgpTGe75k3kFppK715fF9S1DxePL2lWJPAVMRa_n1D3YPVN241DnHYKAUv%26wd%3D%26eqid%3Da7cf497500029b3c0000000462258500%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.1194066918.1609336352.1646626056.1646627907.4; __utmc=30149280; __utma=223695111.814176257.1646626056.1646626056.1646627907.2; __utmb=223695111.0.10.1646627907; __utmc=223695111; dbcl2=\"253935038:S3V6Ha2xGYI\"; ck=Mv-r; push_noty_num=0; push_doumail_num=0; __utmt=1; __utmv=30149280.25393; __utmb=30149280.2.10.1646627907; _pk_id.100001.4cf6=51b6a2048d95de82.1646626056.2.1646628035.1646626070.")

init()

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

douban_url = 'https://movie.douban.com/mine?status=wish'
douban_cookie=os.environ.get("BASE_DOUBAN_COOKIE")
douban_headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
    'Cookie': douban_cookie
}


# 从豆瓣获取电影详情
def getMovieImdbFromDouban(title,href):
    logging.info("开始从豆瓣抓取"+title+"详情")
    movieInfo={}
    response = requests.get(href, headers=douban_headers, timeout=20)
    html = response.text
    soup=BeautifulSoup(html,'lxml')
    logHtml("豆瓣抓取电影"+title+"页面结果",html)
    imdbList = soup.select('#info')[0].find_all(text=re.compile("tt([0-9]{5,10})"))
    
    if(len(imdbList)>0):
        movieInfo["imdbId"]=imdbList.pop().strip()
    else:
        movieInfo["imdbId"]=""

    years = soup.select("h1>.year")
    if(years and len(years)>0):
        movieInfo["year"]=years.pop().getText().replace("(","").replace(")","")
    else:
        movieInfo["year"]=""
    
    logging.info("豆瓣电影结果："+json.dumps(movieInfo))
    return movieInfo

        
# 选择电影
def selectMovie(movies,href):
    if(movies and len(movies)==1):
        return movies.pop()
    for movie in movies:
        title=movie["title"]
        doubanInfo= getMovieImdbFromDouban(title,href)
        if(movie.get("imdbId")):
            imdbId=movie.get("imdbId")
            doubanImdbId=doubanInfo.get("imdbId")
            if(doubanImdbId == imdbId):
                return movie
    return None

# 查找电影详情
def lookup(title,href):
    url=os.environ.get("BASE_RADARR_URL")
    apiKey=os.environ.get("BASE_RADARR_API_KEY")

    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
    }

    logging.info("开始查询"+title+"详细信息")

    url=url+"/api/v3/movie/lookup?apiKey="+apiKey+"&term="+title
    logging.info("Radarr请求地址："+url)
    response = requests.get(url, headers=headers, timeout=20)
    content = response.content
    logHtml("Radder服务器返回结果",response.text)

    sameNameMovies=[]
    jsonObjects = json.loads(content)

    if(len(jsonObjects)==0):
        logging.warning("未找到电影"+title+"相关信息")

    for jsonObj in jsonObjects:
        if(jsonObj["title"]==title):
            # 将相同名称的电影添加到集中去
            sameNameMovies.append(jsonObj)
    return selectMovie(sameNameMovies,href)


# 添加豆瓣tag
def addDoubanTag(doubanMovie):
    logging.info(json.dumps(doubanMovie))

    postUrl="https://movie.douban.com/j/subject/"+doubanMovie.get("doubanId")+"/interest"
    tags=doubanMovie.get("tags")
    if(tags is None):
        tags=""
    tags=tags + " "+DOU_BAN_TAG

    postData={
        'ck':"Mv-r",
        'interest':"wish",
        'rating':"",
        'foldcollect':doubanMovie.get("foldcollect"),
        'tags':tags,
        'comment':''
    }

    logging.info("电影"+doubanMovie["title"]+"准备添加TAG")
    res= requests.post(postUrl,data=postData,headers=douban_headers,timeout=20)
    logging.info("电影"+doubanMovie["title"]+"准备添加TAG返回结果："+res.text)
    return


def addMovieToRadarr(movie):
    moviePath = os.environ.get("BASE_RADARR_PATH")
    if(moviePath is None):
        # 请求电影保存地址
        url= os.environ.get("BASE_RADARR_URL")+"/api/v3/rootfolder?apiKey="+os.environ.get("BASE_RADARR_API_KEY")
        resp = requests.get(url,timeout=20)
        if(resp.status_code==200):
            respData=resp.text
            respObjects = json.loads(respData)
            if(respObjects and len(respObjects)>0):
                respObject=respObjects[0]
                if(respObject is not None):
                    moviePath=respObject.get("path")
                    os.environ.setdefault("BASE_RADARR_PATH",moviePath)
                    logging.info("获取电影保存路径成功！保存路径为："+moviePath)
    # 一些默认值赋值
    movie["id"]=0
    movie["status"]="inCinemas"
    movie["qualityProfileId"]=1
    movie["monitored"]=True
    movie["minimumAvailability"]='announced'
    movie["addOptions"]={"searchForMovie":True}
    movie["rootFolderPath"]=moviePath

    postUrl= os.environ.get("BASE_RADARR_URL")+"/api/v3/movie?apiKey="+os.environ.get("BASE_RADARR_API_KEY")
    postHeaders = {'Content-Type': 'application/json'} ## headers中添加上content-type这个参数，指定为json格式

    postResp = requests.post(url=postUrl,headers=postHeaders,data=json.dumps(movie),timeout=20)
    logging.info(postResp.status_code)
    postRespBody=postResp.text
    postRespObj= json.loads(postRespBody)
    if(postRespObj and postRespObj.get("id") and postRespObj.get("id") > 0):
        logging.info("电影添加成功")
        return True
    return False

# 解析豆瓣ß
def processDouban(url):
    logging.info("开始请求豆瓣我想看地址:"+url)
    response = requests.get(url, headers=douban_headers, timeout=20)
    soup=BeautifulSoup(response.text,'lxml')
    if(response.status_code==200):
        logging.info("获取豆瓣页面成功！")
    else:
        logHtml("请求豆瓣页面失败！",response.text)

    items = soup.select('.grid-view>.item')
    # 循环解析
    for item in items:
        href=item.select(".pic>a").pop().get("href")
        title=item.select(".info>ul>.title>a>em").pop().text
        if(title.find("/")!=-1):
            title= title.split("/")[0]
        date=item.select(".info>ul>li>.date").pop().text
        tagElement=item.select(".info>ul>li>.tags")
        tags=None
        if(tagElement and len(tagElement)>0):
            tags=tagElement.pop().text
        doubanId=None
        foldcollect=None
        delElement=item.select(".info>ul>li>div>.d_link")
        if(delElement and len(delElement) >0):
            rel = delElement.pop().get("rel")
        if(rel):
            doubanId=rel[0].split(":")[0]
            foldcollect=rel[0].split(":")[1]

        doubanMovie={
            'date':date,
            'href':href,
            'title':title,
            'tags':tags,
            'doubanId':doubanId,
            'foldcollect':foldcollect
        }

        # 如果找到上一次添加的标记
        # 结束此次循环
        if(tags and tags.find(DOU_BAN_TAG)!=-1):
            logging.info("发现已标记的电影，脚本结束！")
            return None

        logging.info("开始处理电影："+title)

        moiveInfo=lookup(title.strip(),href)
        if(moiveInfo != None):
            if(moiveInfo.get("id") and moiveInfo["id"]>0):
                addDoubanTag(doubanMovie)
                logging.info("电影"+title+"已存在，无需添加！")
            else:
                result = addMovieToRadarr(moiveInfo)
                if(result):
                    logging.info("电影"+title+"添加成功！")
                    addDoubanTag(doubanMovie)

    nextElements=soup.select(".paginator>.next>a")
    
    if(nextElements and len(nextElements)>0):
        nextElement = nextElements.pop()
        if(nextElement and nextElement.has_attr("href")):
            return nextElement.get("href")

    return None

logging.info("开始执行 radarr-douban 脚本。")

while douban_url is not None:
    next_url=processDouban(douban_url)
    if(next_url):
        logging.info("下一页URL："+next_url)
        douban_url="https://movie.douban.com"+next_url
    else:
        douban_url=None


logging.info("脚本执行完成！")