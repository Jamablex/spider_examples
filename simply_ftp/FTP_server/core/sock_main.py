
#-------------------------------------------------------------------------
#   sock_main.py
#   版本：0.1
#   作者：Jamable
#   日期：编写日期2018/5/5
#   语言：Python 3.5.x
#   操作：python server_main.py
#   功能:实现一些ftp的基本功能
#         此为服务器端
#
#-------------------------------------------------------------------------

import json
import socketserver
import os,hashlib
from FTP_server.conf import settings


class MyTCPHandler(socketserver.BaseRequestHandler):


    def cd(self,*args):
        msg = args[0]
        self.current_path = os.path.abspath(self.current_path)
        print(self.current_path)
        filename = msg["filename"]
        file_path = os.path.join(self.current_path, filename)
        if os.path.isdir(file_path):
            if len(os.path.abspath(file_path)) <= len(settings.HOME_PATH):
                self.request.send("no  permission!".encode())
            else:
                new_path = os.path.abspath(file_path)
                self.current_path = new_path
                self.request.send(self.current_path.encode())
        else:
            self.request.send("dir is not exit!".encode())

    def rename(self,*args):
        cmd_dic = args[0]
        old_filename = cmd_dic["old_filename"]
        print(type(old_filename))
        new_filename = cmd_dic["new_filename"]
        print(new_filename)
        file_name = os.path.join(self.current_path, old_filename)
        new_file_name = os.path.join(self.current_path, new_filename)
        try:
            if os.path.isdir(file_name):
                os.rename(file_name,new_file_name)
                self.request.send("rename success!".encode())
            else:
                self.request.send("rename break down!".encode())
        except:
            self.request.send("filename is exit!".encode())

    def pwd(self,*args):
        self.current_path = os.path.abspath(self.current_path)
        self.request.send(self.current_path.encode())

        pass
    def remove(self,*args):
        cmd_dic = args[0]
        filename = cmd_dic["filename"]
        file_path = os.path.join(self.current_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                self.request.send("delete file success!".encode())
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
                self.request.send("delete floder success!".encode())
            else:
                self.request.send("file is not exit!".encode())
        except:
            self.request.send("floder is not null,can't delete!".encode())



    def re_cd(self,*args):
        now_path = os.path.dirname(self.current_path)
        if len(os.path.abspath(now_path)) != len(settings.HOME_PATH):
            new_now_path = os.path.abspath(now_path)
            self.current_path = new_now_path
            self.request.send(now_path.encode())
        else:
            self.request.send("no  permission!".encode())

    def mkdir(self,*args):
        msg = args[0]
        filename = msg["filename"]
        self.current_path = os.path.abspath(self.current_path)
        folder = os.path.join(self.current_path,filename)
        if not os.path.isdir(folder):
            os.mkdir(folder)
            self.request.send("create folder success!".encode())
        else:
            self.request.send("the folder is exit!".encode())


    def ls(self,*args):
        msg = args[0]
        self.current_path = os.path.abspath(self.current_path)
        ls = os.listdir(self.current_path)
        self.request.send(json.dumps(ls).encode())


    def put(self, *args):
        print (args)
        cmd_dic = args[0]
        print (cmd_dic)
        filename = cmd_dic["filename"]
        file_size = cmd_dic["filesize"]
        file_list = filename.split('.')
        new_filename = file_list[0]+".new."+file_list[1]
        file_path = os.path.join(self.current_path, filename)
        new_file_path = os.path.join(self.current_path, new_filename)

        dir_size = get_dirsize(self.user_home_path)

        print("当前用户磁盘空间大小:%s" % dir_size)
        if dir_size + file_size < settings.MAX_SIZE:

            if os.path.isfile(file_path):
                new_file_size = os.stat(file_path).st_size
             #   print(new_file_size)
                if new_file_size < file_size:
                    f = open(file_path,"wb")
                    self.request.send(json.dumps(settings.LOGIN_STATE["file_not_delivered"]).encode())
                    f.seek(int(new_file_size))
                    self.request.send(str(new_file_size).encode())
                    while new_file_size < file_size:
                        data = self.request.recv(1024)
                        new_file_size += len(data)
                        f.write(data)
                    else:
                        print("file [%s] has uploaded..." % filename)
                        f.close()
                else:
                    f = open(new_file_path, "wb")
                    self.request.send(json.dumps(settings.LOGIN_STATE["file_exit"]).encode())
                    received_size = 0
                    while received_size < file_size:
                        data = self.request.recv(1024)
                        received_size += len(data)
                        f.write(data)
                    else:
                        print("file [%s] has uploaded..." % filename)
                        f.close()
            else:
                f = open(file_path, "wb")
                self.request.send(json.dumps(settings.LOGIN_STATE["file_no_exit"]).encode())
                received_size = 0
                while received_size < file_size:
                    data = self.request.recv(1024)
                    received_size += len(data)
                    f.write(data)
                else:
                    print("file [%s] has uploaded..." % filename)
                    f.close()

        else:
            self.request.send(json.dumps(settings.LOGIN_STATE["size_empty"]).encode())

    def get(self, *args):
        cmd_dic = args[0]
        filename = cmd_dic["filename"]
        self.current_path = os.path.abspath(self.current_path)
        print(self.current_path)
        now_file = os.path.join(self.current_path,filename)
        if os.path.isfile(now_file):
            file_size = os.stat(now_file).st_size
            msg_dic = {
                "file_size": file_size,
                "file_exit": settings.LOGIN_STATE["file_exit"]
            }
            self.request.send(json.dumps(msg_dic).encode())
            client_response = self.request.recv(1024)
            print(client_response.decode())
            f = open(now_file, "rb")
            for line in f:
                self.request.send(line)
            else:
                print("server:file upload to client success")
                f.close()
        else:
            msg_dic = {"file_exit": settings.LOGIN_STATE["file_no_exit"]}
            self.request.send(json.dumps(msg_dic).encode())


    def handle(self):
        self.user_home_path=''
        while True:
            login_state = auth_login(self)
            if login_state == settings.LOGIN_STATE["auth_True"]:
                while True:
                    try:
                        self.data = self.request.recv(1024).strip()

                        print("{} wrote:".format(self.client_address[0]))
                        print(self.data)
                        cmd_dic = json.loads(self.data.decode())
                        cmd = cmd_dic["action"]

                        if hasattr(self, cmd):
                            func = getattr(self, cmd)
                            func(cmd_dic)  #put()
                        elif cmd == "cd..":
                            self.re_cd(cmd_dic)
                        else:
                            print("反射失败")


                    except ConnectionResetError as e:
                        print("客户端断开",e)
                        break
            elif login_state == settings.LOGIN_STATE["auth_False"]:
                continue

def auth_login(self):
    recv_data = self.request.recv(1024).strip()
    recv_data = recv_data.decode('utf-8')
    recv_list = recv_data.split(":")
    print('=====',recv_list)
    self.current_path = os.path.join(settings.HOME_PATH, recv_list[0])
    self.user_home_path = os.path.join(settings.HOME_PATH, recv_list[0])

    user_path = "%s/users/%s.json" % (settings.PATH, recv_list[0])
    print(user_path)
    if os.path.isfile(user_path):
        print("user(file) exist")
        file_data = user_load(user_path)
        print('-----',file_data)
        print(file_data)
        if file_data["password"] == recv_list[1]:
            print("login success")
            self.request.send(settings.LOGIN_STATE["auth_True"].encode())
            print("send login_state")
            return settings.LOGIN_STATE["auth_True"]
        else:
            self.request.send(settings.LOGIN_STATE["auth_False"].encode())
            print("send login_state")
            return settings.LOGIN_STATE["auth_False"]
    else:
        self.request.send(settings.LOGIN_STATE["auth_False"].encode())
        print("send login_state")
        print("False,please registe")
        return settings.LOGIN_STATE["auth_False"]

def get_dirsize(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size

def initialize_user():
    path = settings.PATH
    for key in settings.USER_DATA:
        user_path = "%s/users/%s.json" % (path, key)
        if not os.path.isfile(user_path):
            password_hash = hash(settings.USER_DATA[key])
            user_data = {
                "username":key,
                "password":password_hash,
                "user_path":os.path.join(settings.HOME_PATH, key),
                "max_size": settings.MAX_SIZE
            }
            #json.dump(user_data, open(user_path,"w",encoding="utf-8"))
            user_dump(user_path, user_data)
    user_homedir()

def user_homedir():
    for key in settings.USER_DATA:
        user_home_path = os.path.join(settings.HOME_PATH, key)
        if not os.path.isdir(user_home_path):
            os.popen("mkdir %s" % user_home_path)

def user_load(user_path):
    user_data = json.load(open(user_path, "r", encoding="utf-8"))
   # print(user_data)
    return user_data

def user_dump(user_path, user_data):
    json.dump(user_data, open(user_path, "w", encoding="utf-8"))

def hash(data):
    m = hashlib.md5()
    m.update(data.encode('utf8'))
    return m.hexdigest()

def run():
    initialize_user()
    server = socketserver.ThreadingTCPServer(('127.0.0.1',9999), MyTCPHandler)
    server.serve_forever()