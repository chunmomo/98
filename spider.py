#-*- coding:utf-8 -*-
import json
import os , re
import csv
import codecs
import requests
from lxml import etree
from pip._vendor.distlib.compat import raw_input
import random
import time
from urllib.parse import urlparse
from urllib.parse import unquote,quote

#定义基本信息
magnet = ""
aria2host="5.183.xx.xx"
aria2port="6800"
downloadpath =r'/home/aria2'
#aria2密码,密码为空时aria2session= None
aria2session= 'xxx'

class Spider:
    def __init__(self):
        self.ua_header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3278.0 Safari/537.36"}
        self.failitem=[]
        self.f=codecs.open('sht_torrent.csv','a+','utf-8')
        self.f_csv=csv.writer(self.f)
        if not os.path.isfile('sht_torrent.csv'):
            self.f_csv.writerow(['番号','标题','女优','大小','有无码','磁力链接','种子链接']) 

    def javSpider(self):
        choose = 1 #input('输入模式 0：仅上一次未成功的项 1：正常爬取模式\n')
        for item in self.failitemread():
            try:
                self.f_csv.writerow((item[0],self.gettorrent(item[1])))
            except:
                self.failitem.append(item)    
        choose = int(choose)
        if choose==0:
            return
        beginpage=input('输入起始页码：')
        endpage=input('请输入终止页码：')
        for page in range(int(beginpage),int(endpage)+1):
             try:
                 urllist = 'https://www.sehuatang.org/forum-103-'+str(page)+'.html'
                 self.loadPage(urllist)      
             except Exception as e:
                 print(e)
    #获取页面内容
    def loadPage(self, url):
        html=requests.get(url)
        selector = etree.HTML(html.text)
        javstar=selector.xpath('//*/table/*/tr/th/a[2]')
        torrentlist=[]
#        page_url='https://www.98ssw.space/'+item.get('href')
        for item in javstar:
            try:
                if '置顶' in item.text:
                    continue
                page_url='https://www.sehuatang.org/'+item.get('href')
                temp=(self.getid(page_url),self.getname(page_url),self.getactor(page_url),self.getsize(page_url),self.getma(page_url),self.getmagnet(page_url),self.gettorrent(page_url))
                print(temp)
                #print(self.getid(page_url))
                path = os.getcwd()+'/'+'down.txt'
                try:
                    f = open(path,'r',encoding="utf-8").read()
                except IOError:
                    f = open(path,'w',encoding="utf-8")
                    f.close()
                    f = []
                #读取内容没有的话追加内容
                vainfo = page_url[33:-9]
                vastr = vainfo in f
                if vastr == True:
                    #已经有了
                    print(self.getid(page_url) + '已经存在，跳过采集....')
                    continue
                else:
                    #没有的下载采集,下载视频
                    #tt = random.randint(0,2)
                    #print('防止刷新过快，休息:'+str(tt)+'s')
                    #time.sleep(tt)
                    #写入文件csv
                    #print('正在写入csv文件......')
                    torrentlist.append(temp)
                    print('发送到种子'+self.getid(page_url)+'到aria2')
                    self.aria2(self.gettorrent(page_url))
                    print('保存到已下载列表......\n')
                    #写入文件txt   
                    self.savefile(path,vainfo)
            except Exception as e:
                print(e)
                self.failitem.append(self.getid(page_url),page_url)
        self.f_csv.writerows(torrentlist)

    def getmagnet(self,url):
        html=requests.get(url)
        selector = etree.HTML(html.text)
        magnet = selector.xpath('//*/ol/li')
        for item in magnet:
            return item.text

    def getid(self,url):
        html=requests.get(url)
        selector = etree.HTML(html.text)
        id = selector.xpath('//*/ignore_js_op/dl/dd/p/a')
        if not id:
            id = selector.xpath('//*/ignore_js_op/span/a')
            for item in id:
                return item.text[:-8]
        else:
            for item in id:
                return item.text[:-8]

    def gettorrent(self,url):
        html=requests.get(url)
        selector = etree.HTML(html.text)
        torrent = selector.xpath('//*/ignore_js_op/dl/dd/p/a/@href')
        if not torrent:
            torrentN = selector.xpath('//*/ignore_js_op/span/a/@href')
            for item in torrentN:
                return item
        else:
            for item in torrent:
                return item

    def getactor(self,url):		
        html=requests.get(url)
        actor=re.findall(r'【出演女优】：([\s\S].*?)<br />', html.text)	
        for item in actor: 
            return item
			
    def getname(self,url):		
        html=requests.get(url)
        name=re.findall(r'【影片名称】：([\s\S].*?)<br />', html.text)	
        for item in name: 
            return item

    def getsize(self,url):		
        html=requests.get(url)
        size=re.findall(r'【影片大小】：([\s\S].*?)<br />', html.text)	
        for item in size: 
            return item

    def getma(self,url):		
        html=requests.get(url)
        ma=re.findall(r'【是否有码】：([\s\S].*?)<br />', html.text)	
        for item in ma: 
            return item
			
    def failitemwrite(self):
        file = open('faileditem.txt', 'w+')
        file.write(json.dumps(self.failitem))
        file.close()

    def failitemread(self):
        file = codecs.open('faileditem.txt','w+','utf-8')
        lists=[]
        string = file.read()
        if len(string):
            print(string)
            lists=json.loads(string)
        print(lists)
        return lists

    def aria2(self,url):
        #tmp=urlparse(url.replace('/'+url.split('/')[-1],''))
        #tmp=unquote(tmp.path, encoding="utf-8").replace('/0:','')
        options = {"dir": downloadpath}
        aria2 = Aria2c(host=aria2host, port=aria2port,token=aria2session)
        aria2.addUri(url,options=options)

    def savefile(self,path,vainfo):
        my_open = open(path, 'a',encoding="utf-8")
        my_open.write(vainfo+'\n')
        my_open.close()
	
class Aria2c:
    '''
    Example :
      client = Aria2c('localhost', '6800')
      # print server version
      print(client.getVer())
      # add a task to server
      client.addUri('http://example.com/file.iso')
      # provide addtional options
      option = {"out": "new_file_name.iso"}
      client.addUri('http://example.com/file.iso', option)
    '''
    IDPREFIX = "pyaria2c"
    ADD_URI = 'aria2.addUri'
    GET_VER = 'aria2.getVersion'

    def __init__(self, host, port, token=None):
        self.host = host
        self.port = port
        self.token = token
        self.serverUrl = "http://{host}:{port}/jsonrpc".format(**locals())

    def _genPayload(self, method, uris=None, options=None, cid=None):
        cid = IDPREFIX + cid if cid else Aria2c.IDPREFIX
        p = {
            'jsonrpc': '2.0',
            'id': cid,
            'method': method,
            'params': []
        }
        if self.token is not None:
            p['params'] = ["token:" + self.token]
        else:
            p['params'] = ["token:" + '']
        if uris:
            p['params'].append(uris)
        if options:
            p['params'].append(options)
        return p

    @staticmethod
    def _defaultErrorHandler(code, message):
        print("ERROR: {}, {}".format(code, message))
        return None

    def _post(self, action, params, onSuc, onFail=None):
        if onFail is None:
            onFail = Aria2c._defaultErrorHandler
        payloads = self._genPayload(action, *params)
        resp = requests.post(self.serverUrl, data=json.dumps(payloads))
        result = resp.json()
        if "error" in result:
            return onFail(result["error"]["code"], result["error"]["message"])
        else:
            return onSuc(resp)

    def addUri(self, uri, options=None):
        def success(response):
            return response.text

        return self._post(Aria2c.ADD_URI, [[uri, ], options], success)

    def getVer(self):
        def success(response):
            return response.json()['result']['version']

        return self._post(Aria2c.GET_VER, [], success)	
		
if __name__ == '__main__':
    print("第一次使用请打开文件配置aria2参数")
    print("正在测试aria2链接情况，下面输出aria2版本号即为成功")
    aria2 = Aria2c(host=aria2host, port=aria2port,token=aria2session)
    print("aria2版本号为:"+aria2.getVer())
    print("-------------------------")
    mySpider = Spider()
    mySpider.javSpider()
    mySpider.failitemwrite()
