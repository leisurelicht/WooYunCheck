#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import sys 
import json
import smtplib  
from email.mime.text import MIMEText  
from email.header import Header
import time
import os

reload(sys)
sys.setdefaultencoding('utf8')

wooyun_url = 'http://api.wooyun.org/bugs/submit'

class WooYun(object):
    """docstring for WooYun"""

    def __init__(self,keyfile,check_url,name,mailpassword):
        super(WooYun, self).__init__()
        self.name = name 
        self.check_url = check_url
        self.keyfile = keyfile
        self.keyWordslist = []
        self.errorId = [0]
        self.keyWordsread(keyfile)
        self.mailpassword = mailpassword
        self.count = 0
        for id in open('ErrorId.txt','r'):
            self.errorId.append(id.strip())
        print self.errorId

    def __del__(self):
        print self.name,"is over"


    def keyWordsread(self,keyfile):
        if os.path.exists(keyfile):
            for key in open (keyfile,'r'):
                newKey =  key.strip()   
                self.keyWordslist.append(newKey)


    def dataRequest(self):
        print self.name,"is start dataRequest in",self.count
        try:
            text = requests.get(self.check_url).content
            #raise Exception("connect error")
        except (requests.exceptions.ConnectionError,Exception) as e :
                #print e
                text = "Error in function : \" %s \" ,\nError name is : \" %s \" ,\nError type is : \" %s \" ,\nError Message is : \" %s \" ,\nError doc is : \" %s \" \n" % (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
                print text
                self.mailInit('Program exception',text,'exceptionInfo')
                time.sleep(5)
        else:
            #data = json.loads(text) 
            self.keyWordsckeck(text)

    def keyWordsckeck(self,text):
        print self.name,"is start keyWordsckeck in",self.count

        try :
            #raise Exception("data is not json")
            data = json.loads(text)
        except Exception as e :
            #print e 
            text = "Error in function : \" %s \" ,\nError name is : \" %s \" ,\nError type is : \" %s \" ,\nError Message is : \" %s \" ,\nError doc is : \" %s \" \n" % (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
            print text
            self.mailInit('Program exception',text,'exceptionInfo')
        else : 
            for i in range(0,10):
                temp_name = data[i].get('title')
                temp_url = data[i].get('link')
                temp_id = data[i].get('id')
                #print temp_name
                for Key in self.keyWordslist:
                    #print Key,"===",
                    #print temp_name.find(Key)
                    if ( temp_name.find(Key) != -1 ):
                        #print "ready send"
                        self.sendRecord(temp_name,temp_url,temp_id)
                        break
        self.count += 1

    def sendRecord(self,title,url,id):
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
                #raise Exception("Mail send error")
            except Exception as e :
                #print e
                text = "Error in function : \" %s \" ,\nError name is : \" %s \" ,\nError type is : \" %s \" ,\nError Message is : \" %s \" ,\nError doc is : \" %s \" \n" % (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
                print text
            else :
                self.errorId.append(id)
                tmp = open('ErrorId.txt','a')
                tmp.write(id+'\n')
                tmp.close()
            time.sleep(1)
        else:
            print "Same thing was sent,did not send same mail to everyone"

    def mailInit(self,title,message,type):
        print self.name,"is start mailInit in",self.count

        sender = '3118706739@qq.com'  #发件人
        receiver = ['leisurelylicht@126.com','zhao_haixu@venustech.com.cn','liuchang@venustech.com.cn','zhang_dejun@venustech.com.cn'] #收件人
        receiver_admin = 'leisurelylicht@126.com'
        subject = title  #邮件标题
        smtpserver = 'smtp.qq.com'  #邮件服务器
        username = '3118706739@qq.com'  #邮箱登录名
        password = self.mailpassword  #邮箱登陆密码
        param = {'sender':sender,'receiver':receiver,'subject':subject,'smtpserver':smtpserver,'username':username,'password':password,'receiver_admin':receiver_admin}
        if (type == "securityInfo"):
            self.sendSecurity(message,param)
        elif (type == "timereport"):
            self.sendConnectreport()
        else:
            self.sendException(message,param)

    def sendSecurity(self,url,param):
        print self.name,"is start sendSecurity in",self.count

        msg = MIMEText(url,'text')#中文参数‘utf-8’，单字节字符不需要 
        #msg = MIMEText('hello wold','text') 
        msg['Subject'] = Header(param['subject'])  
  
        try:
            smtp = smtplib.SMTP()  
            smtp.connect(param['smtpserver'])  
            smtp.login(param['username'],param['password'])  
            smtp.sendmail(param['sender'],param['receiver'],msg.as_string())
        except Exception as e :
            text = "Error in function : \" %s \" ,\nError name is : \" %s \" ,\nError type is : \" %s \" ,\nError Message is : \" %s \" ,\nError doc is : \" %s \" \n" % (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
            print text
            #self.mailInit('Program exception',text,'exceptionInfo')
        finally:
            smtp.quit()

    def sendException(self,errorinfo,param):
        print self.name,"is start sendException"

        msg = MIMEText(errorinfo,'text')#中文参数‘utf-8’，单字节字符不需要 
        #msg = MIMEText('hello wold','text') 
        msg['Subject'] = Header(param['subject'])  
        try:
            smtp = smtplib.SMTP()  
            smtp.connect(param['smtpserver'])  
            smtp.login(param['username'],param['password'])  
            smtp.sendmail(param['sender'],param['receiver_admin'],msg.as_string())
        except Exception as e :
            text = "Error in function : \" %s \" ,\nError name is : \" %s \" ,\nError type is : \" %s \" ,\nError Message is : \" %s \" ,\nError doc is : \" %s \" \n" % (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
            print text
            #self.mailInit('Program exception',text,'exceptionInfo')
        finally:
            smtp.quit()
        
def sendConnectreport(mailpassword):
    sender = '3118706739@qq.com'  #发件人print "Scheduled connections is"
    receiver_admin = 'leisurelylicht@126.com'
    #subject = "程序正常运行中......"  #邮件标题
    smtpserver = 'smtp.qq.com'  #邮件服务器
    username = '3118706739@qq.com'  #邮箱登录名
    password = mailpassword
    #msg = MIMEText(url,'text')#中文参数‘utf-8’，单字节字符不需要 
    msg = MIMEText('程序正常运行中......','text','utf-8') 
    msg['Subject'] = Header('Program is running......')  
  
    try:
        smtp = smtplib.SMTP()  
        smtp.connect(smtpserver)  
        smtp.login(username,password)  
        smtp.sendmail(sender,receiver_admin,msg.as_string())
    except Exception as e :
        text = "Error in function : \" %s \" ,\nError name is : \" %s \" ,\nError type is : \" %s \" ,\nError Message is : \" %s \" ,\nError doc is : \" %s \" \n" % (sys._getframe().f_code.co_name,e.__class__.__name__,e.__class__,e,e.__class__.__doc__)
        print text
        #self.mailInit('Program exception',text,'exceptionInfo')
    finally:
        smtp.quit()

if __name__ == '__main__':
    count = 0
    one = time.time() #开始时间
    mailpassword = sys.argv[1]
    #mailpassword = ""
    Guoziwei = WooYun('Guoziwei.txt',wooyun_url,'国资委',mailpassword)
    Baojianhui = WooYun('Baojianhui.txt', wooyun_url,'保监会',mailpassword)
    jijin = WooYun('jijin.txt',wooyun_url,'基金',mailpassword)
    while True:
        print "system is running in [",count,"],now is",time.ctime() 
        two = time.time() #当前时间
        if ( two - one ) > 43200:
            sendConnectreport(mailpassword)
            one = two
            print "Scheduled connections was sent"
        Guoziwei.dataRequest()
        Baojianhui.dataRequest()
        jijin.dataRequest()
        print "This cycle [",count,"] was end in",time.ctime()
        count += 1
        time.sleep(300)
 
    








