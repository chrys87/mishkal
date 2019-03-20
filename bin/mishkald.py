#! /usr/bin/python2
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import os.path
import re
from glob import glob
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

scriptversion = '0.1'
AuthorName = "chrys"

TCP_IP = '127.0.0.1'
TCP_PORT = 6224
BUFFER_SIZE = 1024

def getTask(conn):
#  "Grab command-line arguments"
    options ={ "suggestion" : False, 
    "disableSemantic" : False,
    "disableStatistic" : False,
    "strip_tashkeel" : False,
    "text" : None,
    }

    data = conn.recv(BUFFER_SIZE)
    options["text"] = data.decode('utf8')

    # get the information
    if not data:
        return (options)

    #if text: print text.encode('utf8')
    return (options)


def start():
    acceptSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    acceptSock.bind((TCP_IP, TCP_PORT))
    acceptSock.listen(1)
    vocalizer = ArabicVocalizer.TashkeelClass()

    while True:
        conn, addr = acceptSock.accept()
        options = getTask(conn)
        text     = options['text']
        strip_tashkeel  = options['strip_tashkeel']
        disableSemantic = options['disableSemantic']
        disableStat     = options['disableStatistic']
            
        if not text:
            continue

        lines = text.split('\n')

        counter = 1

        if not strip_tashkeel: 
            if disableSemantic:
                vocalizer.disable_semantic_analysis()
            if disableStat:
                vocalizer.disable_stat_tashkeel()

        if len(lines)>0:
            line = lines[0]

        correct = 0
        incorrect = 0
        total = 0
        totLetters = 0
        LettersError = 0
        WLMIncorrect = 0
        percent = 0

        while line:
            if not line.startswith('#'):
                line = line.strip()
                lineCorrect = 0
                lineWLMIncorrect = 0
                if strip_tashkeel:
                    result = araby.strip_tashkeel(line)
                else:    #vocalize line by line
                    result = vocalizer.tashkeel(line)                    

                # print result.encode('utf8')
                counter += 1
             
                #~ print result.strip('\n').encode('utf8'),
                if text:
                    print result.strip('\n').encode('utf8')

            if counter<len(lines):
                line = lines[counter]
            else:
                line = None
        conn.send(result.encode('utf-8'))
        print result.strip('\n').encode('utf8')
        conn.close()
if __name__ == '__main__':
    start()
