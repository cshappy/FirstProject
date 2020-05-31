import tornado.web
import tornado.ioloop
import time
import datetime
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError

from email import encoders
from email.utils import parseaddr, formataddr

#coding:utf8
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText


#定义处理类型
class SendCode(tornado.web.RequestHandler):
    def get(self):
        pnumber = self.get_query_argument("phonenumber")

        mail_info = {
            "from": "notice@sh.sealu.net",
            "to": "m18260356559@163.com",
            "hostname": "smtp.exmail.qq.com",
            "username": "notice@sh.sealu.net",
            "password": "Dec2018",
            "mail_subject": "新注册用户的手机号",
            "mail_text": "%s"%pnumber,
            "mail_encoding": "utf-8"
        }

        if __name__ == '__main__':
            #这里使用SMTP_SSL就是默认使用465端口
            smtp = SMTP_SSL(mail_info["hostname"])
            smtp.set_debuglevel(1)
            
            smtp.ehlo(mail_info["hostname"])
            smtp.login(mail_info["username"], mail_info["password"])

            msg = MIMEText(mail_info["mail_text"], "plain", mail_info["mail_encoding"])
            msg["Subject"] = Header(mail_info["mail_subject"], mail_info["mail_encoding"])
            msg["from"] = mail_info["from"]
            msg["to"] = mail_info["to"]
            
            smtp.sendmail(mail_info["from"], mail_info["to"], msg.as_string())

            smtp.quit()

        t       = time.time()
        #取时间戳4位作为验证码
        code    = int((t*1000000)%10000)
        params  = [str(code),"60"] #验证码，有效时间
        result  = ssender.send_with_param(86, pnumber,template_id, params, extend="", ext="") #发送短信
        codes[pnumber]=code #将验证码加入到codes中
        expir[pnumber]=t+3600*24 #验证码的失效时间是当前时间加一天
        #TODO记录验证过的手机号
class Download(tornado.web.RequestHandler):
    def get(self):
        pnumber  = self.get_query_argument("phonenumber")
        
        code     = int(self.get_query_argument("code"))
        filepath = self.get_query_argument("file")
        if expir.get(pnumber,0) > time.time() and codes.get(pnumber,0) == code:
            self.add_header('Content-type','application/octet-stream')
            self.add_header('Content-Disposition','attachment;filename='+filepath) #防止浏览器直接打开
            self.add_header('X-Accel-Redirect', '/file/'+filepath) #nginx sendfile功能
        else:
            self.write("手机号码未验证或者验证码已过期，请重新验证，谢谢")
if __name__ == '__main__':
    codes   = {'SEALU':999999} #SEALU是万能账号，CODE是999999
    expir   = {'SEALU':2000000000}
    #腾讯云短信发送基本信息
    appid   = 1400139346
    appkey  = "c669a6c9534350ba2607a1a509b55254"
    ssender = SmsSingleSender(appid, appkey)
    template_id = 194147
    #创建一个应用对象
    app = tornado.web.Application(
        [
            (r"/sendcode", SendCode),
            (r"/download", Download),
        ]
    )
    #绑定一个监听端口
    app.listen(60084)
    #启动web程序，开始监听端口的连接
    tornado.ioloop.IOLoop.current().start()