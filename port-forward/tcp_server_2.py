import argparse
import json
import socket, threading


class TcpServer(threading.Thread):
    def __init__(self, server_port):
        threading.Thread.__init__(self)
        self.server_port = server_port

        # 建立服务端监听
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", server_port))
        self.server_socket.listen(10)

        #服务端进行监听
        self.usr_port = 0


        self.usr_pool = []
        self.client_pool = []
        self.user_client_pool = {}

    # 单向流数据传递
    def single_tcp_transmission(self, conn_receiver, conn_sender):
        while True:
            try:
                # 接收数据缓存大小
                data = conn_receiver.recv(2048)
                print(f"接受到来自{conn_receiver.getpeername()}的数据")
            except Exception:
                print("[-] 关闭: 映射请求已关闭.")
                break
            if not data:
                break
            try:
                conn_sender.sendall(data)
                print(f"[*]{conn_receiver.getpeername()}-->{conn_sender.getpeername()} 数据已发送")
            except Exception:
                print("[-] 错误: 发送数据时出错.")
                break
            print("[+] 映射请求: {} ---> 传输到: {} ---> {} bytes"
                  .format(conn_receiver.getpeername(), conn_sender.getpeername(), len(data)))
        conn_receiver.close()
        conn_sender.close()
        return

    # 端口映射请求处理
    def tcp_mapping(self, local_conn, remote_ip, remote_port):
        remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            remote_conn.connect((remote_ip, remote_port))
        except Exception:
            local_conn.close()
            print("[x] 错误: 无法连接到 {}:{} 远程服务器".format(remote_ip, remote_port))
            return
        threading.Thread(target=self.single_tcp_transmission, args=(local_conn, remote_conn)).start()
        threading.Thread(target=self.single_tcp_transmission, args=(remote_conn, local_conn)).start()
        return
    def tcp_mapping(self,local_conn, remote_conn):
        threading.Thread(target=self.single_tcp_transmission, args=(local_conn, remote_conn)).start()
        threading.Thread(target=self.single_tcp_transmission, args=(remote_conn, local_conn)).start()

    def run(self):
        print(f"[+]初始化完成, 服务端监听端口: {self.server_port}, {self.usr_port}")
        while True:
            server_conn, server_addr = self.server_socket.accept()
            print(f"[+]  {server_addr}服务端连接成功")

            temp_data = server_conn.recv(2048)
            temp_data = json.loads(temp_data.decode("utf-8"))
            if temp_data['msg'] == "请求连接":
                self.usr_port = temp_data['port']
                # 等待用户连接
                self.user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.user_socket.bind(("127.0.0.1",self.usr_port))
                self.user_socket.listen(10)
                user_conn, user_addr = self.user_socket.accept()
                print(f"[+] {user_addr}新用户连接成功")
                self.user_client_pool[user_conn] = server_conn
                threading.Thread(target=self.tcp_mapping, args=(self.user_client_pool[user_conn], user_conn)).start()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='基本用法')
    parser.add_argument('-sp', '--server_port', type=int, default=8081, help='服务端监听端口')
    # parser.add_argument('-up', '--user_port', type=int, default=8082, help='用户连接端口')
    args = parser.parse_args()
    TcpServer(server_port=args.server_port).run()
