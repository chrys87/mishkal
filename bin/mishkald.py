#! /usr/bin/python2
# -*- coding: UTF-8 -*-

import socket, os, sys

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

scriptversion = '0.2'
AuthorName = "chrys"

TCP_IP = '127.0.0.1'
TCP_PORT = 6123
BUFFER_SIZE = 256
DEBUG = False

def getTask(conn):
    options ={
        "text" : None,
    }
    try:
        data = conn.recv(BUFFER_SIZE)
        options["text"] = data.decode('utf8')
    except:
        conn.close()
        return (options)
        
    if not data:
        return (options)

    return (options)


def main():
    acceptSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    acceptSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    acceptSock.bind((TCP_IP, TCP_PORT))
    acceptSock.listen(1)
    vocalizer = ArabicVocalizer.TashkeelClass('/tmp/mishkal_cache/')
    vocalizer.set_log_level(50) # critical
    running = True
    while running:
        conn, addr = acceptSock.accept()
        options = getTask(conn)
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
            conn.send(result.encode('utf-8'))
            if DEBUG:
                print result.strip('\n').encode('utf8')
        finally:
            conn.close()

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
        



