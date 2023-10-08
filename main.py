'''
Author:Wrundorry @汪嗯个凉
Licence:The MIT Licence.
Time:2023/10/8
Version:
二开请认真阅读完所有注释，不然这个屎山代码会跑不起来。有问题上交 Issues 由开发者处理！

二次开发常用：
获得所有列表信息（调用获得数据库某行全部信息时生效）：
result=result[0] # 得到用户所有信息的数据
uid=result[0] # 数据库独立id -数据库中的全局独立ID
fb_userid=result[1] # fanbook中的userid -Fanbook平台中的用户标识
fb_username=result[2] # fanbookid -Fanbook平台中的用户短ID
fb_nickname=result[3] # 昵称 -默认拉取Fanbook平台中的昵称
fb_toady=result[4] # 上一次打卡时间 
fb_total=result[5] # 累计打卡次数 -一共打卡了多少次
fb_money=result[6] # 累计余额 -一共得了多少余额
img_pay=result[7] # 支付码 -支付方式

miniPush相关：
发起提现：devopen_check_money_out
同意提现申请：devopen_admin_money_t  PS:t代表true，相反f代表false
拒绝提现申请：devopen_admin_money_f
'''
import base64
import json
import threading
import time
import requests
import mysql.connector
import traceback

from websocket import create_connection, WebSocketConnectionClosedException
from datetime import datetime, date

TOKEN = '001bde1cb07f24830a64ff776bf91c48d7b62dd39cfa020bcb10ff435fd8db223ee66bd64559a225daf477c6526e7837' # 机器人Toekn
BOT_ID = '461748625211768832' # 机器人ID
BASE_URL = 'https://a1.fanbook.mobi/api'

DB_NAME="check" # 数据库名
DB_HOST="127.0.0.1" # 数据库主机
DB_USER="check" # 数据库用户名
DB_PWD="lyh110927" # 数据库密码

PLAY_CHAT="541544673882533888" # 签到频道ID
ONE_MONEY="0.01" #单次签到获得余额
DOOR="1" # 提现门槛（元）
SSF="" # 手续费（未支持）
ADMIN="375274330516357120" # 管理员长ID
TABLE_NAME="devopen_users"

def on_message(message): # 消息接收
    s = message.decode('utf8')
    obj = json.loads(s)
    print(obj)
    if obj["action"]=="push": # 推送
        if obj["data"]["channel_id"]==PLAY_CHAT: # 来自签到频道
            content_type=obj["data"]["content"] #获得推送类型
            content_type=json.loads(content_type)
            content_type=content_type["type"] # 解析并得到类型
            if content_type=="text": # 纯文本消息
                content_data=obj["data"]["content"] # 获得文本内容
                content_data=json.loads(content_data)
                content_data=content_data["text"] # 解析并得到文本内容
                if "${@!"+BOT_ID+"}" in content_data: # 提及@了机器人
                    if content_data=="${@!"+BOT_ID+"}${/签到打卡}": # 是签到打卡的指令
                        user_id=obj["data"]["user_id"] # 用户Fanbook UserID
                        fanbookid = obj["data"]["author"]["username"] # 用户FanbookID
                        nickname = obj["data"]["author"]["nickname"] # 用户昵称
                        # 连接数据库
                        conn = mysql.connector.connect(user=DB_USER, password=DB_PWD,
                                                   host='127.0.0.1', database=DB_NAME) 
                        cursor = conn.cursor()
                        query = ('SELECT * FROM `'+TABLE_NAME+'` WHERE FanbookUserId = %s') # 查找用户
                        values = (user_id,) # 插入用户ID
                        cursor.execute(query, values) #发起查询
                        result = cursor.fetchall()
                        # 关闭数据库连接
                        cursor.close()
                        conn.close()
                        if result: # 用户在数据表内
                            result=result[0] # 得到用户所有信息的数据
                            uid=result[0] # 数据库独立id
                            fb_userid=result[1] # fanbook中的userid
                            fb_username=result[2] # fanbookid
                            fb_nickname=result[3] # 昵称
                            fb_toady=result[4] # 上一次打卡时间
                            fb_total=result[5] # 累计打卡次数
                            fb_money=result[6] # 累计余额
                            date_today = datetime.strptime(fb_toady, "%Y%m%d").date() # 将上一次打卡时间解析为可读类型
                            current_date = date.today() # 获得今日时间
                            if date_today == current_date: # 上一次打卡时间与今日时间相同
                                print("已经打卡") # 信息
                                # 发送频道提示
                                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage" 
                                headers = {'content-type': "application/json;charset=utf-8"}
                                jsonfile = json.dumps({
                                    "chat_id": int(PLAY_CHAT),
                                    "text": "{\"notification\":\"签到打卡机器人\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"ffd8d8\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"打卡签到 | 已打卡\\\",\\\"style\\\":{\\\"color\\\":\\\"#ff0000\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"啊哟，你今天好像已经签到了耶~去银行看看吧！╰(￣ω￣ｏ)\\\\n\\\\n----------\\\\n\\\\nDevOpen **银行满 ￥ 1 即可无门槛提现到微信账户或商城抵扣券。**\\\"}}]}\",\"come_from_name\":\"—— DevOpen 官方团队提供支持\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                                    "parse_mode": "Fanbook"
                                })  
                                postreturn = requests.post(url, data=jsonfile, headers=headers)
                            else: # 今日未打卡
                                print("没有打卡") # 信息
                                fb_total=int(fb_total)+1 # 累计打卡天数+1
                                fb_money=float(fb_money)+float(ONE_MONEY) # 累计余额加设定余额
                                today=current_date.strftime("%Y%m%d") # 将今日时间格式化成数据库内记载格式
                                # 连接数据库更新数据
                                conn = mysql.connector.connect(
                                    user=DB_USER,
                                    password=DB_PWD,
                                    host='127.0.0.1',
                                    database=DB_NAME
                                )
                                cursor = conn.cursor()

                                update_query = f"UPDATE `"+TABLE_NAME+"` SET today = " + str(today) + " WHERE FanbookUserId = " + str(
                                    fb_userid) + ""
                                cursor.execute(update_query)
                                                    
                                update_query = f"UPDATE `"+TABLE_NAME+"` SET total = " + str(fb_total) + " WHERE FanbookUserId = " + str(
                                    fb_userid) + ""
                                cursor.execute(update_query)

                                update_query = f"UPDATE `"+TABLE_NAME+"` SET money = " + str(fb_money) + " WHERE FanbookUserId = " + str(
                                    fb_userid) + ""
                                cursor.execute(update_query)

                                conn.commit()
                                # 发送频道通知
                                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage"  # 注意令牌
                                headers = {'content-type': "application/json;charset=utf-8"}
                                jsonfile = json.dumps({
                                    "chat_id": int(PLAY_CHAT),
                                    "text": "{\"notification\":\"签到打卡机器人\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"fff1d8\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"打卡签到 | 打卡成功\\\",\\\"style\\\":{\\\"color\\\":\\\"#ffa400\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"🎉恭喜你签到成功！\\\\n\\\\n----------\\\\n\\\\n🎈累计签到："+str(fb_total)+" 天\\\\n\\\\n💰全部资产：￥ "+str(fb_money)+"\\\\n\\\\n💴今日资产：￥ 0.01\\\"} }]}\",\"come_from_name\":\"—— DevOpen 官方\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                                    "parse_mode": "Fanbook"
                                })  
                                postreturn = requests.post(url, data=jsonfile, headers=headers)
                                print("完成")

                        else: # 用户不在数据库内
                            print("未注册") # 信息
                            print(nickname) # 信息
                            current_date = date.today() # 今日日期
                            today=current_date.strftime("%Y%m%d") # 格式化今日日期
                            try: # 尝试插入用户数据
                                cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,
                                    host='127.0.0.1', database=DB_NAME)
                                cursor = cnx.cursor()

                                add_user = ("INSERT INTO `"+TABLE_NAME+"` "
                                    "(FanbookUserId, FanbookID, nickname ,today,total,money) "
                                    "VALUES ("+str(user_id)+", "+str(fanbookid)+", '"+str(nickname)+"', "+str(today)+",1,0.05)")
                                
                                cursor.execute(add_user)
                                cnx.commit()

                                # 关闭连接
                                cursor.close()
                                cnx.close()
                            except: # 无法插入，因为昵称包含特殊字符
                                cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,
                                    host='127.0.0.1', database=DB_NAME)
                                cursor = cnx.cursor()

                               
                                add_user = ("INSERT INTO `"+TABLE_NAME+"` "
                                    "(FanbookUserId, FanbookID, nickname ,today,total,money) "
                                    "VALUES ("+str(user_id)+", "+str(fanbookid)+", '昵称未同步', "+str(today)+",1,0.05)")

                                cursor.execute(add_user)
                                cnx.commit()

                                # 关闭连接
                                cursor.close()
                                cnx.close()
                            # 频道发送通知
                            url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage"  # 注意令牌
                            headers = {'content-type': "application/json;charset=utf-8"}
                            jsonfile = json.dumps({
                                "chat_id": int(PLAY_CHAT),
                                "text": "{\"notification\":\"签到打卡机器人\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"fff1d8\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"打卡签到 | 打卡成功\\\",\\\"style\\\":{\\\"color\\\":\\\"#ffa400\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"🎉恭喜你签到成功！\\\\n\\\\n----------\\\\n\\\\n🎈累计签到：1 天\\\\n\\\\n💰全部资产：￥ 0.05\\\\n\\\\n💴今日资产：￥ 0.05\\\\n\\\\n----------\\\\n\\\\n您首次使用本机器人打卡，首次资产添加￥0.05，后续每日￥0.01。满￥1即可提现至微信账户或抵换优惠券，**具体请见银行系统**。本条目以后不再显示。\\\"} }]}\",\"come_from_name\":\"—— DevOpen 官方\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                                "parse_mode": "Fanbook"
                            }) 
                            postreturn = requests.post(url, data=jsonfile, headers=headers)
                            print("完成") # 信息
                    elif "${@!"+BOT_ID+"}${/银行系统}": # 是银行功能的指令
                        user_id=obj["data"]["user_id"] # 用户的Fanbook UserID
                        fanbookid = obj["data"]["author"]["username"] # 用户FanbookID
                        nickname = obj["data"]["author"]["nickname"] # 用户昵称
                        # 信息查询
                        conn = mysql.connector.connect(user=DB_USER, password=DB_PWD,
                                                   host='127.0.0.1', database=DB_NAME)
                        cursor = conn.cursor()
                        query = ('SELECT * FROM `'+TABLE_NAME+'` WHERE FanbookUserId = %s')
                        values = (user_id,)
                        cursor.execute(query, values)
                        result = cursor.fetchall()
                        # 关闭数据库连接
                        cursor.close()
                        conn.close()
                        if result: # 仅注册后可用
                            result=result[0] # 得到用户所有信息的数据
                            uid=result[0] # 数据库独立id
                            fb_userid=result[1] # fanbook中的userid
                            fb_username=result[2] # fanbookid
                            fb_nickname=result[3] # 昵称
                            fb_toady=result[4] # 上一次打卡时间
                            fb_total=result[5] # 累计打卡次数
                            fb_money=result[6] # 累计余额
                            # 频道发送用户银行信息 频道通知
                            url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage"  # 注意令牌
                            headers = {'content-type': "application/json;charset=utf-8"}
                            jsonfile = json.dumps({
                                "chat_id": int(PLAY_CHAT),
                                "text": "{\"notification\":\"签到打卡机器人\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"ffffd9\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"打卡签到 | 银行系统\\\",\\\"style\\\":{\\\"color\\\":\\\"#ffc55a\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"💰在线小银行💰\\\\n\\\\n----------\\\\n\\\\n💳银行卡号："+str(uid)+"\\\\n\\\\n🎫提现门槛：￥ "+str(DOOR)+"\\\\n\\\\n🤝今日费率："+str(SSF)+"\\\\n\\\\n----------\\\\n\\\\n🎈累计签到："+str(fb_total)+" 天\\\\n\\\\n💰可用资产：￥ "+str(fb_money)+"\\\"}}]}\",\"come_from_name\":\"—— DevOpen 官方\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                                "parse_mode": "Fanbook",
                                "reply_markup": {
                                    "inline_keyboard": [
                                        [
                                            {
                                                "text": "申请提现",
                                                "callback_data": "{\"come_from\":\"devopen_check_money_out\",\"user_id\":\""+str(fb_userid)+"\",\"fanbook_id\":\""+str(fb_username)+"\",\"chat_id\":\""+str(PLAY_CHAT)+"\"}"
                                            }
                                        ]

                                    ]
                                }
                                                    
                            })  
                            postreturn = requests.post(url, data=jsonfile, headers=headers)
    elif obj["action"]=="miniPush": # 内联键盘穿透消息
        print("按钮回复") # 信息
        try: # 尝试获取穿透信息
            # 这一段都是用来得到code_from的json解析，不要动它。我花了好长时间才解析出来的。
            data = obj["data"]
            data = data["content"]
            data = json.loads(data)

            data = data["callback_query"]
            comefrom = data["from"]["id"]
            data = data["data"]
            data = json.loads(data)

            # 开始解析是不是机器人需要的穿透信息
            if data["come_from"] == "devopen_check_money_out": # devopen_check_money_out信息：用户发起提现申请，管理员查阅审批
                print("提现申请") # 信息
                
                chat_id=data["chat_id"] # 频道ID
                user_id=data["user_id"] # 用户的 Fanbook UserID
                
                if str(user_id)==str(comefrom): # 点击内联键盘的是不是自己，如果是那么
                    # 连接数据库查询用户信息
                    conn = mysql.connector.connect(user=DB_USER, password=DB_PWD,
                                                   host='127.0.0.1', database=DB_NAME)
                    cursor = conn.cursor()
                    query = ('SELECT * FROM `'+TABLE_NAME+'` WHERE FanbookUserId = %s')
                    values = (user_id,)
                    cursor.execute(query, values)
                    result = cursor.fetchall()
                    # 关闭数据库连接
                    cursor.close()
                    conn.close()
                    if result: # 用户信息返回
                        result=result[0] # 得到用户所有信息的数据
                        uid=result[0] # 数据库独立id
                        fb_userid=result[1] # fanbook中的userid
                        fb_username=result[2] # fanbookid
                        fb_nickname=result[3] # 昵称
                        fb_toady=result[4] # 上一次打卡时间
                        fb_total=result[5] # 累计打卡次数
                        fb_money=result[6] # 累计余额
                        date_today = datetime.strptime(fb_toady, "%Y%m%d").date() # 将上一次打卡时间解析为可读类型
                        current_date = date.today() # 获得今日时间
                        img_pay=result[7] # 支付码
                        if img_pay!=None: # 上传了支付码
                            if float(DOOR)<float(fb_money): # 达到了提现门槛
                                print("已经提交收款码") # 信息
                                # 获得管理员的私聊频道用户发送批准信息
                                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/getPrivateChat"  
                                headers = {'content-type': "application/json;charset=utf-8"}
                                jsonfile = json.dumps({
                                    "user_id":int(ADMIN)
                                }) 
                                postreturn = requests.post(url, data=jsonfile, headers=headers)
                                postreturn=json.loads(postreturn.text) # 解析接口返回
                                private_id=postreturn["result"]["id"] # 获得私聊频道ID
                                # 发送管理员批准信息
                                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage" 
                                headers = {'content-type': "application/json;charset=utf-8"}
                                jsonfile = json.dumps({
                                    "chat_id": int(private_id),
                                    "text": "{\"notification\":\"提现申请\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"ffd8d8\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"管理面板 | 银行系统 - 提现\\\",\\\"style\\\":{\\\"color\\\":\\\"#ff0000\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"${@!"+str(fb_userid)+"}用户申请提现\\\\n\\\\n---------\\\\n\\\\n金额："+str(fb_money)+"\\\\n\\\\n卡号："+str(uid)+"\\\"}}]}\",\"come_from_name\":\"—— DevOpen 官方团队提供支持\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                                    "parse_mode": "Fanbook",
                                    "reply_markup": {
                                        "inline_keyboard": [
                                            [
                                                {
                                                    "text": "提现完成",
                                                    "callback_data": "{\"come_from\":\"devopen_admin_money_t\",\"user_id\":\""+str(fb_userid)+"\",\"fanbook_id\":\""+str(fb_username)+"\",\"money\":\""+str(fb_money)+"\"}"
                                                },{
                                                    "text": "拒绝提现",
                                                    "callback_data": "{\"come_from\":\"devopen_admin_money_f\",\"user_id\":\""+str(fb_userid)+"\",\"fanbook_id\":\""+str(fb_username)+"\",\"money\":\""+str(fb_money)+"\"}"
                                                }
                                            ]

                                        ]
                                    }
                                })  
                                postreturn = requests.post(url, data=jsonfile, headers=headers)
                                # 发送频道通知用户
                                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage" 
                                headers = {'content-type': "application/json;charset=utf-8"}
                                jsonfile = json.dumps({
                                    "chat_id": int(PLAY_CHAT),
                                    "text": "{\"notification\":\"签到打卡机器人\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"ffffd9\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"打卡签到 | 银行系统 - 申请提交\\\",\\\"style\\\":{\\\"color\\\":\\\"#ffc55a\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"💰在线小银行💰\\\\n\\\\n----------\\\\n\\\\n💳银行卡号："+str(uid)+"\\\\n\\\\n提现申请已经提交至管理员，请等待管理员批准即可到账！（未到账不扣除余额）\\\"}}]}\",\"come_from_name\":\"—— DevOpen 官方\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                                    "parse_mode": "Fanbook"
                                })  
                                postreturn = requests.post(url, data=jsonfile, headers=headers)
                            else: # 没有达到提现门槛
                                # 发送频道通知
                                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage" 
                                headers = {'content-type': "application/json;charset=utf-8"}
                                jsonfile = json.dumps({
                                    "chat_id": int(PLAY_CHAT),
                                    "text": "{\"notification\":\"签到打卡机器人\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"ffd8d8\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"打卡签到 | 银行系统 - 门槛\\\",\\\"style\\\":{\\\"color\\\":\\\"#ff0000\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"**提现门槛为："+str(DOOR)+"元，当前余额："+str(fb_money)+"**\\\\n\\\\n----------\\\\n\\\\n多积攒几天再来吧！\\\"}}]}\",\"come_from_name\":\"—— DevOpen 官方团队提供支持\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                                    "parse_mode": "Fanbook"
                                })  
                                postreturn = requests.post(url, data=jsonfile, headers=headers)
                        else: # 用户没有上传支付码
                            print("无法验证收款码") # 信息
                            # 发送频道通知
                            url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage" 
                            headers = {'content-type': "application/json;charset=utf-8"}
                            jsonfile = json.dumps({
                                "chat_id": int(PLAY_CHAT),
                                "text": "{\"notification\":\"签到打卡机器人\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"ffd8d8\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"打卡签到 | 银行系统 - 未绑定\\\",\\\"style\\\":{\\\"color\\\":\\\"#ff0000\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"**该功能需要绑定微信收款码后才可使用。**\\\\n\\\\n----------\\\\n\\\\n请联系管理员人工协助绑定！\\\"}}]}\",\"come_from_name\":\"—— DevOpen 官方团队提供支持\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                                "parse_mode": "Fanbook"
                            })  
                            postreturn = requests.post(url, data=jsonfile, headers=headers)
                            # 注：当前版本不支持在线上传支付码
            elif data["come_from"]=="devopen_admin_money_t": # 同意用户提现申请
                user_id=data["user_id"] # 用户Fanbook UserID
                money=data["money"] # 用户申请提现的余额
                # 更新数据库数据
                conn = mysql.connector.connect(user=DB_USER, password=DB_PWD,
                                                   host='127.0.0.1', database=DB_NAME)
                cursor = conn.cursor()
                query = ('SELECT * FROM `'+TABLE_NAME+'` WHERE FanbookUserId = %s')
                values = (user_id,)
                cursor.execute(query, values)
                result = cursor.fetchall()
                # 关闭数据库连接
                cursor.close()
                conn.close()

                result=result[0] # 得到用户所有信息的数据
                uid=result[0] # 数据库独立id
                fb_userid=result[1] # fanbook中的userid
                fb_username=result[2] # fanbookid
                fb_nickname=result[3] # 昵称
                fb_toady=result[4] # 上一次打卡时间
                fb_total=result[5] # 累计打卡次数
                fb_money=result[6] # 累计余额
                img_pay=result[7] # 支付码
                print("剩余",fb_money)
                print("提现",money)
                fb_money=float(fb_money)-float(money) # 设置提现后余额
                # 更新数据库内容
                conn = mysql.connector.connect(
                    user=DB_USER,
                    password=DB_PWD,
                    host='127.0.0.1',
                    database=DB_NAME
                )
                cursor = conn.cursor()

                update_query = f"UPDATE `"+TABLE_NAME+"` SET money = " + str(fb_money) + " WHERE FanbookUserId = " + str(
                    user_id) + ""
                cursor.execute(update_query)
                conn.commit()
                # 验证/获取当前用户信息
                conn = mysql.connector.connect(user=DB_USER, password=DB_PWD,
                                                   host='127.0.0.1', database=DB_NAME)
                cursor = conn.cursor()
                query = ('SELECT * FROM `'+TABLE_NAME+'` WHERE FanbookUserId = %s')
                values = (user_id,)
                cursor.execute(query, values)
                result = cursor.fetchall()
                # 关闭数据库连接
                cursor.close()
                conn.close()

                result=result[0] # 得到用户所有信息的数据
                uid=result[0] # 数据库独立id
                fb_userid=result[1] # fanbook中的userid
                fb_username=result[2] # fanbookid
                fb_nickname=result[3] # 昵称
                fb_toady=result[4] # 上一次打卡时间
                fb_total=result[5] # 累计打卡次数
                fb_money=result[6] # 累计余额
                img_pay=result[7] # 支付码
                # 获得管理员私聊频道
                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/getPrivateChat"  # 注意令牌
                headers = {'content-type': "application/json;charset=utf-8"}
                jsonfile = json.dumps({
                    "user_id":int(ADMIN)
                })  
                postreturn = requests.post(url, data=jsonfile, headers=headers)
                postreturn=json.loads(postreturn.text) # 解析接口返回数据
                private_id=postreturn["result"]["id"] # 获得私聊频道
                # 发送批准通知
                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage" 
                headers = {'content-type': "application/json;charset=utf-8"}
                jsonfile = json.dumps({
                    "chat_id": int(private_id),
                    "text": "{\"notification\":\"提现批准\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"ffd8d8\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"管理面板 | 银行系统 - 批准\\\",\\\"style\\\":{\\\"color\\\":\\\"#ff0000\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"${@!"+str(user_id)+"}\\\\n\\\\n---------\\\\n\\\\n卡余额："+str(fb_money)+"\\\\n\\\\n申请余额："+str(money)+"\\\"}}]}\",\"come_from_name\":\"—— DevOpen 官方团队提供支持\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                    "parse_mode": "Fanbook",
                })  
                postreturn = requests.post(url, data=jsonfile, headers=headers)
                # 获取申请提现用户私聊频道
                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/getPrivateChat"  # 注意令牌
                headers = {'content-type': "application/json;charset=utf-8"}
                jsonfile = json.dumps({
                    "user_id":int(user_id)
                })
                postreturn = requests.post(url, data=jsonfile, headers=headers)
                postreturn=json.loads(postreturn.text) # 解析接口返回数据
                private_id=postreturn["result"]["id"] # 获得私聊频道
                # 通知用户余额到账
                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage" 
                headers = {'content-type': "application/json;charset=utf-8"}
                jsonfile = json.dumps({
                    "chat_id": int(private_id),
                    "text": "{\"notification\":\"提现成功\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"ffffd9\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"打卡签到 | 银行系统 - 批准\\\",\\\"style\\\":{\\\"color\\\":\\\"#ffc55a\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"💰在线小银行💰\\\\n\\\\n----------\\\\n\\\\n请您到微信余额里查看。\\\"}}]}\",\"come_from_name\":\"—— DevOpen 官方\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                    "parse_mode": "Fanbook"
                })  
                postreturn = requests.post(url, data=jsonfile, headers=headers)
            elif data["come_from"]=="devopen_admin_money_f": # 拒绝用户提现申请
                user_id=data["user_id"] # 用户Fanbook UserID
                money=data["money"] # 用户申请提现的余额
                # 获得管理员私聊频道
                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/getPrivateChat"  # 注意令牌
                headers = {'content-type': "application/json;charset=utf-8"}
                jsonfile = json.dumps({
                    "user_id":int(ADMIN)
                }) 
                postreturn = requests.post(url, data=jsonfile, headers=headers)
                postreturn=json.loads(postreturn.text) # 解析接口返回数据
                private_id=postreturn["result"]["id"] # 获得私聊频道
                # 发送拒绝通知
                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage" 
                headers = {'content-type': "application/json;charset=utf-8"}
                jsonfile = json.dumps({
                    "chat_id": int(private_id),
                    "text": "{\"notification\":\"提现拒绝\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"ffd8d8\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"管理面板 | 银行系统 - 拒绝\\\",\\\"style\\\":{\\\"color\\\":\\\"#ff0000\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"${@!"+str(user_id)+"}\\\\n\\\\n---------\\\\n\\\\n申请余额："+str(money)+"\\\\n\\\\n------\\\\n\\\\n已拒绝。\\\"}}]}\",\"come_from_name\":\"—— DevOpen 官方团队提供支持\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                    "parse_mode": "Fanbook",
                    
                })  
                postreturn = requests.post(url, data=jsonfile, headers=headers)
                # 通知用户管理员拒绝提现
                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/getPrivateChat"  # 注意令牌
                headers = {'content-type': "application/json;charset=utf-8"}
                jsonfile = json.dumps({
                    "user_id":int(user_id)
                }) 
                postreturn = requests.post(url, data=jsonfile, headers=headers)
                postreturn=json.loads(postreturn.text)
                private_id=postreturn["result"]["id"]
                url = "https://a1.fanbook.mobi/api/bot/" + TOKEN + "/sendMessage" 
                headers = {'content-type': "application/json;charset=utf-8"}
                jsonfile = json.dumps({
                    "chat_id": int(private_id),
                    "text": "{\"notification\":\"提现失败\",\"data\":\"{\\\"tag\\\":\\\"column\\\",\\\"children\\\":[{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12,8,12,8\\\",\\\"width\\\":1024,\\\"backgroundColor\\\":\\\"ffffd9\\\",\\\"child\\\":{\\\"tag\\\":\\\"text\\\",\\\"data\\\":\\\"打卡签到 | 银行系统 - 拒绝\\\",\\\"style\\\":{\\\"color\\\":\\\"#ffc55a\\\",\\\"fontSize\\\":16,\\\"fontWeight\\\":\\\"medium\\\"}}},{\\\"tag\\\":\\\"container\\\",\\\"padding\\\":\\\"12\\\",\\\"width\\\":1024,\\\"child\\\":{\\\"tag\\\":\\\"markdown\\\",\\\"overflow\\\":\\\"clip\\\",\\\"textAlign\\\":\\\"left\\\",\\\"style\\\":{\\\"fontSize\\\":15,\\\"color\\\":\\\"#1F2329\\\"},\\\"data\\\":\\\"💰在线小银行💰\\\\n\\\\n----------\\\\n\\\\n管理员拒绝了你的提现请求。余额不会变更。可能原因：收款方式不正确、账户异常。请联系管理员（${@!"+str(ADMIN)+"}）咨询详情。\\\"}}]}\",\"come_from_name\":\"—— DevOpen 官方\",\"type\":\"messageCard\",\"come_from_icon\":\"111\"}",
                    "parse_mode": "Fanbook"
                })  
                postreturn = requests.post(url, data=jsonfile, headers=headers)
                
        except Exception as e:
            # 为了防止接受其他机器人的信息导致失败，直接忽略
            traceback.print_exc() # 打印完整的错误数据
                
def send_ping(ws):
    while True:
        time.sleep(20)
        ws.send('{"type":"ping"}')

def get_me():
    response = requests.get(f"{BASE_URL}/bot/{TOKEN}/getMe", timeout=3)
    return response.json()

def handleWS(user_token):
    version = '1.6.60'
    device_id = f'bot{BOT_ID}'
    header_map = json.dumps({
        "device_id": device_id,
        "version": version,
        "platform": "bot",
        "channel": "office",
        "build_number": "1"
    })
    super_str = base64.b64encode(header_map.encode('utf8')).decode('utf8')
    addr = f'wss://gateway-bot.fanbook.mobi/websocket?id={user_token}&dId={device_id}&v={version}&x-super-properties={super_str}'
    ws = create_connection(addr)

    ping_thread = threading.Thread(target=send_ping, args=(ws,))
    ping_thread.daemon = True
    ping_thread.start()
    try:
        while True:
            evt_data = ws.recv()
            on_message(evt_data)
    except WebSocketConnectionClosedException:
        print("WebSocketClosed")
   


if __name__ == '__main__':
    res = get_me()
    user_token = res["result"]['user_token']
    handleWS(user_token)