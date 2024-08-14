import argparse
import socket, threading
from contextlib import closing


class TcpClient(threading.Thread):
    def __init__(self, server_host, server_port, app_port):
        self.server_host = server_host
        self.server_port = server_port
        self.app_port = app_port
        threading.Thread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((server_host, server_port))

        self.app = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.app.connect(("127.0.0.1", app_port))

    def app_to_server(self,data):
            try:
                self.s.sendall(data)
                print(f"[*] {self.app.getpeername()}-->{self.server_host}:{self.server_port} 数据发送成功")
            except Exception as e:
                print(f"[!] {self.app.getpeername()}-->{self.server_host}:{self.server_port} 数据发送失败: {e}")


    def server_to_app(self,data):

            try:
                self.app.sendall(data)
                print(f"[*]{self.server_host}:{self.app_port}-->{self.app.getpeername()} 数据发送成功")
            except Exception as e:
                print(f"[!] {self.server_host}:{self.app_port}-->{self.app.getpeername()} 数据发送失败: {e}")


    def app_run(self):
        while True:
            try:
                data = self.app.recv(2048)
                print(f"[*] 接受到来自{self.app.getpeername()}的数据")
            except Exception as e:
                print(f"[!] 接收{self.app.getpeername()}数据失败: {e}")
                break
            if not data:
                break
            threading.Thread(target=self.app_to_server, args=(data,)).start()

    def client_run(self):
        while True:
            try:
                data = self.s.recv(2048)
                print(f"[*] 接受到来自{self.s.getpeername()}的数据")
            except Exception as e:
                print(f"[!] 接收{self.s.getpeername()}数据失败: {e}")
                break
            if not data:
                break
            threading.Thread(target=self.server_to_app, args=(data,)).start()
    def run(self):
        print(f"[*] 客户端初始化成功")
        threading.Thread(target=self.app_run).start()
        threading.Thread(target=self.client_run).start()
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='基本用法')
    parser.add_help = True
    parser.add_argument('-ip', '--server_host', type=str, required=True,help='服务器地址', default='127.0.0.1')
    parser.add_argument('-sp', '--server_port', type=int, required=False,help='服务器端口', default=8081)
    parser.add_argument('-ap', '--app_port', type=int, required=True,help='应用端口', default=22)
    args = parser.parse_args()

    TcpClient(server_port=args.server_port, server_host=args.server_host, app_port=args.app_port).run()
