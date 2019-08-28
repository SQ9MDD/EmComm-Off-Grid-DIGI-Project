#!/usr/bin/env python
# -*- coding: utf-8 -*-

# skrypt podmienia jednorazowo plik z ramką status na ramke bikon digipitera
# uzywany jako moduł do konfiguracji DIGI Przewoźnego
# przykladowa komenda: SET-5215.49-02055.59 po lower: ->set-5215.49-02055.59<-

from ax25lib import ax25lib
import time
import sqlite3
import datetime

myCallsign = "SQ9MDD-15"
myPath = "RFONLY"
savedPos = 0

def main():
    while True:
        time.sleep(1)

def send_answer(kto,message):
    time.sleep(1)
    c.execute("select ack from ack order by ack desc")
    wynik = c.fetchone()
    if (wynik):
        acksqlite = str(int(wynik[0])+1)
    else:
        acksqlite = "1"

    msg=":"+kto+":"+message+"{"+acksqlite
    ax25.send(source=myCallsign,destination="APSQ5T",rpt=myPath,message=msg.encode("ascii"))
    c.execute("insert into ack values('"+kto+"',"+acksqlite+",3)")
    c.execute("select * from ack")
    rows=c.fetchall()

def dane(dane):
    global savedPos
    # print dane['source'] + " | " + dane['via'] + " | " + dane['data']
    if(dane['data'].startswith(":"+myCallsign)):
        msg_1 = dane['data'].split(":")[2].split("{")
        #print "Receive message from ",dane['source']
        #print "Message: ",msg_1[0]
        if len(msg_1) == 1:
            if msg_1[0].startswith("ack"):
                ack_value = int(msg_1[0].replace("ack",""))
                zrodlo = dane['source']
                cmd="delete from ack where myCallsign='"+zrodlo+"' and ack="+str(ack_value)
                c.execute(cmd)
            return
        ack = msg_1[1]
        dst_call = dane['source']
        while len(dst_call) < 9:
            dst_call = dst_call + chr(0x20)
        msg_ack = ":%s:ack%s" % (dst_call,ack)
        ax25.send(source=myCallsign,destination="APSQ5T",rpt=myPath,message=msg_ack) #send ack to source myCallsign

        poleData = msg_1[0]
        if poleData[0:3] == "SET" and savedPos == 0:
            #print "JEST KOMENDA"
            lat = poleData[4:11]
            lon = poleData[12:20]
            # przykladowa ramka RAW: !5149.42N/02125.53E# DIGI Polowe Fill In
            # przygotowana ramka do wrzucenia w plik
            raw_frame = "!" + lat + "N/" + lon + "E# Tymczasowe DIGI Polowe"
            f = open("/tmp/beacon.raw","w")
            f.write(raw_frame)
            f.close()
            #print "Wysylam odpowiedz"
            send_answer(dst_call,"OK - pozycja zapisana czekaj na bikon")
            savedPos = 1

        elif poleData[0:3] == "SET" and savedPos == 1:
            #print "Juz skonfigurowane"
            send_answer(dst_call,"ERR - digi juz skonfigurowane")

if __name__ == '__main__':
    myCallsign = myCallsign.upper() #set to upper letters
    myPath = myPath.upper() #set default path to upper letters
    con = sqlite3.connect(":memory:",check_same_thread = False)
    c = con.cursor()
    c.execute("create table ack (myCallsign text, ack int, ack_count int)")
    ax25 = ax25lib(type="tcp",host="127.0.0.1",port=8002,callback=dane)

    main()
