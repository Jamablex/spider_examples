#Auther: Jam able
# coding=gbk

#-------------------------------------------------------------------------
#   zhihu_topic.py
#   版本：0.1
#   作者：Jamable
#   日期：编写日期2018/6/5
#   语言：Python 3.5.x
#   操作：python zhihu_topic.py
#   功能:获取知乎所有精华话题以及用户的回答，
#         保存下来并保存到mysql
#
#-------------------------------------------------------------------------

import requests
import time
from selenium import webdriver
from lxml import etree
import json
import re
import MySQLdb
from xici_ip import Getip
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent



class zhihu:

    def __init__(self):
        self.ua = UserAgent()
        self.get_ip = Getip()
        self.sleep_time = random.randint(3,6)
        self.start_url = "https://www.zhihu.com"
        self.zhihu_topic_square_url = "https://www.zhihu.com/topics"
        self.topic_url ="https://www.zhihu.com/node/TopicsPlazzaListV2"
        self.question_url = "https://www.zhihu.com/question/"
        self.questions_url = "https://www.zhihu.com/api/v4/topics/{0}/feeds/essence?include=data%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Danswer%29%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Danswer%29%5D.target.is_normal%2Ccomment_count%2Cvoteup_count%2Ccontent%2Crelevant_info%2Cexcerpt.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Darticle%29%5D.target.content%2Cvoteup_count%2Ccomment_count%2Cvoting%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Dpeople%29%5D.target.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Danswer%29%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Danswer%29%5D.target.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Darticle%29%5D.target.content%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dquestion%29%5D.target.comment_count&limit=10&offset=0"
        self.answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=5&offset=0&sort_by=default"
        self.headers =  {
            'Host': 'www.zhihu.com',
            'User-Agent': self.ua.random,
            'Referer':'https://www.zhihu.com/topics',
            'X-Requested-With':'XMLHttpRequest',
        }
        self.xsrf = ""
        self.item = {}
        self.anthor_id_list = []
        self.session = requests.session()
        self.session.headers.update(self.headers)
        self.browser = webdriver.Firefox(executable_path='D:\第三方文件\geckodriver.exe')


    def selenium_login(self):
        self.browser.get("https://www.zhihu.com/signup?next=%2F#signin")
        self.browser.find_element_by_css_selector(".SignContainer-switch span").click()
        self.browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper Input").send_keys("账号")
        self.browser.find_element_by_css_selector(".SignFlow-password Input").send_keys("密码")
        self.browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
        time.sleep(10)
        selenium_cookies = self.browser.get_cookies()
        self.xsrf = selenium_cookies[1]['value']
        self.session_request(selenium_cookies)


    def session_request(self,cookies):
        for i in cookies:
             requests.utils.add_dict_to_cookiejar(self.session.cookies, {i['name']: i['value']})
        self.zhihu_topic()


    def zhihu_topic(self):
        resp = self.session.get(self.zhihu_topic_square_url,headers=self.headers).content.decode('utf-8')
        html = etree.HTML(resp)
        nodes = html.xpath('//ul[@class="zm-topic-cat-main clearfix"]')
        for node in nodes:
            topic_ids =node.xpath('./li/@data-id')
            for topic_id in topic_ids:
                self.zhihu_spider(self.topic_url,topic_id)
               # topic = node.xpath('./li/a/@href')[i]


    def zhihu_spider(self,url,topic_id):
        offset = -20
        while True:
            offset = offset+20
            params = {"topic_id":topic_id,"offset":offset,"hash_id":''}
            params_json = json.dumps(params)
            data = {
                "method": "next",
                "params": params_json,
                "_xsrf":self.xsrf

            }
            resp = self.session.post(url, data=data,headers=self.headers,proxies=self.get_ip.get_random_ip()).content.decode('utf-8')
            parse_json = json.loads(resp)
            urls=[]
            try:
                for i in range(20):
                    msg = parse_json['msg'][i]
                    html = etree.HTML(msg)
                    child_topic = html.xpath('//a[@target="_blank"]/@href')[0]
                    child_topic_number = re.findall("\d+", child_topic)[0]
                    # topic_url = self.start_url+topic+'/hot'
                    self.json_url_spider(self.questions_url.format(child_topic_number),urls)
            except Exception as e:
                print(e)
                break


    def json_url_spider(self,url,urls):
        resp = self.session.get(url,headers=self.headers,proxies=self.get_ip.get_random_ip()).content.decode()
        parse_json = json.loads(resp)
        is_end = parse_json["paging"]["is_end"]
        next_url = parse_json["paging"]["next"]
        item={}
        for i in range(0,10):
            try:
                if "question" in parse_json["data"][i]["target"]:
                    question_url = parse_json["data"][i]["target"]["question"]["url"]
                    re_find = re.findall("\d+",question_url)[1]
                    question_url_now =self.question_url+re_find
                    print(question_url_now)
                    if question_url_now not in list(set(urls)):
                        urls.append(question_url_now)
                        item['question_url'] = question_url_now
                        time.sleep(self.sleep_time)
                        self.question_message(question_url_now,re_find,item)
                    else:
                        continue
                else:
                    continue
            except Exception as e:
                print(e)

        if not is_end:
            self.json_url_spider(next_url,urls)
        else:
            return "已全部爬取完毕"



    def question_message(self,question_url,question_id,item):
        resp = self.session.get(question_url,headers=self.headers,proxies=self.get_ip.get_random_ip()).content.decode()
        html = etree.HTML(resp)
        question_tags = html.xpath('//span[@class="Tag-content"]/a/div/div/text()')
        question_tag = ",".join(question_tags)
        question_title = html.xpath('//div[@class="QuestionHeader-main"]/h1[@class="QuestionHeader-title"]/text()')[0]
     #   for question_title in question_titles:

        attention = html.xpath('//div[@class="NumberBoard-itemInner"]/strong/@title')[0]
        browse = html.xpath('//div[@class="NumberBoard-itemInner"]/strong/@title')[1]
        item["question_tag"] = question_tag
        item["question_title"] = question_title
        item["attention"] = attention
        item["browse"] = browse
        print(item["question_title"])
        anthor_id_list = []
        self.answer_message(self.answer_url.format(question_id),item,anthor_id_list)


    def answer_message(self,answer_url,item,anthor_id_list):
        resp = self.session.get(answer_url,headers=self.headers,proxies=self.get_ip.get_random_ip()).content.decode()
        parse_json = json.loads(resp)
        is_end = parse_json["paging"]["is_end"]
        next_url = parse_json["paging"]["next"]

        for i in range(0,5):
            try:
                initial_content = parse_json["data"][i]["content"] if "content" in parse_json["data"][i] else None
                content = BeautifulSoup(initial_content,'lxml').get_text()
                anthor_name = parse_json["data"][i]["author"]["name"] if "name" in parse_json["data"][i]["author"] else None
                anthor_headline = parse_json["data"][i]["author"]["headline"] if "headline" in parse_json["data"][i]["author"] else None
               # anthor_url_token = parse_json["data"][i]["author"]["url_token"] if "url_token" in parse_json["data"][i]["author"] else None
                anthor_id = parse_json["data"][i]["id"] if "id" in parse_json["data"][i] else None
                ehdorse_number = parse_json["data"][i]["voteup_count"] if "voteup_count" in parse_json["data"][i] else None
            except Exception as e:
                print(e)

            if anthor_id not in list(set(anthor_id_list)):
                anthor_id_list.append(anthor_id)
                item["content"] = content
                item["anthor_name"] = anthor_name
                item["anthor_headline"] = anthor_headline
                #item["anthor_url_token"] = anthor_url_token
                item["anthor_id"] = anthor_id
                item["ehdorse_number"] = ehdorse_number
                # time.sleep(self.sleep_time)
                json_item = json.dumps(item)
                self.save_mysql(json_item)
            else:
                continue
        # if not is_end:
        #     time.sleep(self.sleep_time)
        #     self.answer_message(next_url,item,anthor_id_list)


    def save_mysql(self,json_item):
        item = json.loads(json_item)
        # print(item["question_title"],item["question_tag"])
        conn = MySQLdb.connect("localhost","root","123456","zhihu",charset='utf8')
        cursor = conn.cursor()
        sql = "insert into zhihu_message(question_url,question_title,question_tag,attention,browse,anthor_name,anthor_headline,anthor_id,ehdorse_number,content) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = (item["question_url"],item["question_title"],item["question_tag"],item["attention"],item["browse"],item["anthor_name"],item["anthor_headline"],item["anthor_id"],item["ehdorse_number"],item["content"])
        cursor.execute(sql,params)
        conn.commit()
        cursor.close()
        conn.close()


if __name__=="__main__":
    zhihu = zhihu()
    zhihu.selenium_login()