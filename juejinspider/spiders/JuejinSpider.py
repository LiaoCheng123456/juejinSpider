# -*- coding: utf-8 -*-
import json
import logging
import random
import re
import time

import scrapy
import tomd
from juejinspider.item.articleItem import ArticleItem
from juejinspider.item.tagItem import TagItem
from juejinspider.item.userItem import UserItem
from juejinspider.tools.ConnectionPool import redisConnectionPool


class JuejinspiderSpider(scrapy.Spider):
    name = 'JuejinSpider'
    redisConnection = redisConnectionPool()
    redis = redisConnection.getClient()
    user_agent_list = [ \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safri/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    allowed_domains = ["juejin.im"]
    ua = random.choice(user_agent_list)
    postPages = 1
    url = "https://timeline-merger-ms.juejin.im/v1/get_tag_entry?src=web&tagId={}&page={}&pageSize=10&sort=rankIndex"
    headers = {
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://gupiao.baidu.com/',
        'User-Agent': ua,
        "X-Juejin-Src": "web"
    }
    pages = 1
    # 先读取所有标，存入redis
    def start_requests(self):
        urls = ['https://gold-tag-ms.juejin.im/v1/tags/type/hot/page/%s/pageSize/40' % (self.pages)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)

    def parse(self, response):
        print(response.url)
        logging.info(response.url)
        if "gold-tag-ms.juejin.im/v1/tags/type/hot/page/" in response.url:
            yield scrapy.Request(url=response.url, callback=self.insertToRedis, headers=self.headers, dont_filter=True)

        if "timeline-merger-ms.juejin.im/v1/get_tag_entry" in response.url:
            yield scrapy.Request(url=response.url, callback=self.articleListHandle, headers=self.headers, dont_filter=True)

        if "juejin.im/post" in response.url:
            yield scrapy.Request(url=response.url, callback=self.articleHandle, headers=self.headers, dont_filter=True)

        if "/user/" in response.url and len(str(response.url).split("/")) == 5:
            yield scrapy.Request(url=response.url, callback=self.userHandle, headers=self.headers, dont_filter=True)

    # 数据存入redis, 检查旧的标签连接里面是否有这个链接，如果没有就放入队列里面,并且将新的链接存入到oldTagList
    def insertToRedis(self, response):
        logging.info("insertToRedis，存入标签数据到redis")
        # 标签数据已经读取完,重新装入标签
        body = json.loads(response.body)
        if body:
            for value in body['d']['tags']:
                # 将标签内容存入redis
                tagItem = TagItem()
                tagItem['id'] = value['id']
                tagItem['title'] = value['title']
                obj = tagItem.__dict__
                self.sadd("tagList",obj)
        self.pages += 1
        url = 'https://gold-tag-ms.juejin.im/v1/tags/type/hot/page/%s/pageSize/40' % (self.pages)
        if len(body['d']['tags']) > 0:
            yield scrapy.Request(url=url,callback=self.insertToRedis, headers=self.headers, dont_filter=True)
        else:
            tagId = self.getSpopValue()
            url = self.url.format(tagId, 1)
            yield scrapy.Request(url=url,callback=self.parse, headers=self.headers, dont_filter=True)

    #redis|set集合
    def sadd(self,key, value):
        try:
            return self.redis.sadd(key, value.__str__()) > 0
        except:
            logging.error("redis连接失败,尝试重新连接,post={},port={}".format("192.168.136.21", "6379, 重试中..."))
            time.sleep(1)
            self.sadd(key,value)

    # 获取redis队列数据
    def getSpopValue(self):
        try:
            result = eval(str(self.redis.spop("tagList"),encoding = "utf-8"))
            if result['_values']['id']:
                return result['_values']['id']
            else:
                return None
        except:
            logging.error("redis连接失败,尝试重新连接,post={},port={}".format("192.168.136.21", "6379, 重试中..."))
            time.sleep(1)
            self.getSpopValue()

    # 处理文章列表链接
    def articleListHandle(self, response):
        # 文章id
        tagId = re.findall(r"&tagId=(.+?)&", response.url)[0]

        # 文章页码
        pages = int(re.findall(r"&page=(.+?)&", response.url)[0])

        # 文章内容
        body = json.loads(response.body)
        if len(body['d']['entrylist']) > 0:
            for value in body['d']['entrylist']:
                if "juejin.im/post" in value['originalUrl']:
                    # 将文章的地址放入队列
                    yield scrapy.Request(url=value['originalUrl'], callback=self.parse, headers=self.headers,dont_filter=True)

            # 加载数据,将下一页的数据放入队列
            pages += 1
            url = self.url.format(tagId, pages)
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)
        else:
            tagId = self.getSpopValue()
            url = self.url.format(tagId, 1)
            logging.info("队列数据处理已完成，下次请求url为{}".format(url))
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True)

    # 处理文章
    def articleHandle(self, response):
        article = ArticleItem()

        # 文章id作为id
        article['id'] = str(response.url).split("/")[-1]

        # 标题
        article['title'] = response.css(
            "#juejin > div.view-container > main > div > div.main-area.article-area.shadow > article > h1::text").extract_first()

        # 内容
        parameter = response.css(
            "#juejin > div.view-container > main > div > div.main-area.article-area.shadow > article > div.article-content").extract_first()
        article['content'] = self.parseToMarkdown(parameter)

        # 作者
        article['author'] = response.css(
            "#juejin > div.view-container > main > div > div.main-area.article-area.shadow > article > div:nth-child(6) > meta:nth-child(1)::attr(content)").extract_first()

        # 创建时间
        createTime = response.css(
            "#juejin > div.view-container > main > div > div.main-area.article-area.shadow > article > div.author-info-block > div > div > time::text").extract_first()
        createTime = str(createTime).replace("年", "-").replace("月", "-").replace("日", "")
        article['createTime'] = createTime

        # 阅读量
        article['readNum'] = int(str(response.css(
            "#juejin > div.view-container > main > div > div.main-area.article-area.shadow > article > div.author-info-block > div > div > span::text").extract_first()).split(
            " ")[1])
        if article['readNum'] == None:
            article['readNum'] = 0

        # 点赞数
        badge = response.css(
            "#juejin > div.view-container > main > div > div.article-suspended-panel.article-suspended-panel > div.like-btn.panel-btn.like-adjust.with-badge::attr(badge)").extract_first()
        if badge == None:
            article['praise'] = 0
        else:
            article['praise'] = badge

        # 评论数
        article['commentNum'] = response.css(
            "#juejin > div.view-container > main > div > div.article-suspended-panel.article-suspended-panel > div.comment-btn.panel-btn.comment-adjust.with-badge::attr(badge)").extract_first()
        if article['commentNum'] == None:
            article['commentNum'] = 0

        # 文章链接
        article['link'] = response.url

        yield article

        # 将作者链接存入队列
        yield scrapy.Request(url=response.css(
            "#juejin > div.view-container > main > div > div.main-area.article-area.shadow > article > div:nth-child(6) > meta:nth-child(2)::attr(content)").extract_first(),
                             callback=self.parse, headers=self.headers, dont_filter=True)

    # 处理用户
    def userHandle(self, response):
        length = str(response.url).split("/")

        userItem = UserItem()

        # 用户id
        userItem['id'] = length[4]

        # 用户名
        userItem['username'] = self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.major-area > div.user-info-block.block.shadow > div.info-box.info-box > div.top > h1::text").extract_first())

        # 注册时间
        userItem['registerTime'] = self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.minor-area > div > div.more-block.block > div > div.item-count > time::text").extract_first())
        userItem['registerTime'] = str(userItem['registerTime']).replace("年", "-").replace("月", "-").replace("日", "")

        # 标签
        userItem['tag'] = self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.major-area > div.user-info-block.block.shadow > div.info-box.info-box > div.position > span > span::text").extract())

        # 简介
        userItem['brief'] = self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.major-area > div.user-info-block.block.shadow > div.info-box.info-box > div.intro > span::text").extract_first())

        # 发布文章数量
        userItem['publishedArticlesNum'] = self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.major-area > div.list-block > div > div.list-header > div > a:nth-child(3) > div.item-count::text").extract_first())

        # 沸点文章数量
        userItem['hotNum'] = self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.major-area > div.list-block > div > div.list-header > div > a:nth-child(4) > div.item-count::text").extract_first())

        # 分享文章数量
        userItem['shareNum'] = self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.major-area > div.list-block > div > div.list-header > div > a:nth-child(5) > div.item-count::text").extract_first())

        # 对别人的文章点赞数量
        userItem["initiatePraise"] = self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.major-area > div.list-block > div > div.list-header > div > div:nth-child(6) > div:nth-child(2)::text").extract_first())

        # 发布小册数量
        userItem['publishedBookNum'] = self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.major-area > div.list-block > div > div.list-header > div > a:nth-child(8) > div.item-count::text").extract_first())

        # 共获赞数量
        userItem['praiseCountNum'] = str(self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.minor-area > div > div.stat-block.block.shadow > div.block-body > div:nth-child(2) > span > span::text").extract_first())).replace(
            ",", "")

        # 所有文章共被阅读次数
        userItem['articleReadCountNum'] = str(self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.minor-area > div > div.stat-block.block.shadow > div.block-body > div:nth-child(3) > span > span::text").extract_first())).replace(
            ",", "")

        # 一共关注了多少人
        userItem['attentionPeopleNum'] = str(self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.minor-area > div > div.follow-block.block.shadow > a:nth-child(1) > div.item-count::text").extract_first())).replace(
            ",", "")

        # 有多少人关注了这个用户（粉丝）
        userItem['fans'] = str(self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.minor-area > div > div.follow-block.block.shadow > a:nth-child(2) > div.item-count::text").extract_first())).replace(
            ",", "")

        # 收藏的文章数量
        userItem['collectArticleNum'] = str(self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.minor-area > div > div.more-block.block > a:nth-child(1) > div.item-count::text").extract_first())).replace(
            ",", "")

        # 关注的标签数量
        userItem['attentionTagNum'] = str(self.parseInt(response.css(
            "#juejin > div.view-container > main > div.view.user-view > div.minor-area > div > div.more-block.block > a:nth-child(2) > div.item-count::text").extract_first())).replace(
            ",", "")

        yield userItem

    # 将字符串转换成int
    def parseInt(self, param):
        if param == None:
            return 0
        else:
            return param

    # 将数据转换成markdown
    def parseToMarkdown(self, param):
        return tomd.Tomd(str(param)).markdown
