#Auther: Jam able

import requests
from lxml import etree
import json
import re
from selenium import webdriver
from copy import deepcopy


class xiaowangzi:
    def __init__(self):
        self.start_url ="https://book.douban.com/subject/1084336/comments/"
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0"}


    def get_comment_list(self,url,item):
        resp =requests.get(url,headers=self.headers).content.decode()
        html = etree.HTML(resp)
        all_comment=html.xpath('//div[@class="comment"]')
        for i  in all_comment:
            item["comment_auther"] = i.xpath('./h3/span[2]/a/text()')
            item["comment"] = i.xpath('./p/text()')
            self.comment_write(item)
            print(item)


        next_url = html.xpath('//ul[@class="comment-paginator"]/li[3]/a/@href')[0]
        if next_url is not None and next_url!='javascript:void(0)':
            next_url = "https://book.douban.com/subject/1084336/comments/"+next_url
            return self.get_comment_list(next_url,item)


    def comment_write(self,item):
        comment_auther = item["comment_auther"][0]
        comment = item["comment"][0].replace("\n","").replace("\u3000","").strip()
        result = comment_auther+" : "+comment
        with open("comment.text","a+",encoding='utf-8') as f:
            f.write(result+"\n\n")





    def start(self):
        item = {}
        self.get_comment_list(self.start_url,item)






if __name__ =='__main__':
    xiaowangzi = xiaowangzi()
    xiaowangzi.start()






