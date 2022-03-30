import json
import os
import logging

# 日志输出设置
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# 脚本成功处理的tag
DOUBAN_PROCESS_SUCCESS_TAG="RADARR"
# 脚本处理失败的tag
DOUBAN_PROCESS_FAILURE_TAG="RADARR-FAILURE"


import douban
import radarr

# 处理豆瓣我想看
def processDoubanWishMovies(doubanWishUrl):
    doubanMovies=douban.requestWishMoives(doubanWishUrl)
    logging.info(f"找到待处理电影：{json.dumps(doubanMovies)}")

    if(doubanMovies is not None and doubanMovies["movies"] is not None):
        movies=doubanMovies["movies"]
        if(len(movies) > 0):
            for movie in movies:
                processResult=processDoubanWishMovie(movie)
                if(processResult is None or processResult==False):
                    logging.info("找到上一次处理电影处，脚本自动停止！")
                    return

    return doubanMovies["nextUrl"]

# 根据imdbId,选取正确的radarr电影
def chooseRadarrMovie(radarrMovies,imdbId):
    if(radarrMovies is None):
        return None
    if(imdbId is not None):
        for radarrMovie in radarrMovies:
            radarrMovieiImdbId=radarrMovie.get("imdbId")
            return radarrMovie

# 处理豆瓣电影
def processDoubanWishMovie(movie):
    movieTitle=movie["title"]
    logging.info(f"开始处理电影：{movieTitle}")

    tags=movie.get("tags")
    if(tags and (tags.find(f"{DOUBAN_PROCESS_SUCCESS_TAG} ")!=-1 or tags==DOUBAN_PROCESS_SUCCESS_TAG)):
        logging.info(f"电影{movieTitle}无需重复处理！")
        return False

    # 抓取豆瓣电影详情
    movieDetail=douban.getMovieDetail(movie=movie)
    # 当前电影对应的imdbId
    imdbId=movieDetail["imdbId"]

    # 根据当前电影名称，到radarr服务器找到相关电影
    radarrMovies = radarr.lookup(movieTitle)
    

    # 找到和豆瓣详情一样imdbId的电影详情
    radarrMovie=chooseRadarrMovie(radarrMovies=radarrMovies,imdbId=imdbId)
    if(radarrMovie is None):
        logging.info(f"没有在RADARR中找到电影： {movieTitle} 相关信息")
        douban.addDoubanTag(movie=movie,tag=DOUBAN_PROCESS_FAILURE_TAG)
        return True

    logging.info(f"找到电影：{movieTitle}，详细信息为：{json.dumps(radarrMovie)}")
    if(radarrMovie and radarrMovie.get("id") and radarrMovie["id"]>0):
        douban.addDoubanTag(movie=movie,tag=DOUBAN_PROCESS_SUCCESS_TAG)
        logging.info(f"电影{movieTitle}已存在，无需添加！")
    else:
        # 将当前电影添加到radarr服务器
        result=radarr.addMovieToRadarr(radarrMovie)
        if(result):
            logging.info(f"电影{movieTitle}添加成功！")
            douban.addDoubanTag(movie=movie,tag=DOUBAN_PROCESS_SUCCESS_TAG)
        else:
            logging.info(f"电影{movieTitle}添加失败！")
            douban.addDoubanTag(movie=movie,tag=DOUBAN_PROCESS_FAILURE_TAG)
    return True

# 开始执行脚本
logging.info("开始执行 Douban我想看 脚本。")
requestUrl = douban.DOUBAN_DOUMAN+"/mine?status=wish"

# 循环处理
while requestUrl is not None:
    nextPageUrl = processDoubanWishMovies(requestUrl)
    if(nextPageUrl is not None):
        logging.info("下一页URL："+nextPageUrl)
        requestUrl=nextPageUrl
    else:
        requestUrl=None

logging.info("脚本执行完成！")