# GenBooks
Gen epub and mobi Books from RSS with github action

# 特点

1. 支持epub和mobi格式，支持邮箱（用于kindle）和webdav发送。
2. 部署在github action，免去服务费用以及GAE部署的账号问题
3. 1/25支持自定义下载图片以及更改图片压缩比例
4. 支持单个rss自定义css

# 缺点

~~订阅链接过多时，文件体积会比较大，大多数邮箱不支持20M以上的附件，所以当订阅链接较多时，推荐使用webdav上传~~

~~相比之下，mobi格式的体积要小于epub格式的体积，但是mobi格式的目录存在问题（只有一级目录），未修复~~

~~1.24 暂不支持图片显示，缩小文件体积~~

暂无

当前默认时区为东八区，GMT+8，暂不打算多时区支持

图片默认转换为黑白，暂不打算修改

# 使用方法

1. fork 本项目

2. 在config文件夹里替换成你的封面

3. setting里新建3个secret，CONFIG、GITHUBEMAIL、GITHUBUSER

   ### CONFIG

   使用json样式，

   ```json
   {
       "title":"RSSDaily - GenBook",
   	"feeds": [
           {"name":"知乎热榜","url":"https://rsshub","saveimg":false,"imgquality":100},
           {"name":"example","url":"https://最后一个不要写逗号/","saveimg":false,"imgquality":100,"css":""}
   	],
       "note":"请按照本格式书写feed源,saveimg是意思是是否保存图片（保存图片可能会导致排版错误），imgquality为压缩图片的比例，100表示不压缩，图片过多时，不压缩会导致文件较大",
   	"emailinfo": {
           "note":"是否通过邮件发送",
   		"enable": false,
   		"to": "the email you want to receive",
   		"from": "your email",
   		"smtp": "you email smtp serve adress",
   		"port": 25,
   		"pwd": "your pwd",
           "note2":"是否上传epub或者mobi，仅当enable为true时可用，webdav同",
   		"epub": true, 
   		"mobi": true
   	},
   	"webdav": {
   		"enable": false, 
   		"server":"https://dav.jianguoyun.com/dav/",
           "user":"@189.cn",
           "pwd":"",
   		"epub": true,
   		"mobi": true 
   	},
   	"Github": true,
       "note":"是否上传到github repo，默认上传两个文件，不支持修改"
   }
   ```

   ### GITHUBEMAIL 你的github账户的邮箱

   ### GITHUBUSER 你的github的用户名

4. 在./github/workflow里面修改想推送的时间和频率

   参考crontab，默认为北京时间6：00发送，6:00GMT(22:00UTC)

5. 点击github action，点击star进行测试

   ## CSS示例

   知乎

   `img.avatar{display:none;}`

   36kr

   `h1,h2,h3,h4,h5,h6{font-size:1em; font-weight:normal}`

