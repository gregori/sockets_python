import selectors
import socket
import sys
import types

selector = selectors.DefaultSelector()  # cria um seletor

def accept_wrapper(sock):  # responsável por lidar com a 1a conexão
    conn, addr = sock.accept()  # conn é a conexão do cliente
    print('Aceitando conexão de:', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')  # contém dados da conexão e mensagens transmitidas
    events = selectors.EVENT_READ | selectors.EVENT_WRITE  # lida com eventos de leitura e escrita
    selector.register(conn, events, data=data)

def receive_data(key, mask):  #lida com os dados recebidos
    conn = key.fileobj  # obtem o socket com a conexão do cliente
    data = key.data # recebe os dados que o cliente enviou
    if mask & selectors.EVENT_READ:  # se for um evento de leitura 
        recv_data = conn.recv(1024)  # lê 1024 bytes de dados
        if recv_data is not None:  # se recebe dados ...
            data.outb += recv_data # acrescenta os dados recebidos à variável outb
        else: # se não recebe dados == terminar a conexão
            print('Fechando conexão com:', data.addr)
            selector.unregister(conn)
            conn.close()

    if mask & selectors.EVENT_WRITE:  # se tiver um evento de escrita
        if data.outb:  # se tiver dados para escrever
            print('Mandando mensagem', repr(data.outb), 'para', data.addr)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]  # manda os dados aos poucos

if len(sys.argv) != 3:  # se não receber 3 parâmetros na linha de comando (script, ip, porta)
    print('Uso:', sys.argv[0], '<host> <porta>') # imprime uma ajuda de uso do programa
    sys.exit(1)

host, port = sys.argv[1], sys.argv[2]  # recebe IP e porta da linha de comando
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # cria um socket IP/TCP
sock.bind((host, port))  # vincula ao IP e porta
sock.listen()  # escuta no IP e porta designados
print('Ouvindo em:', (host, port))
sock.setblocking(False)  # declara o socket como não bloqueante (aceita múlt conexões)
selector.register(sock, selectors.EVENT_READ, data=None)  # registra o socket para o seletor, para leitura

try:  # tente
    while True:  # executa infinitamente
        events = selector.select(timeout=None)  # equivale à linha do accept no echo-server
        for key, mask in events: # [(key, mask), (key, mask), (key, mask) ...] -> events
            if key.data is None:  # primeira vez que contactamos o cliente
                # executar o código de accept
                accept_wrapper(key.fileobj)
            else:  # senão, estamos recebendo dados
                # lidar com os dados recebidos
                receive_data(key, mask)
except KeyboardInterrupt:  # se o usuário digitar ctrl-c
    print('Recebi ctrl-c. Saindo do programa.')
finally:  # quando terminar o programa
    selector.close()  # fecha a conexão