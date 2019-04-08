# Author: Justin Miron
# Measurement script that acts as either a client or server s.t. the client can measure
# the latency to the server.
#
# Required args:
#   -client: Whether we are acting as the client. If this arg is not passed,
#            we are the server.
#   
# Client optional args:
#   -send_interval_s: (default: 5) The number of seconds between sending blocks.
#   -block_size_b: (default: 1) The number of bytes in each block.
#   -num_blocks: (default: 1000) The number of blocks to send.
#
# Warning - coded while listening to ska punk. 


import argparse
from  os import urandom as randbytes
import socket
import time

# Default parameter values
DEFAULT_SEND_INTERVAL_S = 5
DEFAULT_BLOCK_SIZE_B = 1
DEFAULT_NUM_BLOCKS = 1000
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 13800

def ns_to_s(ns_value):
    return float(ns_value)/ (10 ** 9)

def client(server_host, server_port, send_interval_s, block_size_b, num_blocks):
    print('Starting client connection to server %s:%d' % (server_host, server_port))
    print('Will be sending blocks of size %d every %d seconds for a total of %d blocks '
          '(est. time: %d minutes)' % (block_size_b, send_interval_s, num_blocks, num_blocks * send_interval_s / 60))

    data = randbytes(block_size_b)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((server_host, server_port))
        except Exception as e:
            print('Failed to connect to server with Error "%s"' % str(e))
            exit(-1)

            
        # We have connected successfully, begin loop of sending data and recording RTT.
        rtt = 0
        for _ in range(num_blocks):
            send_time = time.time_ns()
            s.sendall(data)
            data = s.recv(block_size_b)
            receive_time = time.time_ns()
            rtt = ns_to_s(receive_time - send_time)
            print('%f' % rtt)
            time.sleep(send_interval_s - rtt)


def server(server_host, server_port, block_size_b):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_host, server_port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected to', addr)
            b_received = 0
            block = b''
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                block += data
                if len(block) == block_size_b:
                    conn.sendall(block)
                    block = b''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Measures latency from a client to a server '
                                                 'for a fixed block size.')
    parser.add_argument('--client', 
                        dest='is_client', 
                        default=False, 
                        action='store_true',
                        help='acts as the client in the measurement')

    parser.add_argument('--host', 
                        dest='host',
                        default=DEFAULT_HOST,
                        type=str,
                        action='store',
                        help='host ip of the server')

    parser.add_argument('--port', 
                    dest='port', 
                    default=DEFAULT_PORT,
                    type=int,
                    action='store',
                    help='port of the server')

    parser.add_argument('--send_interval_s', 
                    dest='send_interval_s', 
                    default=DEFAULT_SEND_INTERVAL_S,
                    type=int,
                    action='store',
                    help='The number of seconds between client block sends.')

    parser.add_argument('--block_size_b', 
                    dest='block_size_b', 
                    default=DEFAULT_BLOCK_SIZE_B,
                    type=int,
                    action='store',
                    help='The number of bytes in each client block send.')

    parser.add_argument('--num_blocks', 
                    dest='num_blocks', 
                    default=DEFAULT_NUM_BLOCKS,
                    type=int,
                    action='store',
                    help='The number of blocks for a client to send')

    args = parser.parse_args() 
    
    # Start client or server code.
    if args.is_client:
        client(args.host, args.port, args.send_interval_s, args.block_size_b, args.num_blocks)
    else:
        server(args.host, args.port, args.block_size_b)
