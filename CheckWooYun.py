#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import os
import sys
import time
import json
import smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr , formataddr
from ConfigParser import ConfigParser


reload(sys)
sys.setdefaultencoding('utf8')

wooyun_url = 'http://api.wooyun.org/bugs/submit'

class WooYun(object):
    """docstring for WooYun"""

    def __init__(self,name,mailpassword,keyfile='',check_url=''):
        '''
        '''
        super(WooYun, self).__init__()
        self.name = name
        self.check_url = check_url
        self.keyfile = keyfile
        self.keyWordslist = []
        self.errorId = [0]
        self.keyWordsread(keyfile)
        self.errorIdread('ErrorId.txt')
        self.mailpassword = mailpassword
        self.count = 0
        self.website = ' from WooYun'
        try:
            self.config = ConfigParser()
            self.config.read("config.ini")
        except Exception as e :
            print e
            exit(0)

    def __del__(self):
        print self.name,"is over"

    def errorIdread(self,errorIdfile):
        '''
        从文件中读取已经发送过邮件的事件ID
        '''
        if os.path.exists(errorIdfile):
            with open(errorIdfile) as errors:
                for error in errors:
                   self.errorId.append(error.strip())

    def keyWordsread(self,keyfile):
        '''
        从文件中读取需要监看的关键字
        '''
        if os.path.exists(keyfile):
            for key in open (keyfile,'r'):
                newKey =  key.strip()
                self.keyWordslist.append(newKey)

    def dataRequest(self):
        '''
            从乌云API获取json格式数据
        '''
        print self.name,"is start dataRequest in",self.count
        try:
            #text = requests.get(self.check_url).content
            raise Exception("connect error")
        except (requests.exceptions.ConnectionError,Exception) as e :
                #print e
                text = "Error in function : \" %s \" ,\n \
                Error name is : \" %s \" ,\n \
                Error type is : \" %s \" ,\n \
                Error Message is : \" %s \" ,\n \
                Error doc is : \" %s \" \n" % \
                (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
                print text
                self.mailInit('Program exception',text,'exceptionInfo')
        else:
            #data = json.loads(text)
            self.keyWordscheck(text)

    def keyWordscheck(self,text):
        '''
        检查获得的标题中是否含有要监看的关键字
        '''
        print self.name,"is start keyWordscheck in",self.count

        try :
            #raise Exception("data is not json")
            data = json.loads(text)
        except Exception as e :
            text = "Error in function : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" \n" % \
            (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
            print text
            self.mailInit('Program exception',text,'exceptionInfo')
        else :
            for i in range(0,10):
                temp_name = data[i].get('title')
                temp_url = data[i].get('link')
                temp_id = data[i].get('id')
                for Key in self.keyWordslist:
                    if ( temp_name.find(Key) != -1 ):
                        self.sendRecord(temp_name+self.website,temp_url,temp_id)
                        break
        self.count += 1


    def sendRecord(self,title,url,id):
        '''
        调用邮件初始化函数并记录被发送的事件ID
        '''
        print self.name,"is start sendRecord in",self.count

        temp = []
        if (len(self.errorId) > 0):
            for i in self.errorId:
                temp.append(cmp(i, id))

        if 0 not in temp:
            print "now is",time.ctime(),",",self.name,"to send email to everyone in",self.count
            try:
                #pass #test to use this
                self.mailInit(title,url,'securityInfo')
                #raise Exception("Mail send error") //test
            except Exception as e :
                #print e
                text = "Error in function : \" %s \" ,\n \
                Error name is : \" %s \" ,\n \
                Error type is : \" %s \" ,\n \
                Error Message is : \" %s \" ,\n \
                Error doc is : \" %s \" \n" % \
                (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
                print text
            else :
                self.errorId.append(id)
                tmp = open('ErrorId.txt','a')
                tmp.write(id+'\n')
                tmp.close()
            time.sleep(1)
        else:
            print "Same thing was sent,did not send same mail to everyone"

    def mailInit(self,title,message,messagetype):
        '''
        初始化邮件设置
        title: 邮件标题
        message: 邮件正文,在不同类型的邮件中内容不同
        messagetype有三个值:
        securityinfo: 发送监看事件时调用
        exceptionInfo: 发送错误报告时调用
        timereport: 发动定时运行报告时调用
        '''
        print self.name,"is start mailInit in",self.count

        sender = self.config.get( 'mail' , 'sendermail' )  #发件人
        receiver = self.config.get('mail','receivermail') #收件人
        #receiver =  config.get('mail','receivermail_test') #测试
        receiver_admin = self.config.get('mail','receivermail_admin')
        smtpserver = self.config.get('mail','smtpserver')  #邮件服务器
        username = self.config.get('mail','mailname')  #邮箱登录名
        password = self.mailpassword   #邮箱登陆密码
        param = {'sender':sender,'receiver':receiver,\
        'subject':title+self.website,'smtpserver':smtpserver,\
        'username':username,'password':password,\
        'receiver_admin':receiver_admin}

        self.sendEmail(message,param,messagetype)

    def sendEmail(self,message,param,messagetype):
        '''
        发送邮件
        '''
        print self.name,"is start sendEmail in",self.count

        msg = MIMEText(message,'plain','utf-8')#中文参数‘utf-8’，单字节字符不需要
        #msg = MIMEText('hello wold','text')
        msg['Subject'] = Header(param['subject'])

        try:
            smtp = smtplib.SMTP( param['smtpserver'] , 25 )
            #smtp.connect(param['smtpserver'])
            #smtp.set_debuglevel(1)
            smtp.login(param['username'],param['password'])
            if (messagetype == "securityinfo"):
                smtp.sendmail(param['sender'],param['receiver'],msg.as_string())
            else:
                smtp.sendmail(param['sender'],param['receiver_admin'],msg.as_string())

        except Exception as e :
            text = "Error in function : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" \n" % \
            (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
            print text
            #self.mailInit('Program exception',text,'exceptionInfo')
        else:
            smtp.quit()

if __name__ == '__main__':
    count = 0
    one = time.time() #开始时间

    #mailpassword = sys.argv[1]
    mailpassword = "d6432408j6431646"

    Guoziwei = WooYun('WooYun国资委',mailpassword,'Guoziwei.txt',wooyun_url)
    Baojianhui = WooYun('WooYun保监会',mailpassword,'Baojianhui.txt', wooyun_url)
    jijin = WooYun('WooYun基金',mailpassword,'jijin.txt',wooyun_url)
    yinhang = WooYun('WooYun银行',mailpassword,'yinhang.txt',wooyun_url)

    timereport = WooYun('WooYun运行报告',mailpassword)
    timereport.mailInit('running report','program start running',"timereport")

    while True:
        print "system is running in [",count,"],now is",time.ctime()
        two = time.time() #当前时间
        if ( two - one ) > 10:
            timereport.mailInit('running report from WooYun','program is running',"timereport")
            one = two
            print "Scheduled connections was sent"

        Guoziwei.dataRequest()
        #Baojianhui.dataRequest()
        #jijin.dataRequest()
        #yinhang.dataRequest()
        print "This cycle [",count,"] was end in",time.ctime()
        count += 1
        time.sleep(5)
