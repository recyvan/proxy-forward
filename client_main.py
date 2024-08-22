import argparse

import subprocess

from socketserver import ThreadingTCPServer

from proxyclient import tcpc
from proxyclient import socket_5

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='基本用法')
    parser.add_help = True
    parser.add_argument('-sh', '--server_host', type=str, required=True, help='服务器地址', default='127.0.0.1')
    parser.add_argument('-sp', '--server_port', type=int, required=True, help='服务器端口', default=8081)
    parser.add_argument('-ah', '--app_host', type=str, required=False, help='应用地址', default='127.0.0.1')
    parser.add_argument('-ap', '--app_port', type=int, required=True, help='应用端口', default=80)
    parser.add_argument('-up', '--user_port', type=int, required=False, help='用户端口', default=8082)
    parser.add_argument('-v', '--version', action='version', help='版本信息', version='%(prog)s 0.4.1')
    parser.add_argument('-t', '--type', type=str, required=False, help='类型', default='tcp',
                        choices=['tcp', 'socket5'])
    parser.add_argument('-socket_port', '--socket_port', type=int, required=False, help='socket5 服务器端口',
                        default=1080)
    parser.add_argument('-username', '--socket_username', type=str, required=False, help='socket5 服务器用户名',
                        default='')
    parser.add_argument('-password', '--socket_password', type=str, required=False, help='socket5 服务器密码',
                        default='')

    args = parser.parse_args()
    if args.type == 'tcp':
        tcpc.TcpClient(server_port=args.server_port, server_host=args.server_host, app_host=args.app_host,
                       app_port=args.app_port, user_port=args.user_port).run()
    elif args.type == 'socket5':
        if args.socket_username == '' and args.socket_password == '':
            # socket_5.Socks5Handler.authenticated = 0
            # with ThreadingTCPServer(('0.0.0.0', args.socket_port), socket_5.Socks5Handler) as server:
            #     server.serve_forever()
            subprocess.Popen(['python', 'socket_5.py','','','0',str(args.socket_port)])
            tcpc.TcpClient(server_port=args.server_port, server_host=args.server_host,app_host=args.app_host ,app_port=args.socket_port,
                           user_port=args.user_port).run()
        else:
            socket_5.Socks5Handler.authenticated = 2
            socket_5.Socks5Handler.username = args.socket_username
            socket_5.Socks5Handler.password = args.socket_password
            with ThreadingTCPServer(('0.0.0.0', args.socket_port), socket_5.Socks5Handler) as server:
                server.serve_forever()
            tcpc.TcpClient(server_port=args.server_port, server_host=args.server_host,app_host=args.app_host, app_port=args.socket_port,
                          user_port=args.user_port).run()
