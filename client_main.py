import argparse

import subprocess

from proxyclient import tcpc


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
            subprocess.Popen(['python', 'socket_5.py','','','0',str(args.socket_port)])
            tcpc.TcpClient(server_port=args.server_port,
                           server_host=args.server_host,
                           app_host=args.app_host,
                           app_port=args.socket_port,
                           user_port=args.user_port).run()
        elif args.socket_username != '' and args.socket_password != '':
            subprocess.Popen(['python', 'socket_5.py', args.socket_username, args.socket_password, '2', str(args.socket_port)])
            tcpc.TcpClient(server_port=args.server_port,
                           server_host=args.server_host,
                           app_host=args.app_host,
                           app_port=args.socket_port,
                           user_port=args.user_port).run()
        else:
            raise ValueError('socket5 服务器用户名和密码必须同时填写')
    else:
        raise ValueError('-t 参数类型错误')