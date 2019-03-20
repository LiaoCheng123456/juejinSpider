import scrapy

class TagItem(scrapy.Item):
    # 文章id
    id = scrapy.Field()

    # 标题
    title = scrapy.Field()