#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import os
import ipaddress
import logging


class ipFactory:
    def __init__(self, q, IprangeStr):
        self.q = q
        self.ipRange = IprangeStr.split('\n')
        self.iprangelen = IprangeStr.count('\n')
        self.nowIndex = self.q.get()
        self.deadLine = self.nowIndex
        self.q.put((self.nowIndex + 1) % self.iprangelen)
        self.generateIP()
        self.GoodRange = set()
        self.getFromGood = True
        self.getGoodRange()
        print("Now Index:%4d" % self.nowIndex)

    def getGoodRange(self):
        with open("find_log0.txt") as f:
            s = f.readlines()
        self.GoodRange = set([int(i.split(":")[0]) for i in s])
        self._GoodRange = self.GoodRange.copy()
        if not self.getFromGood:
            self.GoodRange = set()

    def generateIP(self):
        l1 = [[ipaddress.ip_address(ip.split('-')[0]),
               ipaddress.ip_address(ip.split('-')[-1])]
              for ip in self.ipRange if '-' in ip]
        l2 = [[ipaddress.ip_network(net)[0],
               ipaddress.ip_network(net)[-1]]
              for net in self.ipRange if '/' in net]
        self.ipList = l1 + l2
        self.nowIp = self.ipList[self.nowIndex][0]

    def getIp(self):
        while self.nowIp > self.ipList[self.nowIndex][-1]:
            self.nowIndex = self.increaseIndex()
            self.nowIp = self.ipList[self.nowIndex][0]
            print("Now Index:%4d" % self.nowIndex)
        t = self.nowIp
        self.nowIp += 1
        return str(t)

    def increaseIndex(self):
        while True:
            if len(self.GoodRange) > 0:
                nowIndex = self.GoodRange.pop()
                return nowIndex
            else:
                nowIndex = self.q.get()
                if nowIndex == self.deadLine:
                    raise SystemExit
                self.q.put((nowIndex + 1) % self.iprangelen)
                if nowIndex not in self._GoodRange:
                    return nowIndex

    def getIndex(self):
        return self.nowIndex
