import socket

server = '127.0.1.1'  # endereço do servidor ao qual vamos conectar
port = 12345   # porta à qual vamos conectar

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:  # abre socket TCP
    sock.connect((server, port))  # conecta ao servidor
    sock.sendall(b'Hello, world!')  # envia mensagem ao servidor
    data = sock.recv(1024)   # recebe 1024 bytes do servidor

print('Recebido: ', repr(data))   # imprime dados recebidos

