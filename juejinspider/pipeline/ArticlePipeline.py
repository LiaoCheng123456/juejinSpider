from elasticsearch import Elasticsearch

from juejinspider.item.articleItem import ArticleItem


class ArticlePipelines(object):
    def __init__(self):
        self.index = "article"
        self.type = "type"
        self.es = Elasticsearch(hosts="192.168.136.211:9200")

    def process_item(self, item, spider):
        if not isinstance(item, ArticleItem):
            return item

        result = self.checkDocumentExists(item)
        if result == False:
            self.createDocument(item)
        else:
            self.updateDocument(item)

    # 添加文档
    def createDocument(self, item):
        body = {
            "title"         : item['title'],
            "content"       : item['content'],
            "author"        : item['author'],
            "createTime"    : item['createTime'],
            "readNum"       : item['readNum'],
            "praise"        : item['praise'],
            "link"          : item['link'],
            "commentNum"    : item['commentNum'],
            'tags'          : item['tags']
        }
        try:
            self.es.create(index=self.index, doc_type=self.type, id=item["id"], body=body)
        except:
            pass

    # 更新文档
    def updateDocument(self, item):
        parm = {
            "doc" : {
                "readNum"   : item['readNum'],
                "praise"    : item['praise']
            }
        }

        try:
            self.es.update(index=self.index, doc_type=self.type, id=item["id"], body=parm)
        except:
            pass

    # 检查文档是否存在
    def checkDocumentExists(self, item):
        try:
            self.es.get(self.index, self.type, item["id"])
            return True
        except:
            return False
