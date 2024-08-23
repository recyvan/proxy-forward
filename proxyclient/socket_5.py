from sys import argv, path
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path.append(BASE_DIR)
import socket
import struct
import select
from proxylog.log import Logger

from socketserver import ThreadingTCPServer, StreamRequestHandler


class Proxysockets5(StreamRequestHandler):
    username = ""
    password = ""
    logger = Logger()
    # 认证标志
    authenticated = 0

    # 连接到socks5服务器后进行协商，处理连接请求
    # 重写handle方法
    def handle(self):
        self.logger.info("Socks5初始化完成")
        self.logger.info(f"接收到来自{self.client_address}的连接请求")
        # ## 协商 ###
        # 接受两个字节的版本号和一个字节的认证方法数量 ver,nmethods
        header = self.connection.recv(2)
        version, nmethods = struct.unpack("!BB", header)
        if version != 5:
            self.logger.error(f"版本错误")
            raise Exception("版本错误")
        if nmethods <= 0:
            self.logger.error(f"方法数量错误")
            raise Exception("方法数量错误")
        # 获取客户端支持的认证方法
        methods = []
        for i in range(nmethods):
            methods.append(ord(self.connection.recv(1).decode("utf-8")))
        # # 2表示支持用户名密码认证
        # if 2 not in set(methods):
        #     self.server.close_request(self.request)
        #     self.logger.error(f"不支持的认证方法")
        #     return
        # 发送协商响应数据,即版本号和认证方法

        if self.authenticated in set(methods):
            if self.authenticated == 2:
                self.connection.sendall(struct.pack("!BB", 5, 2))
                if not self.verify_username_password():
                    self.logger.error(f"用户名或密码错误")
                    return
            elif self.authenticated == 0:
                self.connection.sendall(struct.pack("!BB", 5, 0))
        else:
            self.server.close_request(self.request)
            self.logger.error(f"不支持的认证方法")
        # self.connection.sendall(struct.pack("!BB", 5, 2))
        # ???
        # ### 认证 ###

        # ### 请求 ###
        header = self.connection.recv(4)
        ver, cmd, rsv, atpy = struct.unpack("!BBBB", header)
        if ver != 5:
            self.logger.error(f"版本错误")
            raise Exception("版本错误")
        if atpy == 1:
            # IPv4地址从二进制整数形式转换成十进制点分式字符串
            addr = socket.inet_ntoa(self.connection.recv(4))
        elif atpy == 3:
            # 域名地址从二进制形式转换成字符串 [0]从二进制中取第一个字节作为长度
            domain_len = self.connection.recv(1)[0]
            addr = self.connection.recv(domain_len)
        elif atpy == 4:
            # IPv4地址从二进制整数形式转换成十进制点分式字符串
            addr_ipv6 = self.connection.recv(16)
            addr = socket.inet_ntop(socket.AF_INET6, addr_ipv6)
        else:
            self.logger.error(f"地址类型错误")
            return
        port = struct.unpack("!H", self.connection.recv(2))[0]
        self.logger.info(f"连接请求：{addr}:{port}")
        # ### 数据转发 ###
        #开始相应
        try:
            ## 主动连接
            if cmd == 1:  #CONNECT连接方式
                remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote_socket.connect((addr, port))
                bind_addr = remote_socket.getsockname()
                self.logger.info(f"连接成功：{bind_addr[0]}:{bind_addr[1]}")
            else:
                self.server.close_request(self.request)
                self.logger.error(f"请求类型：{cmd},不支持的命令,关闭连接")
                return
            reply = struct.pack("!BBBBIH", 5, 0, 0, 1, struct.unpack("!I", socket.inet_aton(bind_addr[0]))[0],
                                bind_addr[1])
        except Exception as e:
            self.logger.error(f"连接失败：{e}")

            # version, rep=5(表示连接超时),rsv(保留参数),atpy(地址类型),addr(地址),port(端口)
            reply = struct.pack("!BBBBIH", 5, 5, 0, atpy, 0, 0)
        self.connection.sendall(reply)
        # 开始数据交换
        # rep=0(表示成功)
        if reply[1] == 0 and cmd == 1:
            self.change_data(self.connection, remote_socket)
        self.server.close_request(self.request)

    # 验证用户名和密码
    def verify_username_password(self):
        authentication_version = ord(self.connection.recv(1))
        if authentication_version == 1:
            username_len = ord(self.connection.recv(1))
            username = self.connection.recv(username_len).decode("utf-8")
            password_len = ord(self.connection.recv(1))
            password = self.connection.recv(password_len).decode("utf-8")
            if username == self.username and password == self.password:
                self.connection.sendall(struct.pack("!BB", authentication_version, 0))
                return True
            self.connection.sendall(struct.pack("!BB", authentication_version, 0xFF))
            self.server.close_request(self.request)
            return False
        else:
            self.logger.error(f"版本错误")
            raise Exception("版本错误")

    def change_data(self, client_socket, remote_socket):
        while True:
            readable, writable, exceptional = select.select([client_socket, remote_socket], [], [])
            if client_socket in readable:
                data = client_socket.recv(2048)
                if remote_socket.send(data) <= 0:
                    self.logger.info(f"客户端断开连接")
                    break
            if remote_socket in readable:
                data = remote_socket.recv(2048)
                if client_socket.send(data) <= 0:
                    self.logger.info(f"服务端断开连接")
                    break


if __name__ == '__main__':
    username = argv[1]
    password = argv[2]
    authenticated = int(argv[3])
    server_port = int(argv[4])
    Proxysockets5.username = username
    Proxysockets5.password = password
    Proxysockets5.authenticated = authenticated
    with ThreadingTCPServer(('0.0.0.0', server_port), Proxysockets5) as server:
        server.serve_forever()
