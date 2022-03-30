# 豆瓣我想看脚本



## 1. 介绍

此脚本只是自动爬取豆瓣我想看的电影，然后添加到Radarr服务器。

至于Radarr如何查找种子，如何下载电影，如何联动`jellyfin` `emby` `plex`等媒体服务器，可自行百度



## 2. 使用方法



#### 青龙

1. 添加定时任务：

   * BASE_RADARR_URL：RADARR服务器地址
   * BASE_RADARR_API_KEY：RADARR API KEY,可以在设置 -> 通用中找到
   * BASE_DOUBAN_COOKIE：豆瓣的登陆Cookie

2. 添加依赖管理

   ![image-20220330095937524](https://img.renjilin.top/i/2022/03/30/6243b989cd05f.png)

 3. 添加脚本任务

    ![image-20220330100012163](https://img.renjilin.top/i/2022/03/30/6243b9ac6e506.png)



#### 定时任务

大体思路同上，此处省略一万字...
