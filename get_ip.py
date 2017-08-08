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
        self.i += 1
        return self.list[self.i]
    def scan_ip(self):
        file = open("ip.txt")
        self.list = file.read().split('|')
        self.list.pop()
        #print(self.list)
        file.close()
        self.i = 0
    def find_ip(self):
        with open("ip_range.txt") as fd:
            self.str = fd.read()
        self.read_from_file()


    def read_from_file(self):
        for i in self.str.splitlines():
            min, max = i.split('-')
            #print(min, max)
            #max = max[:-1]
            self.listmax.append(max)
            self.listmin.append(min)
        #print("end read from file")

    async def generate(self):
        index = random.randint(0, len(self.listmax)-1)
        min = self.listmin[index].split('.')
        max = self.listmax[index].split('.')
        l = []
        # for i in range(4):
            # l.append(random.randint(int(min[i]), int(max[i]))
        for i in range(4):
            l.append(random.randint(int(min[i]), int(max[i])))
        ip = ""
        for i in l:
            if ip == "":
                ip += str(i)
            else:
                ip += "." + str(i)
        return ip
test = IpCreator()
test.find_ip()
import asyncio
loop = asyncio.get_event_loop()
#print(loop.run_until_complete(test.generate()))

