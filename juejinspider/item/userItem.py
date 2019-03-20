import scrapy


class UserItem(scrapy.Item):
    # id
    id = scrapy.Field()
    # 用户名
    username = scrapy.Field()

    # 注册时间
    registerTime = scrapy.Field()

    # 个人标签
    tag = scrapy.Field()

    # 简介
    brief = scrapy.Field()

    # 发布文章数量（专栏数量）
    publishedArticlesNum = scrapy.Field()

    # 沸点数量
    hotNum = scrapy.Field()

    # 分享文章数量
    shareNum = scrapy.Field()

    # 点赞过的文章数量
    initiatePraise = scrapy.Field()

    # 发布小册数量
    publishedBookNum = scrapy.Field()

    # 点赞总数
    praiseCountNum = scrapy.Field()

    # 文章总共被阅读次数（对应文章被阅读多少次）
    articleReadCountNum = scrapy.Field()

    # 关注了多少人(对应关注了)
    attentionPeopleNum = scrapy.Field()

    # 粉丝数（对应关注着）
    fans = scrapy.Field()

    # 收藏文章数（对应收藏集）
    collectArticleNum = scrapy.Field()

    # 关注标签数量（对应关注标签）
    attentionTagNum = scrapy.Field()
