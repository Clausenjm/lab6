"""
- CS2911 - 051
- Fall 2021
- Lab 06
- Names:
  - Josiah Clausen
  - Elisha Hamp

An HTTP server

Introduction: (Describe the lab in your own words)
The purpose of this lab is to expose us to getting requests from a client
which we then have to respond with the appropriate information. Like content length
what the connection type is and what data we are sending. Along with that we must
also handle incorrect GET request as well as request that have no path on the
server

Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked, and any suggestions you have for improvement)
    This lab was in some ways tougher than the client lab. Handling 404 errors has been incredibly difficult for us.
The basic response however has worked rather well and allowed us to feel accomplished once we got that far, as it was
very fascinating to see our code respond to different url requests. There are no changes we could suggest.

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
    response = respond(status_code, url)
    request_socket.sendall(response)
    #request_socket.close() # We talked to you about this!!!!


def receive_request(request_socket):
    """
    -author: Josiah Clausen
    this method receives request from a client and parses thorough the data
    it will try to verify the data
    :param request_socket: The open tcp socket that the request is being made from.
    """
    status_code, url = read_request_line(request_socket)
    return status_code, url


def read_request_line(request_socket):
    """
    -author: Josiah Clausen
    This method reads the request line i.e. GET / HTTP/1.1 and saves all the components to
    a byte[] array split by the spaces so the array should hold [GET] [/URL] and [HTTP/1.1]
    :param request_socket: The open tcp socket that the request is being made from.
    """
    b = read_line(request_socket).replace(b'\r\n', b'').split(b' ', -1)
    stat_line = b'200'
    url = b'/'
    if b[0] == b'GET':
        find_the_url = b[1]
        if find_the_url != b'/' and find_the_url != b'/index.html' \
                and find_the_url != b'/msoe.png' and find_the_url != b'/styles.css':
            stat_line = b'404'
            url = b'/'
        else:
            url = b[1]
            read_headers(request_socket)
    else:
        stat_line = b'400'
        url = b'/'
    return stat_line, url


def read_headers(request_socket):
    """
    -author: Josiah Clausen
    this method goes through all the headers and reads them one by one
    and saves them to a map with the keys being there name
    :param request_socket: The open tcp socket that the request is being made from.
    """
    header_dict = dict()
    b = b''
    end_of_headers = False
    while not end_of_headers:
        header, end_of_headers = read_header(request_socket)
        if not end_of_headers:
            header_dict[read_header_name(header)] = read_header_value(header)
        b += header
    return b


def read_header(request_socket):
    """
    -author: Josiah Clausen
    This method reads single headers and can
    :param request_socket: The open tcp socket that the request is being made from.
    """
    b = b''
    is_end_of_headers = False
    b += read_line(request_socket)
    if b == b'\r\n':
        is_end_of_headers = True
    return b, is_end_of_headers


def read_header_value(byte_object):
    """
    -author: Josiah Clausen
    if you need to remove \r\n from the data do it here
    :param byte_object: this object is the bytes object of a header
    """
    holder = byte_object.split(b":", 1)
    return holder[1]


def read_header_name(byte_object):
    """
    -author: Josiah Clausen
    if you need to remove or add to the name do it here
    :param byte_object: this object is the bytes object of a header
    """
    holder = byte_object.split(b":", 1)
    return holder[0]


def next_byte(data_socket):
    """
    -author: Josiah Clausen
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
    """
    :author: Elisha Hamp
    Takes in the data socket and uses it to read a line of bytes, ending when the
    bytes end in CRLF.
    :param data_socket: The open tcp connection with the client to read from.
    :return: The full line of bytes received from the data socket.
    """
    line = b''
    while not line.endswith(b'\r\n'):
        line += next_byte(data_socket)

    return line


def respond(stat_code, url):
    """
    :author: Elisha Hamp
    Puts together the response with the status line, headers, and body.
    :param stat_code: The status code to be added to the response status line
    :param url: The url extension received from the tcp connection.
    :return: the full byte literal response
    """

    response = status_line(stat_code)
    url = check_default_file(url)
    response += generate_headers(url)
    if stat_code == b'404':
        response += b'<!DOCTYPE html><html lang="en"><head><body><meta charset="UTF-8"><h1>404 Not Found</h1></body></head></html>'
    elif stat_code == b'400':
        response += b'<!DOCTYPE html><html lang="en"><head><body><meta charset="UTF-8"><h1>400 bad request</h1></body></head></html>'
    else:
        response += body(url)
    return response


def body(url):
    """
    :author: Elisha Hamp
    Opens the desired file and reads the bytes in it.
    :param url: The url extension received from the tcp connection.
    :return: the body put together from reading the file.
    """
    file_name = url.replace(b'/', b'')
    file = open(file_name, 'rb')
    file_byte = file.read(1)
    file_body = b''
    while file_byte:
        file_body += file_byte
        file_byte = file.read(1)
    return file_body


def check_default_file(url):
    """
    :author: Elisha Hamp
    Checks the url byte literal to see if the program should return the default index.html file
    :param url: The url extension received from the tcp connection.
    :return: returns the adjusted
        """
    if url == b'/':
        url = b'/index.html'
    return url


def status_line(stat_code):
    """
    :author: Elisha Hamp
    Reads the status code and uses it to assemble the status line.
    :param stat_code: The status code to be added to the status line.
    :return: the full status line
    """
    stat_line = b'HTTP/1.1 ' + stat_code
    if stat_code == b'200':
        stat_line += b' OK'

    elif stat_code == b'400':
        stat_line += b' Bad Request'

    elif stat_code == b'404':
        stat_line += b' Not Found'

    stat_line += b'\r\n'
    return stat_line


def generate_headers(file_name):
    """
    :author: Elisha Hamp
    Gets a path using the file name and uses it to generate all of the necessary headers.
    :param file_name: name of the file to be used to generate the headers.
    :return: the headers as a byte literal.
    """
    header_map = dict()
    file_path = '.' + file_name.decode()
    #date = datetime.datetime.utcnow()
    timestamp = datetime.datetime.utcnow()
    timestring = timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT')
    # Sun, 06 Nov 1994 08:49:37 GMT
    header_map['Date: '] = timestring.encode()
    header_map['Connection: '] = b'close'
    header_map['Content-Type: '] = (get_mime_type(file_path).encode())
    header_map['Content-Length: '] = (str(get_file_size(file_path)).encode("ASCII"))

    return assemble_headers(header_map)


def assemble_headers(header_map):
    """
    :author: Elisha Hamp
    Turns the header map into a byte literal.
    :param header_map: Python dictionary containing all of the headers
    :return: headers in byte literal form
    """
    keys = header_map.keys()
    headers = b''
    for key in keys:
        headers += key.encode()
        headers += header_map[key]
        headers += b'\r\n'
    headers += b'\r\n'
    print(headers)
    return headers


# ** Do not modify code below this line.  You should add additional helper methods above this line.

# Utility functions
# You may use these functions to simplify your code.


def get_mime_type(file_path):
    """
    Try to guess the MIME type of a file (resource), given its path (primarily its file extension)

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If successful in guessing the MIME type, a string representing the content type, such as 'text/html'
             Otherwise, None
    :rtype: str or None
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
