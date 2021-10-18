"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 0NN
- Fall 202N
- Lab N
- Names:
  - 
  - 

An HTTP server

Introduction: (Describe the lab in your own words)




Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked, and any suggestions you have for improvement)





"""

import socket
import threading
import os
import mimetypes
import datetime


def main():
    """ Start the server """
    http_server_setup(8080)


def http_server_setup(port):
    """
    Start the HTTP server
    - Open the listening socket
    - Accept connections and spawn processes to handle requests

    :param port: listening port number
    """

    num_connections = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_address = ('', port)
    server_socket.bind(listen_address)
    server_socket.listen(num_connections)
    try:
        while True:
            request_socket, request_address = server_socket.accept()
            print('connection from {0} {1}'.format(request_address[0], request_address[1]))
            # Create a new thread, and set up the handle_request method and its argument (in a tuple)
            request_handler = threading.Thread(target=handle_request, args=(request_socket,))
            # Start the request handler thread.
            request_handler.start()
            # Just for information, display the running threads (including this main one)
            print('threads: ', threading.enumerate())
    # Set up so a Ctrl-C should terminate the server; this may have some problems on Windows
    except KeyboardInterrupt:
        print("HTTP server exiting . . .")
        print('threads: ', threading.enumerate())
        server_socket.close()


def handle_request(request_socket):
    """
    Handle a single HTTP request, running on a newly started thread.

    Closes request socket after sending response.

    Should include a response header indicating NO persistent connection

    :param request_socket: socket representing TCP connection from the HTTP client_socket
    :return: None
    """
    status_code, url = receive_request(request_socket)
    respond(status_code, url)
    pass  # Replace this line with your code


def receive_request(request_socket):
    """
    this method receives request from a client and parses thorough the data
    it will try to verify the data
    """
    status_code, url = read_request_line(request_socket)
    read_headers(request_socket)
    return status_code, url


def read_request_line(request_socket):
    """
    This method reads the request line i.e. GET / HTTP/1.1 and saves all the components to
    a byte[] array split by the spaces so the array should hold [GET] [/URL] and [HTTP/1.1]
    """
    b = read_line(request_socket).replace(b'\r\n', b'').split(b' ', -1)
    print(b)
    url = b.index(1)

    t = read_headers(request_socket)
    return b'200', url


def read_headers(request_socket):
    """
    this method goes through all the headers and reads them one by one
    and saves them to a map with the keys being there name
    """
    header_dict = {}
    b = b''
    end_of_headers = False
    while not end_of_headers:
        header, end_of_headers = read_header(request_socket)
        if not end_of_headers:
            header_dict[read_header_name(header)] = read_header_value(header)
        b += header
    print(header_dict)
    return b


def read_header(request_socket):
    """
    This method reads single headers and can
    """
    b = b''
    is_end_of_headers = False
    b += read_line(request_socket)
    if b == b'\r\n':
        is_end_of_headers = True
    return b, is_end_of_headers


def read_header_value(byte_object):
    """
    if you need to remove \r\n from the data do it here
    """
    return byte_object[0:byte_object.index(b':')+1]


def read_header_name(byte_object):
    """
    if you need to remove or add to the name do it here
    """
    return byte_object[byte_object.index(b':')+2:byte_object.index(b'\r\n')+2]

def verify_request(line):
    pass

def next_byte(data_socket):
    """
    Read the next byte from the socket data_socket.

    Read the next byte from the sender, received over the network.
    If the byte has not yet arrived, this method blocks (waits)
      until the byte arrives.
    If the sender is done sending and is waiting for your response, this method blocks indefinitely.

    :param data_socket: The socket to read from. The data_socket argument should be an open tcp
                        data connection (either a client socket or a server data socket), not a tcp
                        server's listening socket.
    :return: the next byte, as a bytes object with a single byte in it
    """
    return data_socket.recv(1)


def read_line(data_socket):
    line = b''
    while not line.endswith(b'\r\n'):
        line += next_byte(data_socket)

    return line


# Eli's shit

def respond(stat_code, url):
    response = status_line(stat_code)
    response += generate_headers(url)
    response += body(url)
    return response


def body(file_name):
    pass


def status_line(stat_code):
    stat_line = b'HTTP/1.1 ' + stat_code
    if stat_code == b'200':
        stat_line += b' OK'

    elif stat_code == b'400':
        stat_line += b' BAD REQUEST'

    elif stat_code == b'404':
        stat_code += b' NOT FOUND'

    stat_line += b'\r\n'
    return stat_line


def generate_headers(file_name):
    header_map = dict()
    header_map['date'] = datetime
    header_map['connection'] = 0
    header_map['content_type'] = get_mime_type(file_name)
    header_map['content_length'] = get_file_size(file_name)


# ** Do not modify code below this line.  You should add additional helper methods above this line.

# Utility functions
# You may use these functions to simplify your code.


def get_mime_type(file_path):
    """
    Try to guess the MIME type of a file (resource), given its path (primarily its file extension)

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If successful in guessing the MIME type, a string representing the content type, such as 'text/html'
             Otherwise, None
    :rtype: int or None
    """

    mime_type_and_encoding = mimetypes.guess_type(file_path)
    mime_type = mime_type_and_encoding[0]
    return mime_type


def get_file_size(file_path):
    """
    Try to get the size of a file (resource) as number of bytes, given its path

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If file_path designates a normal file, an integer value representing the the file size in bytes
             Otherwise (no such file, or path is not a file), None
    :rtype: int or None
    """

    # Initially, assume file does not exist
    file_size = None
    if os.path.isfile(file_path):
        file_size = os.stat(file_path).st_size
    return file_size


main()

# Replace this line with your comments on the lab
