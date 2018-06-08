#coding:utf-8
__author__ = "Jam able"

#-------------------------------------------------------------------------
#   client_main.py
#   版本：0.1
#   作者：Jamable
#   日期：编写日期2018/5/5
#   语言：Python 3.5.x
#   操作：python client_main.py
#   功能:实现一些ftp的基本功能
#         此为客户端
#
#-------------------------------------------------------------------------


from FTP_client.core import ftp_client

if __name__ == "__main__":
    ftp_client.run()