#coding:utf-8
__author__ = "Jam able"

#-------------------------------------------------------------------------
#   server_main.py
#   版本：0.1
#   作者：Jamable
#   日期：编写日期2018/5/5
#   语言：Python 3.5.x
#   操作：python server_main.py
#   功能:实现一些ftp的基本功能
#         此为服务器端
#
#-------------------------------------------------------------------------

import os,sys


dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir)

from FTP_server.core import sock_main


if __name__ == "__main__":
    sock_main.run()