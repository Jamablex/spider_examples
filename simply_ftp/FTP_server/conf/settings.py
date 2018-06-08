#coding:utf-8
__author__ = "Jam able"
import os

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME_PATH = os.path.join(PATH, "home")

#帐号名与密码
USER_DATA = {
    "xing":"123",
    "ming":"123",
    "feng":"123",
    "yan":"123",
    "yang":"123"
}

LOGIN_STATE = {
    "auth_True": "200",
    "auth_False": "400",
    "file_exit": "202",
    "file_no_exit": "402",
    "cmd_right": "201",
    "cmd_error": "401",
    "dir_exit": "203",
    "dir_no_exit": "403",
    "cmd_success": "204",
    "cmd_fail": "404",
    "size_enough": "205",
    "size_empty": "405",
    "file_not_delivered": "206",  # 文件未上传完
}

MAX_SIZE = 2**30