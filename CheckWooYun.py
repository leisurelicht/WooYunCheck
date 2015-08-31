#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import os
import sys
import time
import json
import hashlib
import smtplib
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
        self.mailpassword = mailpassword
        self.keyfile = keyfile
        self.check_url = check_url
        self.keyWordslist = []
        self.errorId = [0]
        self.count = 0
        self.fileCheck = 0
        self.website = ' from WooYun'

        self.keyWordsread(self.keyfile)
        self.errorIdread('ErrorId.txt')
        self.fileMd5check(self.keyfile)
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

    def fileMd5check(self,keyfile):
        '''
        检查文件的MD5值,确定文件是否发生改变
        没有发生改变返回 'not'
        发生改变返回 'change'
        '''
        filemd5 = hashlib.md5()
        if ( self.fileCheck == 0 ):
            with open(keyfile) as filetemp:
                filemd5.update(filetemp.read())
                self.fileCheck = filemd5.hexdigest()
                return 'not'
        else:
            with open(keyfile) as filetemp:
                filemd5.update(filetemp.read())
                md5temp = filemd5.hexdigest()
                if ( self.fileCheck != md5temp ):
                    self.fileCheck = md5temp
                    return 'change'

    def keyWordsread(self,keyfile):
        '''
        从文件中读取需要监看的关键字
        没有返回值
        '''
        self.keyWordslist = []
        if os.path.exists(keyfile):
            with open(keyfile) as keys:
                for key in keys:
                        self.keyWordslist.append(key.strip())


    def dataRequest(self):
        '''
            从乌云API获取json格式数据
            返回json格式的数据
        '''
        print self.name,"is start dataRequest in",self.count
        try:
            text = requests.get(self.check_url).content
            #raise Exception("connect error")
        except (requests.exceptions.ConnectionError,Exception) as e :

                text = "Error in function : \" %s \" ,\n \
                Error name is : \" %s \" ,\n \
                Error type is : \" %s \" ,\n \
                Error Message is : \" %s \" ,\n \
                Error doc is : \" %s \" \n" % \
                (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
                print text
                self.mailInit('Program exception',text,'exceptionInfo')
        else:
            return text

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
            flag = self.fileMd5check(self.keyfile)
            if ( flag == 'change'):
                self.keyWordsread(self.keyfile)
            #print self.keyWordslist
            for i in range(0,10):
                temp_name = data[i].get('title')
                temp_url = data[i].get('link')
                temp_id = data[i].get('id')
                for Key in self.keyWordslist:
                    if ( temp_name.find(Key) != -1 ):
                        self.sendRecord(temp_name,temp_url,temp_id)
                        break
        self.count += 1


    def sendRecord(self,title,url,id):
        '''
        调用邮件初始化函数并记录被发送的事件ID
        没有返回值
        函数内调用mailInit()
        '''
        print self.name,"is start sendRecord in",self.count

        temp = []
        if (len(self.errorId) > 0):
            for i in self.errorId:
                temp.append(cmp(i, id))

        if 0 not in temp:
            print "now is",time.ctime(),",",self.name,"to send email ",title," to everyone in",self.count
            try:
                #pass #test to use this
                self.mailInit(title+self.website,url,'securityInfo')
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
            print title," Same thing was sent,did not send same mail to everyone"

    def mailInit(self,title,message,messagetype):
        '''
        初始化邮件设置
        title: 邮件标题
        message: 邮件正文,在不同类型的邮件中内容不同
        messagetype有三个值:
        securityinfo: 发送监看事件时调用
        exceptionInfo: 发送错误报告时调用
        timereport: 发动定时运行报告时调用
        没有返回值
        函数内调用sendEmail()
        '''
        print self.name,"is start mailInit in",self.count

        sender = self.config.get( 'mail' , 'sendermail' )  #发件人
        receiver = self.config.get('mail','receivermail').split(',') #收件人
        receiver_admin = self.config.get('mail','receivermail_admin').split(',')
        smtpserver = self.config.get('mail','smtpserver')  #邮件服务器
        username = self.config.get('mail','mailname')  #邮箱登录名
        password = self.mailpassword   #邮箱登陆密码
        param = {'sender':sender,'receiver':receiver,\
        'subject':title,'smtpserver':smtpserver,\
        'username':username,'password':password,\
        'receiver_admin':receiver_admin}

        self.sendEmail(message,param,messagetype)

    def sendEmail(self,message,param,messagetype):
        '''
        发送邮件
        没有返回值
        函数内调用_format_addr()
        '''
        print self.name,"is start sendEmail in",self.count

        msg = MIMEText(message,'plain','utf-8')#中文参数‘utf-8’，单字节字符不需要
        msg[ 'From' ] = self._format_addr( u'WooYun监看机器人<%s>' % param['sender'] )
        msg[ 'Subject' ] = Header( param['subject'] )

        try:
            smtp = smtplib.SMTP( param['smtpserver'] , 25 )
            #smtp = smtplib.SMTP()
            #smtp.connect(param['smtpserver'])
            #smtp.set_debuglevel(1)
            smtp.login(param['username'],param['password'])
            if (messagetype == "securityInfo"):
                msg[ 'To' ] = self._format_addr(u'Dollars<%s>' % param['receiver'] )
                smtp.sendmail(param['sender'],param['receiver'],msg.as_string())
            else:
                msg[ 'To' ] = self._format_addr(u'Admin<%s>' % param['receiver_admin'] )
                smtp.sendmail(param['sender'],param['receiver_admin'],msg.as_string())

        except Exception as e :
            text = "Error in function : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" \n" % \
            (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
            print text
        else:
            smtp.quit()

    def _format_addr(self,s):
        '''
        格式化一个邮件地址
        返回一个被格式化为 '别名<email address>' 的邮件地址
        '''
        name , addr = parseaddr(s)
        return formataddr(( Header(name,'utf-8').encode(),\
                          addr.encode('utf-8') if isinstance(addr,unicode) else addr ))

if __name__ == '__main__':
    count = 0
    one = time.time() #开始时间

    mailpassword = sys.argv[1]
    #mailpassword = ""
    #mailpassword = raw_input("Please input mail password:")

    robot = WooYun('WooYun机器人',mailpassword,'KeyWords.txt',wooyun_url)


    timereport = WooYun('WooYun运行报告',mailpassword,'KeyWords.txt')
    timereport.mailInit('Running report','Program start running',"timereport")

    while True:
        print "WooYun robot system is running in [",count,"],now is",time.ctime()
        two = time.time() #当前时间
        if ( two - one ) > 43200:
            timereport.mailInit('Running report','Program is running',"timereport")
            one = two
            print "Scheduled connections was sent"

        data = robot.dataRequest()
        robot.keyWordscheck(data)

        print "WooYun robot : This cycle [",count,"] was end in",time.ctime()
        count += 1
        time.sleep(600)
