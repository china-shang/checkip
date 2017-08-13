#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import asyncio
#loop = asyncio.get_event_loop()
#queue = asyncio.Queue(900)
# async def Puts(queue, list):
    # for i in list:
        #print("put", i)
        # await queue.put(i)
    # return 0

#asyncio.ensure_future(Puts(queue, list))

# loop.run_forever()
# loop.close()
import random


class IpCreator:
    def __init__(self):
        self.listmin = []
        self.listmax = []
        self.used = []
        # self.read_from_file()

    async def generate_for_scan(self):
        if(len(self.list) == 0):
            return None
        return self.list.pop(0)

    def scan_ip(self):
        file = open("ip.txt")
        self.list = file.read().split('|')
        self.list.pop()
        self.list.pop()
        print(self.list)
        # print(self.list)
        file.close()

    def getIndex(self):
        return self.index

    def find_ip(self):
        with open("ip_has_find.txt") as f:
            self.index = int(f.read())+1
        print("index", self.index)
        with open("ip_range.txt") as fd:
            self.str = fd.read()
        self.read_from_file()
        self.sum = 0
        for i in range(len(self.listmax)):
            min = self.listmin[i]
            max = self.listmax[i]
            for j in range(4):
                sum = 1
                if min[j] == max[j]:
                    pass
                else:
                    sum *= sum * int(max[j]) - int(min[j])
            self.sum += sum
        print("all ip : %d" % self.sum)
        self.lastIp = self.listmin[self.index]

    def read_from_file(self):
        for i in self.str.splitlines():
            min, max = i.split('-')
            t = []
            for i in min.split('.'):
                t.append(int(i))
            min = t

            t = []
            for i in max.split('.'):
                t.append(int(i))
            max = t

            #print(min, max)
            #max = max[:-1]
            self.listmax.append(max)
            self.listmin.append(min)
        #print("end read from file")

    async def generate(self):
        l = self.ip_add()
        ip = ""
        for i in l:
            if ip == "":
                ip += str(i)
            else:
                ip += "." + str(i)
        return ip

    def ip_add(self):
        t = self.lastIp
        self.lastIp[3] += 1
        for i in range(2, -1, -1):
            if self.lastIp[i + 1] == 256:
                self.lastIp[i + 1] = 0
                self.lastIp[i] = self.lastIp[i] + 1
        if self.lastIp[0] == 256:
            self.index += 1
            self.lastIp = self.listmin[self.index]
            return t
        for i in range(4):
            if self.lastIp[i] < self.listmax[self.index][i]:
                return t
        else:
            self.index += 1
            self.lastIp = self.listmin[self.index]
            return t
