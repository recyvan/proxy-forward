import argparse
import json
import socket, threading
from log.log import Logger


class TcpClient(threading.Thread):
    def __init__(self, server_host, server_port, app_port, user_port):
        self.server_host = server_host
        self.server_port = server_port
        self.app_port = app_port
        threading.Thread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((server_host, server_port))
        data = {'msg': "请求连接", "port": user_port}
        data = json.dumps(data).encode('utf-8')
        data = data + b"#END#"
        self.s.send(data)
        self.app = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.app.connect(("127.0.0.1", app_port))
        self.heartbeat_counter = {}  # 心跳包计数器

    #心跳包处理
    # def handle_heartbeat(self, conn):
    #     # 接收来自客户端连接的数据
    #     while True:
    #         data = conn.recv(1024)
    #         if data ==b'heartbeat':
    #             counter = self.heartbeat_counter.get(conn)
    #             if not counter:
    #                 counter = 0
    #             counter += 1
    #             self.heartbeat_counter[conn] = time.time()


        # 每30秒检测超时连接

    def app_to_server(self, data):
        try:
            self.s.sendall(data)
            Logger.info(f"{self.app.getpeername()}-->{self.server_host}:{self.server_port} 数据发送成功")
        except Exception as e:
            Logger.error(f"数据发送失败: {e}")
            # print(f"[!] {self.app.getpeername()}-->{self.server_host}:{self.server_port} ")

    def server_to_app(self, data):

        try:
            self.app.sendall(data)
            Logger.info(f"{self.server_host}:{self.app_port}-->{self.app.getpeername()} 数据发送成功")

        except Exception as e:
            Logger.error(f"数据发送失败: {e}")
            # print(f"[!] {self.server_host}:{self.app_port}-->{self.app.getpeername()} 数据发送失败: {e}")

    def app_run(self):
        while True:
            try:
                data = self.app.recv(2048)
                Logger.info(f"接受到来自应用端的数据")
            except Exception as e:
                Logger.error(f"接收应用数据失败，应用端已断开连接: {e}")
                self.s.close()
                self.app.close()
                Logger.warning("服务端已断开连接，应用端已断开连接")
                return

            if not data:
                break
            threading.Thread(target=self.app_to_server, args=(data,)).start()

    def client_run(self):
        while True:
            try:
                data = self.s.recv(2048)
                Logger.info(f"接受到来自服务端的数据")
            except Exception as e:
                Logger.error(f"接收服务端数据失败,服务端已断开连接: {e}")
                self.s.close()
                self.app.close()
                Logger.warning("服务端已断开连接，应用端已断开连接")
                return
            if not data:
                break
            threading.Thread(target=self.server_to_app, args=(data,)).start()

    def run(self):
        Logger.info(f"客户端初始化成功")
        threading.Thread(target=self.client_run).start()
        threading.Thread(target=self.app_run).start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='基本用法')
    parser.add_help = True
    parser.add_argument('-i', '--server_host', type=str, required=True, help='服务器地址', default='127.0.0.1')
    parser.add_argument('-sp', '--server_port', type=int, required=False, help='服务器端口', default=8081)
    parser.add_argument('-ap', '--app_port', type=int, required=True, help='应用端口', default=22)
    parser.add_argument('-up', '--user_port', type=int, required=False, help='用户端口', default=8082)

    args = parser.parse_args()

    TcpClient(server_port=args.server_port, server_host=args.server_host, app_port=args.app_port,
              user_port=args.user_port).run()
