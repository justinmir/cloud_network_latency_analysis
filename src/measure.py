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
DEFAULT_SEND_INTERVAL_S = 0
DEFAULT_BLOCK_SIZE_B = 1
DEFAULT_NUM_BLOCKS = 1000
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 13800
DEFAULT_FNAME = 'latency.txt'

def ns_to_s(ns_value):
    return float(ns_value)/ (10 ** 9)

def client(server_host, server_port, send_interval_s, block_size_b, num_blocks, latency_out_file):
    print('Starting client connection to server %s:%d' % (server_host, server_port))
    print('Will be sending blocks of size %d every %d seconds for a total of %d blocks '
          '(est. time: %d minutes)' % (block_size_b, send_interval_s, num_blocks, num_blocks * send_interval_s / 60))

    block_data = randbytes(block_size_b)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s, open(latency_out_file, 'w+') as f:
        while True:
            try:
                s.connect((server_host, server_port))
                break
            except Exception as e:
                time.sleep(0.1)

        print('Successfully connected to server %s:%d' % (server_host, server_port))

        # We have connected successfully, begin loop of sending data and recording RTT.
        rtt = 0.
        for i in range(num_blocks):
            print('Block: %d' % i)
            send_time = time.time_ns()
            s.sendall(block_data)

            b_received = 0
            while True:
                data = s.recv(8192)
                b_received += len(data) # Warning: Copy.
                if b_received == block_size_b:
                    b_received = 0
                    break

            receive_time = time.time_ns()
            rtt = ns_to_s(receive_time - send_time)
            f.write('%f\n' % rtt)
            time.sleep(max(0, send_interval_s - rtt))

def server(server_host, server_port, block_size_b):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_host, server_port))
        s.listen()

        block_data = randbytes(block_size_b)

        conn, addr = s.accept()
        with conn:
            print('Connected to', addr)
            b_received = 0
            while True:
                data = conn.recv(8192)
                if not data:
                    break

                b_received += len(data)
                if b_received == block_size_b:
                    conn.sendall(block_data)
                    b_received = 0

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

    parser.add_argument('--latency_fname', 
                    dest='latency_fname', 
                    default=DEFAULT_FNAME,
                    type=str,
                    action='store',
                    help='The file to write latencies to')

    args = parser.parse_args() 

    # Start client or server code.
    if args.is_client:
        client(args.host, args.port, args.send_interval_s, args.block_size_b, args.num_blocks, args.latency_fname)
    else:
        server(args.host, args.port, args.block_size_b)
