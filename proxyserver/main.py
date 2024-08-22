import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import tcps

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='基本用法')
    parser.add_argument('-sp', '--server_port', type=int, default=8081, help='服务端监听端口')
    parser.add_argument('-v', '--version', action='version', help='版本信息', version='%(prog)s 0.4.1')

    args = parser.parse_args()
    tcps.TcpServer(server_port=args.server_port).main()