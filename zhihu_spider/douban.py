#Auther: Jam able

import requests
from lxml import etree
import re
from openpyxl import workbook




class douban:
    def __init__(self):
        self.douban_url = "https://book.douban.com"
        self.start_url ="https://book.douban.com/tag/?view=type&icn=index-sorttags-hot"
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0"}
        self.wb = workbook.Workbook()
        self.ws = self.wb.active
        self.ws.append(['书名','评分','评价人数'])

    def start_flag(self,url):
        resp =requests.get(url,headers=self.headers).content.decode()
        html = etree.HTML(resp)
        nodes=html.xpath('//table[@class="tagCol"]/tbody/tr/td/a/@href')
        item = {}
        for node in nodes:
            if node is not None:
                novel_list = self.douban_url + node
                self.get_novel_message(novel_list, item)


    def get_novel_message(self,url,item):
        resp =requests.get(url,headers=self.headers).content.decode()
        html = etree.HTML(resp)
        nodes=html.xpath('//ul[@class="subject-list"]/li/div[2]')
        for node  in nodes:
            item["novel_name"] = node.xpath('./h2/a/text()')
            item["novel_score"] = node.xpath('./div[2]/span[2]/text()')
            item["comment"] = node.xpath('./div[2]/span[3]/text()')
            self.save_excel(item)

        next_url = html.xpath('//div[@class="paginator"]/span[@class="next"]/a/@href')[0]
        if next_url is not None and next_url!='javascript:void(0)':
            next_url = self.douban_url+next_url
            return self.get_novel_message(next_url,item)

    def save_excel(self,item):
        novel_name = item["novel_name"][0].strip()
        novel_score = item["novel_score"][0].strip()
        comment = item["comment"][0].strip()
        comment_number = re.findall("\d+",comment)[0]
        self.ws.append((novel_name,novel_score,comment_number))
        self.wb.save("comment.xlsx")


    def comment_write(self,item):
        novel_name = item["novel_name"][0].strip()
        novel_score = item["novel_score"][0].strip()
        comment = item["comment"][0].strip()
        comment_number = re.findall("\d+",comment)[0]
        if float(novel_score)>=8.0:
            result = novel_name+"\t"+novel_score+"\t"+comment_number
            with open("comment.text","a+",encoding='utf-8') as f:
                f.write(result+"\n\n")



    def start_(self):
        self.start_flag(self.start_url)



if __name__ =='__main__':
    douban = douban()
    douban.start_()
