## 针对于TCP流的内网端口对端口的转发工具

## 更新日志
- 2024-8-21: 发布v0.4.1版本
  - 优化代码结构，增加功能：增加了对socket5协议的支持。支持代理socker5下tcp/udp的数据转发，初步适配proxychains工具
  - 修复了tcp端对端数据转发中http的中断造成的服务端无法再次接收数据的bug。
  - 更新了参数使用说明。
- 2024-8-15: 发布v0.2版本
  - 优化代码结构，增加功能：增加了多个客户端连接服务端的功能。
  - 优化代码结构，增加功能：增加了日志功能，可记录转发过程中的日志。
  - 改为命令行模式，增加了命令行参数功能。

- 2024-8-14: 发布初始版本 v0.1    
  - tcp端对端流量转发初想设计成功，已通过ssh流量转发测试。
  - 后续将继续完善功能，并发布更多版本。

## 功能介绍
###  v0.4.1版本参数说明

> 服务端:  
>> -p 端口号: 指定服务端监听的端口号，默认为8080。   
> >-v 版本信息  
> > -h 帮助信息 

> 客户端  
> > -sh --server-host 服务器地址: 指定服务端的地址，默认为localhost。  （必选）   
> > -sp --server-port 服务器端口: 指定服务端的端口号，默认为8080。  (必选)  
> > -ah --app_host 应用地址: 指定应用的地址，默认为localhost。  
> > -ap --app_port 应用端口: 指定应用的端口号，默认为80。  (必选)  
> > -t --type 转发类型:tcp,socks5,指定转发类型，默认为tcp。  
> > -socks-host --sockrts-host socks5服务器地址: 指定socks5服务器地址，默认为localhost。  
> > -socks-port --sockets-port socks5服务器端口: 指定socks5服务器端口号，默认为1080。  
> > username --socket-username socks5用户名: 指定socks5用户名，默认为""。  
> > password --socket-password socks5密码: 指定socks5密码，默认为""  
> > -v 版本信息  
> > -h 帮助信息  


> 如有任何问题，请联系本人邮箱：recyvanren@gmail.com 
