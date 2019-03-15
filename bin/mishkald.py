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

                
scriptname = os.path.splitext(base_dir)[0]

scriptversion = '0.1'
AuthorName = "chrys"

TCP_IP = '127.0.0.1'
TCP_PORT = 6127
BUFFER_SIZE = 1024

def getTask(conn):
#  "Grab command-line arguments"
    options ={ "suggestion" : False, 
    "ignore" : False,
    "limit" : False, 
    "compare" : False,
    "disableSyntax" : False,
    "disableSemantic" : False,
    "disableStatistic" : False,
    "strip_tashkeel" : False,
    "reducedTashkeel" : False,  
    "progress" : False,  
    "train" : False,  
    "nocache" : False,
    "text" : None,
    }

    data = conn.recv(BUFFER_SIZE)
    options["text"] = data.decode('utf8')

    # get the information
    if not data:
        return (options)

    #if text: print text.encode('utf8')
    return (options)

import tashkeel.tashkeel as ArabicVocalizer

def start():
    acceptSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    acceptSock.bind((TCP_IP, TCP_PORT))
    acceptSock.listen(1)

    while True:
        conn, addr = acceptSock.accept()
        options = getTask(conn)
        text     = options['text']
        strip_tashkeel  = options['strip_tashkeel']
        nocache         = options['nocache']
        reducedTashkeel = options['reducedTashkeel']
        disableSyntax   = options['disableSyntax']
        disableSemantic = options['disableSemantic']
        disableStat     = options['disableStatistic']
        ignore = options['ignore']
        limit  = options['limit']
        compare = options['compare']
        progress = options['progress']
        enable_syn_train = options['train']
            
        if not text:
            continue

        lines = text.split('\n')
        # all things are well, import library
        import core.adaat 
        import pyarabic.araby as araby

        counter = 1
        if not limit : 
            limit = 100000000
        if not strip_tashkeel: 
            vocalizer = ArabicVocalizer.TashkeelClass()
            if nocache : 
                vocalizer.disable_cache()
                #print "nocache"
            if ignore : 
                vocalizer.disable_last_mark()
            if disableSemantic:
                vocalizer.disable_semantic_analysis()
            if disableSyntax:
                vocalizer.disable_syntaxic_analysis()
            if disableStat:
                vocalizer.disable_stat_tashkeel()
            if enable_syn_train:
                vocalizer.enable_syn_train()
                #print "mishkal-console, vocalizer.anasynt.syntax_train_enabled", vocalizer.anasynt.syntax_train_enabled

        #vocalizer.disableShowCollocationMark()
        #print "show delimiter", vocalizer.collo.showDelimiter
        #nolimit = True
        nolimit = False

        if len(lines)>0:
            line = lines[0]

        correct = 0
        incorrect = 0
        total = 0
        totLetters = 0
        LettersError = 0
        WLMIncorrect = 0
        percent = 0
        if compare:
            #dispaly stats for the current line
            print "id\tfully Correct\tStrip Correct\tfully WER\tStrip WER\tLER\tTotal\tline Fully correct\tline Strip correct\tLine"
            
        while line and (nolimit or counter <= limit):
            if not line.startswith('#'):
                line = line.strip()
                lineCorrect = 0
                lineWLMIncorrect = 0
                if strip_tashkeel:
                    result = araby.strip_tashkeel(line)
                else:    #vocalize line by line
                    if not compare:
                        result = vocalizer.tashkeel(line)                    
                    if compare:
                        inputVocalizedLine = line
                        inputlist = vocalizer.analyzer.tokenize(inputVocalizedLine)
                        inputUnvocalizedLine = araby.strip_tashkeel(line)
                        vocalized_dict = vocalizer.tashkeel_ouput_html_suggest(inputUnvocalizedLine)


                        #stemmer=tashaphyne.stemming.ArabicLightStemmer()
                        #~texts = vocalizer.analyzer.split_into_phrases(inputVocalizedLine)
                        #~inputlist =[]
                        #~for txt in texts:
                            #~inputlist += vocalizer.analyzer.text_tokenize(txt)
                        outputlist = [x.get("chosen",'') for x in vocalized_dict]
                        result = u" ".join(outputlist)
                        outputlistsemi = [x.get("semi",'') for x in vocalized_dict]
                        total += len(inputlist)
                        lineTotal = len(inputlist)
                        if len(inputlist) != len(outputlist):
                            print "lists haven't the same length"
                            print len(inputlist), len(outputlist)
                            print u"#".join(inputlist).encode('utf8')
                            print u"#".join(outputlist).encode('utf8')
                        else:
                            for inword, outword, outsemiword in zip(inputlist, outputlist, outputlistsemi):
                                simi = araby.vocalized_similarity(inword, outword)
                                if simi<0:
                                    LettersError += -simi
                                    incorrect    += 1
                                    # evaluation without last haraka
                                    simi2 = araby.vocalized_similarity(inword, outsemiword)
                                    if simi2<0: 
                                        WLMIncorrect     += 1
                                        lineWLMIncorrect += 1                                
                                else:
                                    correct += 1
                                    lineCorrect  += 1
                        
                #compare resultLine and vocalizedLine
                if reducedTashkeel:
                    result = araby.reduceTashkeel(result)
                # print result.encode('utf8')
                counter += 1
             
                #~ print result.strip('\n').encode('utf8'),
                if text:
                    #conn.send(result.encode('utf-8'))
                    print result.strip('\n').encode('utf8')
                    #conn.close()

            if counter<len(lines):
                line = lines[counter]
            else:
                line = None
        conn.send(result.encode('utf-8'))
        print result.strip('\n').encode('utf8')
        conn.close()
if __name__ == '__main__':
    start()
