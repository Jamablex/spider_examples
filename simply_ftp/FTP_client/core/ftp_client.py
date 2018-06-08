#coding:utf-8
__author__ = "Jam able"

#-------------------------------------------------------------------------
#   ftp_client.py
#   版本：0.1
#   作者：Jamable
#   日期：编写日期2018/5/5
#   语言：Python 3.5.x
#   操作：python client_main.py
#   功能:实现一些ftp的基本功能
#         此为客户端
#
#-------------------------------------------------------------------------


import socket
import hashlib
import json
import os
import time
import threading
import tkinter
import tkinter.messagebox
from tkinter import *
from FTP_client.conf import settings


def w1(func):
    def feature(self,args):
        if len(args) > 1:
            action = args[0]
            filename = args[1]
            msg ={
                "action":action,
                "filename":filename,
            }
            self.client.send(json.dumps(msg).encode())
            server_response = self.client.recv(1024).decode()
            self.textbox4.insert(END, server_response+"\n\n")

        else:
            self.textbox4.insert(END, "wrong order"+"\n\n")
        return func(self,args)
    return feature

def w2(func1):
    def feature1(self,args):
        if len(args) == 1:
            msg = {
                "action": args[0]
            }
            self.client.send(json.dumps(msg).encode())
            server_response = self.client.recv(1024).decode()
            self.textbox4.insert(END, server_response+"\n\n")
        else:
            self.textbox4.insert(END, "wrong order"+"\n\n")
        return func1(self, args)
    return feature1

def w3(func):
    def feature(self,args):
        self.textbox5.delete(0.0, END)
        self.textbox6.delete(0.0, END)
        self.pwd(['pwd'])
        self.ls(['ls'])
        return func(self,args)
    return feature


class MYTCPClient:
    def __init__(self, server_address,connect=True):
        self.client = socket.socket()
        self.server_address=server_address
        if connect:
            try:
                self.client_connect()
            except:
                self.client_close()
                raise
        self.top = tkinter.Tk()
        #self.top1 = tkinter.Tk()
        self.top1 = Toplevel()
        self.top.title("用户登录")
        self.top1.title("客户端")
        self.top1.withdraw()
        self.top.update()
        self.top.geometry('800x600+300+100')
        self.top1.geometry('800x600+300+100')
        label1 = Label(self.top,text="用户名:",font=("宋体",15)).place(x=230,y=250)
        label2 = Label(self.top,text="密码:",font=("宋体",15)).place(x=250,y=300)
        label3 = Label(self.top,text="FTP 用 户 登 录",font=("楷体",25)).place(x=270,y=120)
        label4 = Label(self.top1,text="请输入命令:",font=("宋体",15)).place(x=50,y=100)
        label5 = Label(self.top1,text="状态信息:",font=("宋体",15)).place(x=70,y=150)
        label6 = Label(self.top1,text="任务进度:",font=("宋体",15)).place(x=70,y=50)
        label7 = Label(self.top1,text="当前目录下文件:",font=("宋体",15)).place(x=400,y=150)
        label8 = Label(self.top1,text="当前目录:",font=("宋体",15)).place(x=460,y=100)
        self.username = Entry(self.top,width=20,font=("宋体",15))
        self.password = Entry(self.top,width=20,font=("宋体",15),show='*')
        self.textbox3 = Entry(self.top1,font=("宋体",15))
        self.textbox4 = Text(self.top1, width=25, height=40,font=("宋体",12))
        self.textbox5 = Text(self.top1, width=25, height=1.5,font=("宋体",12))
        self.textbox6 = Text(self.top1, width=25, height=10,font=("宋体",12))
        self.x = StringVar()
        label9 = Label(self.top1,textvariable=self.x,font=("宋体",15)).place(x=285,y=52)
        self.x.set("0.00%")
        self.username.place(x=310,y=250)
        self.password.place(x=310,y=300)
        self.textbox3.place(x=170,y=100)
        self.textbox4.place(x=170,y=150)
        self.textbox5.place(x=570,y=100)
        self.textbox6.place(x=570,y=150)
        #self.button1 = Button(self.top, text="登录", command=lambda:self.thread_it(self.auth,None),font=("宋体",15)).place(x=280,y=400)
        self.button1 = Button(self.top, text="登录", command=self.auth,font=("宋体",15)).place(x=280,y=400)
        self.button3 = Button(self.top, text="退出", command=self.frameclose,font=("宋体",15)).place(x=450,y=400)
        self.button2 = Button(self.top1, text="确定", command=self.interactive,font=("宋体",12)).place(x=400,y=100)
        self.button4 = Button(self.top1, text="上传", command=lambda:self.thread_it(self.put,self.textbox3.get().strip().split()),font=("宋体",12)).place(x=400,y=50)
        self.canvas = Canvas(self.top1, width=110, height=30, bg="white")
        self.canvas.place(x=170,y=50)
        self.out_rec = self.canvas.create_rectangle(5, 5, 105, 25, outline="blue", width=1)
        self.fill_rec = self.canvas.create_rectangle(5, 5, 5, 25, outline="", width=0, fill="blue")
        self.top.mainloop()
        self.top1.mainloop()





    def thread_it(self,func,*args):
        t = threading.Thread(target=func,args=args)
        t.setDaemon(True)
        t.start()

    def frameclose(self):
        self.top.destroy()
        self.top1.destroy()

    def auth(self):
        user_name = self.username.get()
        pwd = self.password.get()
        pwd_hash=hash(pwd)
        user_data = '%s:%s'%(user_name,pwd_hash)
        self.client.send(user_data.encode())
        server_response = self.client.recv(1024).decode()
        if server_response ==settings.LOGIN_STATE["auth_True"]:
            tkinter.messagebox.showinfo('登录','登陆成功！')
            self.top.withdraw()
            self.top1.deiconify()
            self.interactive()
            return 1
        else:
            tkinter.messagebox.showinfo('登录','登录失败！请检查用户名或密码！')


    def interactive(self):
        try:
            self.textbox5.delete(0.0, END)
            self.textbox6.delete(0.0, END)
            self.pwd(['pwd'])
            self.ls(['ls'])
            user_input = self.textbox3.get().strip()
            l = user_input.split()
            action = l[0]
            if hasattr(self, action):
                func = getattr(self, action)
                func(l)  # put(put week02b.mp4)
            elif l[0] == "cd..":
                self.re_cd(l)
            else:
                self.help()
            self.textbox3.delete('0','end')
        except:
            pass


    def client_connect(self):
        self.client.connect(self.server_address)


    def help(self):
        msg = '''
        ls
        cd../..
        cd filename
        mkdir filename
        get filename
        put filename
        '''
        self.textbox4.insert(END,"请输入有效命令，示例:"+msg+"\n\n")


    def client_close(self):
        self.client.close()

    @w1
    @w3
    def cd(self,args):
        pass


    def rename(self,args):
        if len(args) > 1:
            action = args[0]
            old_filename = args[1]
            new_filename = args[2]
            msg ={
                "action":action,
                "old_filename":old_filename,
                "new_filename":new_filename,
            }
            self.client.send(json.dumps(msg).encode())
            server_response = self.client.recv(1024).decode()
            self.textbox4.insert(END, server_response+"\n\n")
            self.textbox5.delete(0.0, END)
            self.textbox6.delete(0.0, END)
            self.pwd(['pwd'])
            self.ls(['ls'])
        else:
            self.textbox4.insert(END, "wrong order"+"\n\n")

    @w1
    @w3
    def mkdir(self,args):
        pass

    def pwd(self,args):
        if len(args) == 1:
            msg = {
                "action": args[0]
            }
            self.client.send(json.dumps(msg).encode())
            server_response = self.client.recv(1024).decode()
            self.textbox5.insert(END, server_response+"\n\n")
        else:
            self.textbox5.insert(END, "wrong order"+"\n\n")


    def ls(self,args):
        if len(args) == 1:
            msg = {
                "action": args[0]
            }
            self.client.send(json.dumps(msg).encode())
            server_response = self.client.recv(1024).decode()
            self.textbox6.insert(END, server_response+"\n\n")
        else:
            self.textbox6.insert(END, "wrong order"+"\n\n")

    @w1
    @w3
    def remove(self,args):
        pass


    @w2
    @w3
    def re_cd(self,args):
        pass


    def put(self,args):
        if len(args) > 1:
            action = args[0]
            filename = args[1]
            self.textbox4.insert(END, filename+"\n\n")
            if  not os.path.isfile(filename):
                self.textbox4.insert(END,"file is not exit"+"\n\n")
                return
            else:
                filesize = os.stat(filename).st_size
            msg = {
                "action":action,
                "filename":filename,
                "filesize":filesize,
            }
            self.client.send(json.dumps(msg).encode())
            server_response = json.loads(self.client.recv(1024).decode())
            self.textbox4.insert(END, "======="+server_response+"\n\n")
            if server_response ==settings.LOGIN_STATE["file_no_exit"] or server_response ==settings.LOGIN_STATE["file_exit"]:
                with open(filename,"rb")  as f:
                    for line in f:
                        self.client.send(line)
                        file_now_size = f.tell()
                        progress_bar1(self,file_now_size,filesize)
                    else:
                        self.textbox4.insert(END, "upload success!"+"\n\n")
                        self.textbox5.delete(0.0, END)
                        self.textbox6.delete(0.0, END)
                        self.pwd(['pwd'])
                        self.ls(['ls'])
            elif server_response ==settings.LOGIN_STATE["file_not_delivered"]:
                new_file_size = self.client.recv(1024).decode()
                with open(filename,'rb') as f:
                    f.seek(int(new_file_size))
                    for line in f:
                        self.client.send(line)
                        file_now_size = f.tell()
                        progress_bar1(self,file_now_size,filesize)
                    else:
                        self.textbox4.insert(END, "upload success!"+"\n\n")
                        self.textbox5.delete(0.0, END)
                        self.textbox6.delete(0.0, END)
                        self.pwd(['pwd'])
                        self.ls(['ls'])

            elif server_response ==settings.LOGIN_STATE["size_empty"]:
                self.textbox4.insert(END, "磁盘空间不足，无法上传！"+"\n\n")


    def get(self, args):
        '下载'
        if len(args) > 1:
            filename = args[1]
            msg_dic = {  # 为了可拓展性，用字典形式
                "action": "get",  # 发送给服务端的指令
                "filename": filename,
            }
            file_list = filename.split('.')
            new_filename = file_list[0] + ".new." + file_list[1]
            self.client.send(json.dumps(msg_dic).encode())
            # 等服务器确认
            server_response = json.loads(self.client.recv(1024).decode())
            if server_response["file_exit"] == settings.LOGIN_STATE["file_exit"]:
                self.client.send("客户端已准备好下载".encode())
                if os.path.isfile(msg_dic["filename"]):  # 文件已经存在
                    f = open(new_filename, "wb")
                else:
                    f = open(filename, "wb")
                receive_size = 0
                while receive_size < server_response["file_size"]:
                    data = self.client.recv(1024)
                    receive_size += len(data)
                    # 调用progress_bar模块的方法
                    progress_bar1(self, receive_size, server_response["file_size"])
                    f.write(data)
                else:
                    self.textbox4.insert(END, "download from server success！"+"\n\n")
                    self.textbox5.delete(0.0, END)
                    self.textbox6.delete(0.0, END)
                    self.pwd(['pwd'])
                    self.ls(['ls'])
                    f.close()

            elif server_response["file_exit"] == settings.LOGIN_STATE["file_no_exit"]:
                self.textbox4.insert(END,"%s:请求文件不存在" % server_response["file_exit"]+"\n\n")


def progress_bar1(self, now_schedule, all_schedule):
    self.canvas.coords(self.fill_rec, (5, 5, 6 + (now_schedule / all_schedule) * 100, 25))
    self.top1.update()
    self.x.set(str(round(now_schedule / all_schedule * 100, 2)) + '%')
    if round(now_schedule / all_schedule * 100, 2) == 100.00:
        self.x.set("完成")



def hash(data):
    m=hashlib.md5()
    m.update(data.encode('utf8'))
    return m.hexdigest()


def run():
    MYTCPClient(('127.0.0.1', 9999))
