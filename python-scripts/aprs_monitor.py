#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import time
from ax25lib import ax25lib
from aprs_parser import aprs_parser
from datetime import datetime

parser=aprs_parser()
port=serial.Serial(port='/dev/ttyUSB0',baudrate=9600, timeout=1.0)
eof = "\xff\xff\xff"
undimCmd = "dim=60"
callsign="SQ9MDD-15"
call_list = ['N0CALL','N0CAL']
icon_list = ['!','\"','#','$','%','&','\'','(',')','*','+',',','-','.','/','0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?','@','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','[','\\',']','^','_','`','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','{','|','}','~']

# !"#$%&'()*+,-.0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~

def main():
    port.write("page start" + eof)
    port.write(undimCmd + eof)
    port.write('settings.callsign.txt="' + callsign + '"' + eof)
    #port.write('bauds="115200"')
    while True:
        time.sleep(1)

def dane(dane):
    znak = ""
    icon_idx = 4
    icon_tbl = 0
    icon_symb = ""
    il_powtorzen = 0
    comment = ""
    global call_list
    global icon_list
    
    if dane['data'][0] == ";":                              # obiekt ;439.275WM*111111z5210.73N/02103.39Er
        znak = dane['data'][1:10]
        icon_symb = dane['data'][36]
        comment = dane['data'][37:]
        if dane['data'][26] != "/":
            icon_tbl = 94
            
    elif dane['data'][0] == ")":                            # item )TST!5215.09N\02055.64E;Test item
        mark = dane['data'].find('!') 
        znak = dane['data'][1:mark]
        icon_symb = dane['data'][mark+19]
        comment = dane['data'][mark+20:]
        if dane['data'][mark+9] != "/":
            icon_tbl = 94       
        
    elif dane['data'][0] == "@" or dane['data'][0] == "/":  # zwykle plus czas -> @081407z5214.36N/02105.83E#
        znak = dane['source']
        icon_symb = dane['data'][26]
        comment = dane['data'][27:]
        if dane['data'][16] != "/":
            icon_tbl = 94
            
    elif dane['data'][0] == "}":                            # dane od stacji trzecich
        mark = dane['data'].find('>') 
        znak = dane['data'][1:mark]
        icon_symb = 'D'
        comment = dane['data'][mark:]
        
    elif dane['data'][0] == ">":                            # status
        znak = dane['source']
        icon_symb = '{'
        comment = dane['data'][1:]
        
    elif dane['data'][0] == ":":                            # wiadomosc zmiana ikonki na mail
        znak = dane['source']
        icon_symb = ']'
        comment = dane['data'][1:]
            
    elif dane['data'][0] == "`" or dane['data'][0] == "'":  # Mic-E decode z nowa biblioteka Tomka SQ5T
        znak = dane['source']
        wynik=parser.parser(dane['destination'],dane['data'])      
        icon_symb = wynik['symbol']
        comment = wynik['comment']
        if wynik['symbol_table'] != "/":
            icon_tbl = 94          

        
    else:
        znak = dane['source']                               # zwykle =5216.13N/02102.22E>
        icon_symb = dane['data'][19]
        comment = dane['data'][20:]
        if dane['data'][9] != "/":
            icon_tbl = 94
            
    icon_idx = icon_list.index(icon_symb)
    icon_gfx = icon_idx + 4 + icon_tbl
    for x in call_list:
        if x == znak:
            il_powtorzen =+ 1

    if il_powtorzen <= 0:
        # 1 linia
        #port.write('click m1,1' + eof)
        port.write('click reflist,0' + eof)
        port.write('stationlist.p0.pic=' + str(icon_gfx) + '' + eof)
        port.write('stationlist.l9.txt="'+ datetime.now().strftime('%H:%M:%S') + '"' + eof)
        port.write('stationlist.l1.txt="' + znak + '"' + eof)
        port.write('storage.t0.txt="' + dane['via'] + '"' + eof)
        port.write('storage.t8.txt="' + comment + '"' + eof)
        
        call_list.append(znak)
        
    if len(call_list) > 8:
        call_list.pop(0)
    #print icon_symb + ' / ' + str(icon_idx) + '/' + str(icon_gfx) + '-' + str(icon_tbl)
    #print datetime.now().strftime('%H:%M:%S')    
    print dane['source'] + " | " + dane['via'] + " | " + dane['data']
    
if __name__ == '__main__':
    callsign = callsign.upper() #set to upper letters
    #via = via.upper() #set default path to upper letters
    ax25 = ax25lib(type="tcp",host="127.0.0.1",port=8002,callback=dane)

    main()
