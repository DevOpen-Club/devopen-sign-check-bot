# 教程-使用 Python 原生 IDE 部署程序

# 1.安装环境
Python 官网：[Python.org](https://www.python.org/)

建议版本：3.9+

根据系统下载对应环境，并自行配置环境变量（不懂就百度）

# 2.编辑配置
这里以Windows系统为例，开始菜单打开IDE，然后复制main.py程序，按照注释更改配置。

![2.1](https://fb-cdn.fanbook.mobi/fanbook/app/files/chatroom/image/ed5324d1f3a41fa6df2b6330ca44ae2f.png)

# 3.安装库
需要额外安装的库：
- pip install requests
- pip install websocket-client
- pip install mysql-connector-python

方法：打开终端，分别输出以上指令，返回done成功。

![3.1](https://fb-cdn.fanbook.mobi/fanbook/app/files/chatroom/image/98c8f3f6b0b8c61d57aa8ad6ef94ddde.png)

# 4.导入数据库
使用 phpStudy 导入数据库（Windows）。
## 4.1.安装 phpStudy
小皮面板也是一个老程序了，有更新新版（web版本），但是我们建议使用原.exe版本，教程也将使用本版本讲解。[下载安装](https://www.xp.cn/download.html)

## 4.2.安装环境/软件
打开 phpStudy，找到“软件管理”栏，安装以下环境：
![4.1.1](https://fb-cdn.fanbook.mobi/fanbook/app/files/chatroom/image/3fe5a99e3944b7e8e36723eaa3737950.png)
![4.1.2](https://fb-cdn.fanbook.mobi/fanbook/app/files/chatroom/image/5678c795686c97124263a99c932b5e69.png)

下载完后，回到首页，点击“启动WNMP”服务一键启动。
![4.1.3](https://fb-cdn.fanbook.mobi/fanbook/app/files/chatroom/image/ddf4ef8303827fbd3b503f2b09cf1e8d.png)

## 4.2.创建数据库
点击左侧栏“数据库”->“新建”->“输入基本信息”->“完成”
![4.2.1](https://fb-cdn.fanbook.mobi/fanbook/app/files/chatroom/image/caeb282d09b8e93c7dc6c6c774d491c8.png)

回至首页，点击“数据库工具”“phpMyAdmin”，输入刚才创建数据库的用户名和密码，登录到数据库。

phpMyAdmin数据库管理页面，上方菜单栏内点击导入，选择版本号对应的数据库文件，导入即可使用。



# 5.运行服务
IDE里选择Run-Run Model，出现发送心跳包ping则代表程序开始运行，然后测试一遍所有功能。
![5.1](https://fb-cdn.fanbook.mobi/fanbook/app/files/chatroom/image/f08d99c4067ca1bd0ac70d4230ad5f5e.png)

------------
懒得写太多了，教程非常简略，后期会更新的。
