#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import math
import sys
from re import findall

class aprs_parser:
    def __init__(self):
        self.data = []

        if sys.version_info[0] >= 3:
            self.string_type = (str, )
            self.string_type_parse = self.string_type + (bytes, )
            int_type = int
        else:
            self.string_type = (str, unicode)
            self.string_type_parse = self.string_type
            int_type = (int, long)


        # Mic-e message type table

        self.MTYPE_TABLE_STD = {
            "111": "M0: Off Duty",
            "110": "M1: En Route",
            "101": "M2: In Service",
            "100": "M3: Returning",
            "011": "M4: Committed",
            "010": "M5: Special",
            "001": "M6: Priority",
            "000": "Emergency",
            }
        self.MTYPE_TABLE_CUSTOM = {
            "111": "C0: Custom-0",
            "110": "C1: Custom-1",
            "101": "C2: Custom-2",
            "100": "C3: Custom-3",
            "011": "C4: Custom-4",
            "010": "C5: Custom-5",
            "001": "C6: Custom-6",
            "000": "Emergency",
            }



    def weather_decode(data):
        # m/km/C
        # 247/005g012t066r000p071P...h66b07916Stacja pogodowa Jablonna
        print(data)
        wind_dir=data[0:2]
        wind_speed=int(int(data[4:7])*1.85)
        print(wind_speed)
        wind_peak=int(int(data[8:11])*1.6)
        print(wind_peak)
        temperature=round(5/9*(int(data[12:15])-32),1)
        print(temperature)
        rain_1h=round(int(data[16:19])*2.54,1)
        print(rain_1h)
        print(data[20:23])
        rain_24h=round(int(data[20:23])*2.54,1)
        print(rain_24h)

    def parser(self,to_call,line):

        # if x in 'bc':
        #     # Fall-through by not using elif, but now the default case includes case 'a'!
        # elif x in 'xyz':
        #     # Do yet another thing


        if line[0] == '!':
            # Position without timestamp (no APRS messaging), or Ultimeter 2000 WX Station
            print("x")
        elif line[0] == '"':
            # [Unused]
            print("xy")
        elif line[0] == '#':
            # Peet Bros U-II Weather Station
            print("x")
        elif line[0] == '$':
            # Raw GPS data or Ultimeter 2000
            print("x")
        elif line[0] == '%':
            # Agrelo DFJr / MicroFinder
            print("x")
        elif line[0] == '&':
            # [Reserved — Map Feature]
            print("x")
        elif line[0] == '`':
            # Old Mic-E Data (but Current data for TM-D700)
            return(self.parse_mice(to_call, line[1:]))
        elif line[0] == '(':
            # [Unused]
            print("x")
        elif line[0] == ')':
            # Item
            print("x")
        elif line[0] == '*':
            # Peet Bros U-II Weather Station
            print("x")
        elif line[0] == '+':
            # [Reserved — Shelter data with time]
            print("x")
        elif line[0] == ',':
            # Invalid data or test data
            print("x")
        elif line[0] == '-':
            # [Unused]
            print("x")
        elif line[0] == '.':
            # [Reserved — Space weather]
            print("x")
        elif line[0] == '/':
            # Position with timestamp (no APRS messaging)
            print("x")
        elif line[0] in '0123456789':
            # [Do not use]
            print("x")
        elif line[0] == ':':
            # Message
            print("x")
        elif line[0] == ';':
            # Object
            print("x")
        elif line[0] == '<':
            # Station Capabilities
            print("x")
        elif line[0] == '=':
            # Position without timestamp (with APRS messaging)
            print("x")
        elif line[0] == '>':
            # Status
            print("x")
        elif line[0] == '?':
            # Query
            print("x")
        elif line[0] == '@':
            print("małpa")
            if line[7] == "z":
                aprs_time=line[3:7]
                aprs_day=line[1:3]
                print(aprs_time)
                print(aprs_day)
                lon=line[8:16]
                lat=line[17:26]
                print(lon)
                print(lat)
                if line[16:17] == "\\":
                    fix_lat_lon=False
                else:
                    fix_lat_lon=True
                if line[26:27] == "_":
                    weather = weather_decode(line[27:])

        elif line[0] in 'ABCDEFGHIJKLMNOPQR':
            print("x")
            # [Do not use]
        elif line[0] == 'T':
            # Telemetry data
            print("x")
        elif line[0] in 'UVWXYZ':
            # [Do not use]
            print("x")
        elif line[0] == '[':
            # Maidenhead grid locator beacon (obsolete)
            print("x")
        elif line[0] == '\'':
            # [Unused]
            print("x")
        elif line[0] == ']':
            # [Unused]
            print("x")
        elif line[0] == '^':
            # [Unused]
            print("x")
        elif line[0] == '_':
            # Weather Report (without position)
            print("x")
        elif line[0] == '‘':
            # Current Mic-E Data (not used in TM-D700)
            print("x")
        elif line[0] in 'abcdefghijklmnopqrstuvwxyz':
            # [Do not use]
            print("x")
        elif line[0] == '{':
            # User-Defined APRS packet format
            print("xASDF")
        elif line[0] == '|':
            # [Do not use — TNC stream switch character]
            print("x")
        elif line[0] == '}':
            # Third-party traffic
            print("x")
        elif line[0] == '~':
            # [Do not use — TNC stream switch character]
            print("x")
        else:
            print("unsupported")



    def parse_comment_telemetry(self,text):
        """
        Looks for base91 telemetry found in comment field
        Returns [remaining_text, telemetry]
        """
        parsed = {}
        match = re.findall(r"^(.*?)\|([!-{]{4,14})\|(.*)$", text)

        if match and len(match[0][1]) % 2 == 0:
            text, telemetry, post = match[0]
            text += post

            temp = [0] * 7
            for i in range(7):
                temp[i] = self.to_decimal(telemetry[i*2:i*2+2])

            parsed.update({
                'telemetry': {
                    'seq': temp[0],
                    'vals': temp[1:6]
                    }
                })

            if temp[6] != '':
                parsed['telemetry'].update({
                    'bits': "{0:08b}".format(temp[6] & 0xFF)[::-1]
                    })

        return (text, parsed)

    def parse_dao(self,body, parsed):
        match = re.findall("^(.*)\!([\x21-\x7b])([\x20-\x7b]{2})\!(.*?)$", body)
        if match:
            body, daobyte, dao, rest = match[0]
            body += rest

            parsed.update({'daodatumbyte': daobyte.upper()})
            lat_offset = lon_offset = 0

            if daobyte == 'W' and dao.isdigit():
                lat_offset = int(dao[0]) * 0.001 / 60
                lon_offset = int(dao[1]) * 0.001 / 60
            elif daobyte == 'w' and ' ' not in dao:
                lat_offset = (self.to_decimal(dao[0]) / 91.0) * 0.01 / 60
                lon_offset = (self.to_decimal(dao[1]) / 91.0) * 0.01 / 60

            parsed['latitude'] += lat_offset if parsed['latitude'] >= 0 else -lat_offset
            parsed['longitude'] += lon_offset if parsed['longitude'] >= 0 else -lon_offset

        return body


    def to_decimal(self,text):
        """
        Takes a base91 char string and returns decimal
        """

        if not isinstance(text, self.string_type):
            print("expected str or unicode, %s given" % type(text))

        if findall(r"[\x00-\x20\x7c-\xff]", text):
            print("invalid character in sequence")

        text = text.lstrip('!')
        decimal = 0
        length = len(text) - 1
        for i, char in enumerate(text):
            decimal += (ord(char) - 33) * (91 ** (length - i))

        return decimal if text != '' else 0

    # Mic-encoded packet
    #
    # 'lllc/s$/.........         Mic-E no message capability
    # 'lllc/s$/>........         Mic-E message capability
    # `lllc/s$/>........         Mic-E old posit
    def parse_mice(self,dstcall, body):
        parsed = {'format': 'mic-e'}

        dstcall = dstcall.split('-')[0]

        # verify mic-e format
        if len(dstcall) != 6:
            print("dstcall has to be 6 characters")
            return None
        if len(body) < 8:
            print("packet data field is too short")
            return None
        if not re.match(r"^[0-9A-Z]{3}[0-9L-Z]{3}$", dstcall):
            print("invalid dstcall")
            return None
        if not re.match(r"^[&-\x7f][&-a][\x1c-\x7f]{2}[\x1c-\x7d]"
                        r"[\x1c-\x7f][\x21-\x7e][\/\\0-9A-Z]", body):
            print("invalid data format")
            return None

        # get symbol table and symbol
        parsed.update({
            'symbol': body[6],
            'symbol_table': body[7]
            })

        # parse latitude
        # the routine translates each characters into a lat digit as described in
        # 'Mic-E Destination Address Field Encoding' table
        tmpdstcall = ""
        for i in dstcall:
            if i in "KLZ":  # spaces
                tmpdstcall += " "
            elif ord(i) > 76:  # P-Y
                tmpdstcall += chr(ord(i) - 32)
            elif ord(i) > 57:  # A-J
                tmpdstcall += chr(ord(i) - 17)
            else:  # 0-9
                tmpdstcall += i

        # determine position ambiguity
        match = re.findall(r"^\d+( *)$", tmpdstcall)
        if not match:
            print("invalid latitude ambiguity")
            return None

        posambiguity = len(match[0])
        parsed.update({
            'posambiguity': posambiguity
            })

        # adjust the coordinates be in center of ambiguity box
        tmpdstcall = list(tmpdstcall)
        if posambiguity > 0:
            if posambiguity >= 4:
                tmpdstcall[2] = '3'
            else:
                tmpdstcall[6 - posambiguity] = '5'

        tmpdstcall = "".join(tmpdstcall)

        latminutes = float(("%s.%s" % (tmpdstcall[2:4], tmpdstcall[4:6])).replace(" ", "0"))
        latitude = int(tmpdstcall[0:2]) + (latminutes / 60.0)

        # determine the sign N/S
        latitude = -latitude if ord(dstcall[3]) <= 0x4c else latitude

        parsed.update({
            'latitude': latitude
            })

        # parse message bits

        mbits = re.sub(r"[0-9L]", "0", dstcall[0:3])
        mbits = re.sub(r"[P-Z]", "1", mbits)
        mbits = re.sub(r"[A-K]", "2", mbits)

        parsed.update({
            'mbits': mbits
            })

        # resolve message type

        if mbits.find("2") > -1:
            parsed.update({
                'mtype': self.MTYPE_TABLE_CUSTOM[mbits.replace("2", "1")]
                })
        else:
            parsed.update({
                'mtype': self.MTYPE_TABLE_STD[mbits]
                })

        # parse longitude

        longitude = ord(body[0]) - 28  # decimal part of longitude
        longitude += 100 if ord(dstcall[4]) >= 0x50 else 0  # apply lng offset
        longitude += -80 if longitude >= 180 and longitude <= 189 else 0
        longitude += -190 if longitude >= 190 and longitude <= 199 else 0

        # long minutes
        lngminutes = ord(body[1]) - 28.0
        lngminutes += -60 if lngminutes >= 60 else 0

        # + (long hundredths of minutes)
        lngminutes += ((ord(body[2]) - 28.0) / 100.0)

        # apply position ambiguity
        # routines adjust longitude to center of the ambiguity box
        if posambiguity is 4:
            lngminutes = 30
        elif posambiguity is 3:
            lngminutes = (math.floor(lngminutes/10) + 0.5) * 10
        elif posambiguity is 2:
            lngminutes = math.floor(lngminutes) + 0.5
        elif posambiguity is 1:
            lngminutes = (math.floor(lngminutes*10) + 0.5) / 10.0
        elif posambiguity is not 0:
            print("Unsupported position ambiguity: %d" % posambiguity)
            return None

        longitude += lngminutes / 60.0

        # apply E/W sign
        longitude = 0 - longitude if ord(dstcall[5]) >= 0x50 else longitude

        parsed.update({
            'longitude': longitude
            })

        # parse speed and course
        speed = (ord(body[3]) - 28) * 10
        course = ord(body[4]) - 28
        quotient = int(course / 10.0)
        course += -(quotient * 10)
        course = course*100 + ord(body[5]) - 28
        speed += quotient

        speed += -800 if speed >= 800 else 0
        course += -400 if course >= 400 else 0

        speed *= 1.852  # knots * 1.852 = kmph
        parsed.update({
            'speed': speed,
            'course': course
            })

        # the rest of the packet can contain telemetry and comment

        if len(body) > 8:
            body = body[8:]

            # check for optional 2 or 5 channel telemetry
            match = re.findall(r"^('[0-9a-f]{10}|`[0-9a-f]{4})(.*)$", body)
            if match:
                hexdata, body = match[0]

                hexdata = hexdata[1:]           # remove telemtry flag
                channels = len(hexdata) / 2     # determine number of channels
                hexdata = int(hexdata, 16)      # convert hex to int

                telemetry = []
                for i in range(channels):
                    telemetry.insert(0, int(hexdata >> 8*i & 255))

                parsed.update({'telemetry': telemetry})

            # check for optional altitude
            match = re.findall(r"^(.*)([!-{]{3})\}(.*)$", body)
            if match:
                body, altitude, extra = match[0]

                altitude = self.to_decimal(altitude) - 10000
                parsed.update({'altitude': altitude})

                body = body + extra

            # attempt to parse comment telemetry
            body, telemetry = self.parse_comment_telemetry(body)

            parsed.update(telemetry)

            # parse DAO extention
            body = self.parse_dao(body, parsed)

            # rest is a comment
            parsed.update({'comment': body.strip(' ')})

        return (parsed)
