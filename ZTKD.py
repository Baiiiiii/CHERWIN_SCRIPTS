# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# ✨✨✨ 中通快递小程序签到✨✨✨
# ✨ 功能：
#       积分签到
# ✨ 抓包步骤：
#       打开中通快递小程序
#       授权登陆
#       打开抓包工具
#       找URl请求头带[x-token或者token]
#       复制里面的[x-token或者token]参数值
# 参数示例：eyJhbGciOiJIUzUxMiJ9.eyJnZW5lcmF0ZVRpbWUixxxxxx
# ✨ 设置青龙变量：
# export YDKD='x-token或者token参数值'多账号#或&分割
# export SCRIPT_UPDATE = 'False' 关闭脚本自动更新，默认开启
# ✨ ✨ 注意：抓完CK没事儿别打开小程序，重新打开小程序请重新抓包
# ✨ 推荐cron：0 6 * * *
# ✨✨✨ @Author CHERWIN✨✨✨
# -------------------------------
# cron "0 6 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('中通快递小程序签到')
import json
import os
import random
import time
from datetime import datetime, date
from os import path
import requests
import hashlib
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# import CHERWIN_TOOLS
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#
if os.path.isfile('DEV_ENV.py'):
    import DEV_ENV
if os.path.isfile('notify.py'):
    from notify import send
    print("加载通知服务成功！")
else:
    print("加载通知服务失败!")
send_msg = ''
one_msg=''
def Log(cont=''):
    global send_msg,one_msg
    print(cont)
    if cont:
        one_msg += f'{cont}\n'
        send_msg += f'{cont}\n'

class RUN:
    def __init__(self,info,index):
        global one_msg
        one_msg = ''
        split_info = info.split('@')
        self.token = split_info[0]
        len_split_info = len(split_info)
        last_info = split_info[len_split_info - 1]
        self.send_UID = None
        if len_split_info > 0 and "UID_" in last_info:
            print('检测到设置了UID')
            print(last_info)
            self.send_UID = last_info
        self.index = index + 1

        self.headers = {
            'Host': 'api.ztomember.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/6945',
            'token': self.token,
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://h5.ztomember.com/',
            'Accept-Language': 'zh-CN,zh',

        }

        self.baseUrl = 'https://api.ztomember.com/api/'
        self.news_List = []
        self.list_index = 0
        self.isFirstTask = True

    def get_point(self):
        Log('>>>>>>获取积分信息')
        json_data = {}
        response = s.post(f'{self.baseUrl}user/point/get', headers=self.headers,json=json_data)
        point_info = response.json()
        # print(point_info)
        code = point_info.get('code',-1)
        if point_info.get('success',False) == True and code == 10000:
            data = point_info.get('data',[{}])
            point=data.get('point',0)
            mobile=data.get('mobile','')
            mobile=mobile[:3] + "*" * 4 + mobile[7:]
            Log(f'>>当前用户：【{mobile}】')
            Log(f'>>当前积分：【{point}】')
            return True
        else:
            Log('可能token失效了')
            return False

    def Check_sign(self):
            Log('>>>>>>查询签到')
            json_data = {"calendarType":0}
            response = s.post(f'{self.baseUrl}member/sign/v2/calendar', headers=self.headers,json=json_data)
            response = response.json()
            # print(point_info)
            code = response.get('code', -1)
            if response['success']== True and response['data'] != None and code == 10000:
                data=response.get('data',{})
                dayList=data.get('dayList',[{}])
                signDays=data.get('signDays',0)
                Len_dayList=len(dayList)
                dates = dayList[Len_dayList-1].get('date','')
                current_date = date.today()
                parsed_date = datetime.strptime(dates, '%Y-%m-%d').date()
                if parsed_date == current_date:
                    Log(f'今日已签到,连续签到【{signDays}】天')
                else:
                    self.sign()
            else:
                Log(f"查询签到失败，{response['msg']}")
    def sign(self):
            Log('>>>>>>签到')
            json_data = {}
            response = s.post(f'{self.baseUrl}member/sign/v2/userSignIn', headers=self.headers,json=json_data)
            point_info = response.json()
            # print(point_info)
            code = point_info.get('code', -1)
            if point_info['success']== True and point_info['data'] != None and code == 10000:
                point=point_info['data']['point']
                Log(f'>>签到成功获得：【{point}】积分')
            else:
                Log(f"签到失败，{point_info['msg']}")



    def main(self):
        print(f"\n开始执行第{self.index}个账号--------------->>>>>")
        if self.get_point():
            self.Check_sign()
            self.get_point()
            time.sleep(2)
            self.sendMsg()
        else:
            return False

    def sendMsg(self):
        if self.send_UID:
            push_res = CHERWIN_TOOLS.wxpusher(self.send_UID, one_msg, APP_NAME)
            print(push_res)


def down_file(filename, file_url):
    print(f'开始下载：{filename}，下载地址：{file_url}')
    try:
        response = requests.get(file_url, verify=False, timeout=10)
        response.raise_for_status()
        with open(filename + '.tmp', 'wb') as f:
            f.write(response.content)
        print(f'【{filename}】下载完成！')

        # 检查临时文件是否存在
        temp_filename = filename + '.tmp'
        if os.path.exists(temp_filename):
            # 删除原有文件
            if os.path.exists(filename):
                os.remove(filename)
            # 重命名临时文件
            os.rename(temp_filename, filename)
            print(f'【{filename}】重命名成功！')
            return True
        else:
            print(f'【{filename}】临时文件不存在！')
            return False
    except Exception as e:
        print(f'【{filename}】下载失败：{str(e)}')
        return False

def import_Tools():
    global CHERWIN_TOOLS,ENV, APP_INFO, TIPS, TIPS_HTML, AuthorCode
    import CHERWIN_TOOLS
    ENV, APP_INFO, TIPS, TIPS_HTML, AuthorCode = CHERWIN_TOOLS.main(APP_NAME, local_script_name, ENV_NAME,local_version)

if __name__ == '__main__':
    APP_NAME = '中通快递小程序'
    ENV_NAME = 'ZTKD'
    CK_NAME = 'x-token或者token'
    print(f'''
✨✨✨ {APP_NAME}签到✨✨✨
✨ 功能：
      积分签到
✨ 抓包步骤：
      打开{APP_NAME}
      授权登陆
      打开抓包工具
      找URl请求头带[{CK_NAME}]
      复制里面的[{CK_NAME}]参数值
参数示例：eyJhbGciOiJIUzUxMiJ9.eyJnZW5lcmF0ZVRpbWUixxxxxx
✨ 设置青龙变量：
export {ENV_NAME}='{CK_NAME}参数值'多账号#或&分割
export SCRIPT_UPDATE = 'False' 关闭脚本自动更新，默认开启
✨ ✨ 注意：抓完CK没事儿别打开小程序，重新打开小程序请重新抓包
✨ 推荐cron：0 6 * * *
✨✨✨ @Author CHERWIN✨✨✨
''')
    local_script_name = os.path.basename(__file__)
    local_version = '2024.04.06'
    if os.path.isfile('CHERWIN_TOOLS.py'):
        import_Tools()
    else:
        if down_file('CHERWIN_TOOLS.py', 'https://py.cherwin.cn/CHERWIN_TOOLS.py'):
            print('脚本依赖下载完成请重新运行脚本')
            import_Tools()
        else:
            print('脚本依赖下载失败，请到https://py.cherwin.cn/CHERWIN_TOOLS.py下载最新版本依赖')
            exit()
    print(TIPS)
    token = ''
    token = ENV if ENV else token
    if not token:
        print(f"未填写{ENV_NAME}变量\n青龙可在环境变量设置 {ENV_NAME} 或者在本脚本文件上方将{CK_NAME}填入token =''")
        exit()
    tokens = CHERWIN_TOOLS.ENV_SPLIT(token)
    # print(tokens)
    if len(tokens) > 0:
        print(f"\n>>>>>>>>>>共获取到{len(tokens)}个账号<<<<<<<<<<")
        access_token = []
        for index, infos in enumerate(tokens):
            s = requests.session()
            s.verify = False
            run_result = RUN(infos, index).main()
            if not run_result: continue
        if send: send(f'{APP_NAME}挂机通知', send_msg + TIPS_HTML)