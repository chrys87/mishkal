#! /usr/bin/python2
# -*- coding: UTF-8 -*-

import socket, os, sys, select

base_dir = os.path.dirname(os.path.realpath(__file__))
#~ sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../support/'))
#~ sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../mishkal'))
#~ sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../')) # used for core
sys.path.append(os.path.join(base_dir, '../support/'))
sys.path.append(os.path.join(base_dir, '../mishkal'))
sys.path.append(os.path.join(base_dir, '../')) # used for core

import tashkeel.tashkeel as ArabicVocalizer
import core.adaat 
import pyarabic.araby as araby

scriptname = os.path.splitext(base_dir)[0]

scriptversion = '0.3'
AuthorName = "chrys"

TCP_IP = '127.0.0.1'
TCP_PORT = 6123
BUFFER_SIZE = 65536
DEBUG = False

sockets = []

def addSocket(conn):
    sockets.append(conn)

def closeSock(conn):
    try:
        conn.close()
    except:
        pass
    try:
        sockets.remove(conn)
    except:
        pass

def getData(conn):
    options ={
        "text" : None,
    }
    try:
        data = conn.recv(BUFFER_SIZE)
        while  '\00' not in data:
            data += conn.recv(BUFFER_SIZE)
        options["text"] = data.decode('utf8').replace('\00', '')
    except:
        closeSock(conn)
        return (options)
        
    if not data:
        return (options)

    return (options)

def main():
    acceptSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    acceptSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    acceptSock.bind((TCP_IP, TCP_PORT))
    acceptSock.listen(1)
    addSocket(acceptSock)
    vocalizer = ArabicVocalizer.TashkeelClass('/tmp/mishkal_cache/')
    vocalizer.set_log_level(50) # critical
    running = True
    while running:
        ready = select.select(sockets, [], [], -1)
        # only accept connection and skip
        if acceptSock in ready:        
            conn, addr = acceptSock.accept()
            acceptSock(conn)
            ready.remove(acceptSock)
        # for better reading skip if there are no more requests
        if ready == []:
            continue
        # handle outstanding requests
        for conn in ready:
            options = getData(conn)
            text = options['text']

            if not text:
                continue

            lines = text.split('\n')

            result = u''
            for line in lines:
                line = line.strip()
                if line == '':
                    continue
                if line.startswith('#'):
                    continue

                lineResult = vocalizer.tashkeel(line)                    
                result += ' ' + lineResult

                if DEBUG:
                    if text:
                        print lineResult.strip('\n').encode('utf8')
            try:
                answer = result + '\00'
                conn.send(answer.encode('utf-8'))
                if DEBUG:
                    print result.strip('\n').encode('utf8')
            finally:
                closeSock(conn)
            if sockets == []:
                return
if __name__ == '__main__':
    try:
        print 'start as daemon'
        pid = "/run/mishkal.pid"
        from daemonize import Daemonize
        daemon = Daemonize(app="mishkald", pid=pid, action=main)
        daemon.start()
    except Exception as e:
        print 'starting daemon failed, start in foreground'
        print e
        main()
        



