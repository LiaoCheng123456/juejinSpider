from elasticsearch import Elasticsearch

from juejinspider.item.userItem import UserItem


class UserPipeline(object):
    def __init__(self):
        self.index = "user"
        self.type = "type"
        self.es = Elasticsearch(hosts="192.168.136.211:9200")

    def process_item(self, item, spider):
        if not isinstance(item, UserItem):
            return item

        result = self.checkDocumentExists(item)
        if result == False:
            self.createDocument(item)
        else:
            self.updateDocument(item)

    # 添加文档
    def createDocument(self, item):
        body = {
            "username"              : item['username'],
            "registerTime"          : item['registerTime'],
            "tag"                   : item['tag'],
            "brief"                 : item['brief'],
            "publishedArticlesNum"  : item['publishedArticlesNum'],
            "hotNum"                : item['hotNum'],
            "shareNum"              : item['shareNum'],
            "initiatePraise"        : item['initiatePraise'],
            "publishedBookNum"      : item['publishedBookNum'],
            "praiseCountNum"        : item['praiseCountNum'],
            "articleReadCountNum"   : item['articleReadCountNum'],
            "attentionPeopleNum"    : item['attentionPeopleNum'],
            "fans"                  : item['fans'],
            "collectArticleNum"     : item['collectArticleNum'],
            "attentionTagNum"       : item["attentionTagNum"]
        }
        try:
            self.es.create(index=self.index, doc_type=self.type, id=item["id"], body=body)
        except:
            pass

    # 更新文档
    def updateDocument(self, item):
        parm = {
            "doc" : {
                "tag"                   : item['tag'],
                "brief"                 : item['brief'],
                "publishedArticlesNum"  : item['publishedArticlesNum'],
                "hotNum"                : item['hotNum'],
                "shareNum"              : item['shareNum'],
                "initiatePraise"        : item['initiatePraise'],
                "publishedBookNum"      : item['publishedBookNum'],
                "praiseCountNum"        : item['praiseCountNum'],
                "articleReadCountNum"   : item['articleReadCountNum'],
                "attentionPeopleNum"    : item['attentionPeopleNum'],
                "fans"                  : item['fans'],
                "collectArticleNum"     : item['collectArticleNum'],
                "attentionTagNum"       : item["attentionTagNum"]
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
