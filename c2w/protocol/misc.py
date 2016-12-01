# -*- coding: utf-8 -*-

#Put useful function in this module


def decodeIpAdress(part1, part2, part3, part4) :
    data = str(part1) + '.' + str(part2) + '.' + str(part3) + '.' + str(part4)
    return data

def codeIpAdress(ipAdress) :
    data = ipAdress.split('.')
    return int(data[0]), int(data[1]), int(data[2]), int(data[3])
    
