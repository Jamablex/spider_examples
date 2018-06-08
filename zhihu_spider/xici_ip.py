#Auther: Jam able
import requests
from lxml import etree
import time
import MySQLdb


#-------------------------------------------------------------------------
#   xici_ip.py
#   版本：0.1
#   作者：Jamable
#   日期：编写日期2018/6/5
#   语言：Python 3.5.x
#   功能:爬取西刺代理的代理ip
#        保存下来并保存到mysql
#       获取随机代理ip的功能函数
#-------------------------------------------------------------------------
conn = MySQLdb.connect("localhost", "root", "123456", "zhihu", charset='utf8')
cursor = conn.cursor()


def xici_ip():
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0"}
    for i in range(150,3177):
        time.sleep(4)
        resp = requests.get("http://www.xicidaili.com/nn/{0}".format(i),headers=headers,proxies=get_ip.get_random_ip()).content.decode()
        html = etree.HTML(resp)
        all_trs = html.xpath('//table[@id="ip_list"]/tr')
        ip_list = []
        for trs in all_trs[1:]:
            speed_str = trs.xpath('./td[7]/div[@class="bar"]/@title')[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            if speed<=2.5:
                ip = trs.xpath('./td[2]/text()')[0]
                port = trs.xpath('./td[3]/text()')[0]
                proxy_type = trs.xpath('./td[6]/text()')[0]
                print(ip)
                ip_list.append((ip,port,proxy_type,speed))
            else:
                print(speed)
                continue

        for ip_info in ip_list:
            cursor.execute(
                "insert into proxy_ip(ip,port,speed,proxy_type) values ('{0}','{1}','{2}','{3}')".format(ip_info[0],ip_info[1],ip_info[3],ip_info[2])
            )
            conn.commit()


class Getip:

    def delete_ip(self,ip):
        delete_sql = "delete from proxy_ip where ip={0}".format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self,ip,port,proxy_type):
        try:
            http_url = "http://www.baidu.com"
            proxy_url = "{0}://{1}:{2}".format(proxy_type,ip,port)
            proxy_dict = {
                "%s"%proxy_type:proxy_url,
            }
            response = requests.get(http_url,proxies=proxy_dict)
        except Exception as e:
         #   print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code>=200 and code<300:
             #   print("effective ip")
                return True
            else:
             #   print("invalid ip and port")
                self.delete_ip(ip)
                return False


    def get_random_ip(self):

        random_sql = "SELECT * FROM proxy_ip ORDER BY RAND() LIMIT 1"
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            proxy_type =ip_info[3]
            judge_re =self.judge_ip(ip,port,proxy_type)
            if judge_re:
             #   print({"%s"%proxy_type:"{0}://{1}:{2}".format(proxy_type,ip,port)})
                return {"%s"%proxy_type:"{0}://{1}:{2}".format(proxy_type,ip,port)}
            else:
                return self.get_random_ip()

# xici_ip()
if __name__=="__main__":
    get_ip = Getip()
    get_ip.get_random_ip()


