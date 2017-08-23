#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import os


class ipFactory:
    def __init__(self, start, q, IprangeStr, *, increasing=True):
        self.str = IprangeStr
        self.increasing = increasing
        self.index = start

        self.q = q
        self.hasFind = 0
        self.listmin = []
        self.listmax = []
        self.used = []
        # self.read_from_file()

    async def getip_for_scan(self):
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
        print("pid:%d\tindex:" % os.getpid(), self.index)
        # with open("ip_range.txt") as fd:
            #self.str = fd.read()
        self.read_from_file()
        #self.sum = 0
        #for i in range(len(self.listmax)):
            #min = self.listmin[i]
            #max = self.listmax[i]
            #t = 0
            #for j in range(4):
                #if min[j] == max[j]:
                    #pass
                #else:
                    #t += (int(max[j]) - int(min[j])) * 256**(3 - j)
            #self.sum += t
        #print("all ip : %d" % self.sum)
        self.indexSum = len(self.listmax) - 1
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

    async def getip(self):
        l = self.ip_increasing()
        ip = ""
        for i in l:
            if ip == "":
                ip += str(i)
            else:
                ip += "." + str(i)
        return ip

    def ip_increasing(self):
        num = self.q.get()
        if num <= 0:
            print("Find Done")
            self.q.put(num)
            raise KeyboardInterrupt
        self.q.put(num)
        t = self.lastIp
        self.lastIp[3] += 1
        for i in range(2, -1, -1):
            if self.lastIp[i + 1] == 256:
                self.lastIp[i + 1] = 0
                self.lastIp[i] = self.lastIp[i] + 1
        if self.lastIp[0] == 256:
            if self.increasing:
                self.index = (self.index + 1) % self.indexSum
            else:
                self.index = (self.index - 1) % self.indexSum
            self.hasFind += 1
            num = self.q.get()
            self.q.put(num - 1)
            print("pid:%d\tleave index :" % os.getpid(), num)

            self.lastIp = self.listmin[self.index]
            return t
        for i in range(4):
            if self.lastIp[i] < self.listmax[self.index][i]:
                return t
        else:
            num = self.q.get()
            self.q.put(num - 1)
            if self.increasing:
                self.index = (self.index + 1) % self.indexSum
            else:
                self.index = (self.index - 1) % self.indexSum

            self.hasFind += 1
            self.lastIp = self.listmin[self.index]
            print("pid:%d\tleave index :" % os.getpid(), num)
            return t
