import os
import logging
import requests 
import json
import util

DEFAULT_USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
DEFAULT_REQUEST_TIME_OUT=20

BASE_URL=os.environ.get("BASE_RADARR_URL")
API_KEY=os.environ.get("BASE_RADARR_API_KEY")

HEADERS={
    'User-Agent':DEFAULT_USER_AGENT
}

# 根据电影名称，从radarr服务器中找到相同名称的电影
def lookup(title):
    logging.info("开始从RADARR服务器查询"+title+"详细信息")

    url=BASE_URL+"/api/v3/movie/lookup?apiKey="+API_KEY+"&term="+title
    logging.info("RADARR 请求地址："+url)
    response = requests.get(url, headers=HEADERS, timeout=DEFAULT_REQUEST_TIME_OUT)
    content = response.content
    util.logHtml("Radder服务器返回结果",response.text)

    jsonObjects = json.loads(content)
    return jsonObjects

# 获取电影保存地址
def getMovieSavePath():
    # 电影保存地址
    movieSavePath = os.environ.get("BASE_RADARR_PATH")
    if(movieSavePath is None):
        # 请求电影保存地址
        url= BASE_URL+"/api/v3/rootfolder?apiKey="+API_KEY
        resp = requests.get(url,headers=HEADERS,timeout=20)
        if(resp.status_code==200):
            respData=resp.text
            respObjects = json.loads(respData)
            if(respObjects and len(respObjects)>0):
                respObject=respObjects[0]
                if(respObject is not None):
                    moviePath=respObject.get("path")
                    os.environ.setdefault("BASE_RADARR_PATH",moviePath)
                    logging.info("获取电影保存路径成功！保存路径为："+moviePath)
    return moviePath

# 添加电影
def addMovieToRadarr(movie):
    movieSavePath=getMovieSavePath()

    # 一些默认值赋值
    movie["id"]=0
    movie["status"]="inCinemas"
    movie["qualityProfileId"]=1
    movie["monitored"]=True
    movie["minimumAvailability"]='announced'
    movie["addOptions"]={"searchForMovie":True}
    movie["rootFolderPath"]=movieSavePath

    postUrl= f"{BASE_URL}/api/v3/movie?apiKey={API_KEY}"
    postHeaders = {'Content-Type': 'application/json'} ## headers中添加上content-type这个参数，指定为json格式

    postResp = requests.post(url=postUrl,headers=postHeaders,data=json.dumps(movie),timeout=20)
    postRespBody=postResp.text
    postRespObj= json.loads(postRespBody)
    if(postRespObj and postRespObj.get("id") and postRespObj.get("id") > 0):
        logging.info("电影添加成功")
        return True
    return False


