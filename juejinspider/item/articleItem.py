import scrapy

class ArticleItem(scrapy.Item):
    # 文章id
    id = scrapy.Field()

    # 文章标题
    title = scrapy.Field()

    # 文章内容
    content = scrapy.Field()

    # 作者
    author = scrapy.Field()

    # 发布时间
    createTime = scrapy.Field()

    # 阅读量
    readNum = scrapy.Field()

    # 点赞数
    praise = scrapy.Field()

    # 头像
    photo = scrapy.Field()

    # 评论数
    commentNum = scrapy.Field()

    # 文章链接
    link = scrapy.Field()

    # 文章所属标签
    tags = scrapy.Field()