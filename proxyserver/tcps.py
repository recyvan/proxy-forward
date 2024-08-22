import argparse
import json
import socket, threading

from proxylog.log import Logger

## 服务端
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
                Logger().info(f"接收到来自{conn_receiver.getpeername()}的数据")
                if not data:
                    break
                try:
                    conn_sender.sendall(data)
                    Logger().info(f"向{conn_receiver.getpeername()}-->{conn_sender.getpeername()}发送数据")
                except Exception:
                    Logger().error("发送数据时出错")
                    break
            except Exception as e:
                Logger().warning(f"接收数据时出错:{e}")
                break


        conn_receiver.close()
        conn_sender.close()
        return

    # 心跳包检测
    def heartbeat_check(self, conn):
        try:
            while True:
                data = conn.receive(4)
                if not data:
                    break
                conn.sendall(b"0x00")
        except Exception as e:
            Logger().warning(f"心跳包检测出错:{e}")

    def tcp_mapping(self,local_conn, remote_conn):
        # threading.Thread(target=self.heartbeat_check, args=(remote_conn,)).start()
        threading.Thread(target=self.single_tcp_transmission, args=(local_conn, remote_conn)).start()
        threading.Thread(target=self.single_tcp_transmission, args=(remote_conn, local_conn)).start()

    def run(self):
        while True:
            server_conn, server_addr = self.server_socket.accept()
            Logger().info(f" {server_addr}服务端连接成功")
            temp_data = server_conn.recv(2048)
            temp_data = json.loads(temp_data.decode("utf-8").split("#END#")[0])
            if temp_data['msg'] == "请求连接" :
                self.usr_port = temp_data['port']
                # 等待用户连接
                self.user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.user_socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, True)
                self.user_socket.bind(("127.0.0.1",self.usr_port))
                self.user_socket.listen(10)
                user_conn, user_addr = self.user_socket.accept()
                Logger().info(f"{user_addr}用户连接成功,正在监听用户端口:{self.usr_port}")
                self.usr_pool.append(user_conn)
                self.client_pool.append(server_conn)
                # threading.Thread(target=self.heartbeat_check, args=(server_conn,)).start()
                threading.Thread(target=self.tcp_mapping, args=(server_conn, user_conn)).start()
    def main(self):
        Logger().info( f"服务端已启动,监听端口:{self.server_port}")
        threading.Thread(target=self.run,args=()).start()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='基本用法')
    parser.add_argument('-sp', '--server_port', type=int, default=8081, help='服务端监听端口')
    # parser.add_argument('-up', '--user_port', type=int, default=8082, help='用户连接端口')
    args = parser.parse_args()
    TcpServer(server_port=args.server_port).main()
    # Thread = TcpServer(server_port=args.server_port)
    # threading.Thread(target=Thread.run).start()
