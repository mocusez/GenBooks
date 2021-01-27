from email.utils import COMMASPACE, formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
import os,smtplib,sys,pytz,time,logging,threading,subprocess,json,requests,shutil,_thread,processRss
logging.basicConfig(level=logging.INFO)

config = os.environ.get("config",'''
{
    "title":"你的推送名字",
    "feeds": [
        {"name":"知乎热榜","url":"https://rsshub.xsnet.top/zhihu/hotlist","saveimg":true,"imgquality":20,"css":"img.avatar,a.originUrl,div.view-more{display:none;}span.bio,span.author{font-size:0.7em;}div.question{margin-bottom:2cm;}"},
        {"name":"左岸读书","url":"https://rsshub.app/zreading","saveimg":false,"imgquality":100}    
    ],
    "emailinfo": {
        "enable": false,
        "to": "@kindle.cn",
        "from": "@.cn",
        "smtp": "smtp..cn",
        "port": 25,
        "pwd": "",
        "epub": false,
        "mobi": true
    },
    "webdav":{
        "enable":false,
        "server":"https://dav.jianguoyun.com/dav/genrss/",
        "user":"@.cn",
        "pwd":"",
        "epub": false,
        "mobi": true
    },
    "Github": true
}
''')

logging.info("配置配置文件")
if(config):
    config = json.loads(config)
feeds = config["feeds"]
booktitle = config["title"]
emailInfo = config["emailinfo"]
webdavInfo = config["webdav"]
CONFIG_PATH = './config'
feed_file = "./config/time.txt"
source_path = os.path.abspath(r'./template')
target_path = os.path.abspath(r'./temp')
if not os.path.exists(target_path):
    # 如果目标路径不存在原文件夹的话就创建
    os.makedirs(target_path)

if os.path.exists(source_path):
    # 如果目标路径存在原文件夹的话就先删除
    shutil.rmtree(target_path)
shutil.copytree(source_path, target_path)
shutil.copy(os.path.abspath(r'./config/cover.jpg'), os.path.abspath(r'./temp/OEBPS/'))
logging.info('copy files finished!')

def get_start(fname):
    """
    Get the starting time to read posts since. This is currently saved as 
    the timestamp of the time file.
    """
    '''
    return pytz.utc.localize(datetime.fromtimestamp(os.path.getmtime(fname)))
    '''
    with open("./config/time.txt","r+") as f:
        timeStamp = int(f.read())
        #获取完start立即写入，确保时间间隔为最小
        f.seek(0)
        f.write(str(int(time.mktime(datetime.now(pytz.timezone('UTC')).timetuple()))))
        f.close()
    '''
    #获取完start立即写入，确保时间间隔为最小
    logging.info("save this stamp to file.")
    with open("./config/time.txt","w") as f:
        #f.write("1611509501")
        f.close()
    '''
    #logging.info(pytz.utc.localize(datetime.fromtimestamp(timeStamp)))
    return pytz.timezone('UTC').localize(datetime.fromtimestamp(timeStamp))
    #86400适用于每天推送一次
    #return pytz.timezone('UTC').localize(datetime.fromtimestamp(time.time()-86400))#发现有些Rss源的pubtime和显示在源上的time是不对称的，很难过，还没有想到更好的解决办法

def convert_to_mobi(input_file, output_file):
    cmd = ['ebook-convert', input_file, output_file]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out = process.communicate()
    #print ("Result : "+out.decode() )
    #print(str(out))
    if(output_file in str(out).encode('raw_unicode_escape').decode()):
        logging.info("mobi 创建成功")
    else:
        logging.info("mobi 创建失败")
        logging.info(out)
def sendEmail(send_from, send_to, subject, text, files):
    # assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    #msg['To'] = COMMASPACE.join(send_to)
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text, 'plain', 'utf-8'))

    for f in files or []:
        with open(f, "rb") as fil:
            msg.attach(MIMEApplication(
                fil.read(),
                Content_Disposition=f'attachment; filename="{os.path.basename(f)}"',
                Name=os.path.basename(f)
            ))
    try:
        smtp = smtplib.SMTP_SSL(emailInfo["smtp"],emailInfo["port"])
    except:
        smtp = smtplib.SMTP(emailInfo["smtp"],emailInfo["port"])
    if("@outlook.com" in send_from):#outlook邮箱自动开启starttls安全验证，其他的暂不清楚
        smtp.starttls()
    logging.info(smtp.login(emailInfo["from"], emailInfo["pwd"]))
    logging.info(smtp.sendmail(send_from, send_to, msg.as_string()))
    smtp.quit()

def do_one_round():
    # get all posts from starting point to now
    start = get_start(feed_file)
    
    logging.info(f"Collecting posts since {start} UTC")
    logging.info(f"Convert Rss to json( need a long time if pic needed)")
    #generJson
    project = processRss.processRss(start)
    logging.info("RSS2Json")
    json = project.genjson(feeds)
    if(project.updatenum!=0):
        logging.info(f"发现{project.updatenum}条RSS更新，开始Json2Epub")
        epubinfo = project.json2epub(json,booktitle)
        logging.info("Epub转换成功，准备保存Epub")
        epubFile = f"{booktitle}.epub"
        mobiFile = F"{booktitle}.mobi"
        logging.info(f"删除旧的书籍(如果有)")
        if(os.path.exists(epubFile)):
            os.remove(epubFile)
        if(os.path.exists(mobiFile)):
            os.remove(mobiFile)
        project.save_epub(epubinfo,savepath=epubFile)
        logging.info("Del Temp folder")
        shutil.rmtree("./temp/")
        logging.info("Epub2Mobi")
        convert_to_mobi(epubFile, mobiFile)
        ###################################文件创建完成，开始发送部分
        logging.info("send file by email")
        if(emailInfo["enable"]==True):
            attachfile=[]
            if(emailInfo["epub"]):
                attachfile.append(epubFile)
            if(emailInfo["mobi"]):
                attachfile.append(mobiFile)
            sendEmail(send_from=emailInfo["from"],
                        send_to=emailInfo["to"],
                        subject="Convert",
                        text="delivery by your github action.\n\n--\n\n",
                        files=attachfile)
        else:
            logging.info("Email is disabled, skip")
        logging.info("send file by webdav")
        if(webdavInfo["enable"]==True):
            attachfile=[]
            if(webdavInfo["epub"]):
                attachfile.append(epubFile)
            if(webdavInfo["mobi"]):
                attachfile.append(mobiFile)
            for thisfile in attachfile:
                fileb = open(thisfile,'rb')
                r = requests.put(webdavInfo["server"]+thisfile, data=fileb,auth = requests.auth.HTTPBasicAuth(webdavInfo["user"], webdavInfo["pwd"]))
                #print(r)
                logging.info("文件上传返回代码"+str(r.status_code))
            logging.info("webdav上传完成")
        else:
            logging.info("webdav is disabled, skip")
        
        logging.info("upload file to github repo")
        if(config["Github"]==False):
            os.remove(epubFile)
            os.remove(mobiFile)
            logging.info("upload is disabled, skip")

    else:
        shutil.rmtree("./temp/")
        logging.info("RSS无更新，取消执行")
    logging.info("Finished.")
if __name__ == '__main__':
    do_one_round()
