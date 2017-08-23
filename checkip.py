#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import warnings
import aiohttp
import os
import ssl
import time
import get_ip
import multiprocessing
from multiprocessing import Process, Queue
import random

ipList = Queue()


class Test_Ip:
    def __init__(self, loop, ipfactory):
        self.loop = loop
        self.indexDict = dict()
        self.d = dict()
        self.ipfactory = ipfactory
        self.q = asyncio.Queue()
        self.max = 64
        self.now = 1
        self._running = True
        self.future = None
        # self.scan = True
        self.scan = False
        self.num = 0
        self.ipSum = 0
        self.ipSuccessSum = 0

        if(self.scan):
            self.now = 0
            self.ipfactory.scan_ip()
            self.generateIp = self.ipfactory.generate_for_scan
        else:
            #file_name = "ip" + str(self.num) + ".txt"
            #self.f = open(file_name, 'w')
            self.ipfactory.find_ip()
            self.generateIp = self.ipfactory.generate

    async def test(self, ip):
        start_time = time.time()

        try:
            async with self.session.request("GET", "https://%s/_gh/" % ip, headers={"Host": "my-project-1-1469878073076.appspot.com"}, ) as resp:
                headers = resp.headers
                server_type = headers.get('Server', '')
                len = headers.get('Content-Length', '')

                if int(len) == 86:
                    end_time = time.time()
                    time_used = end_time - start_time
                    self.d[ip] = time_used
                    return True

        except (KeyboardInterrupt, SystemExit) as e:
            print("this worker")
            if self._running:
                self._running = False
                self.loop.create_task(self.stop())
        except BaseException as e:
            return False

    async def worker(self):
        try:
            while self._running:
                ip = await self.generateIp()
                self.index = self.ipfactory.getIndex()
                if(ip is None):
                    break

                if ip not in self.d:
                    self.d[ip] = 0
                success = await self.test(ip)
                self.ipSum += 1

                if success:
                    if self.index not in self.indexDict:
                        self.indexDict[self.index] = 1
                    else:
                        self.indexDict[self.index] += 1

                    self.ipSuccessSum += 1
                    print(
                        "Process:", self.num, "\tspend time:%ds\t" %
                        (time.time() - self.start_time))
                    print(ip, "\tdelay:\t%.2f" % self.d[ip])
                    print(
                        "Success:%4d\tAll:%4d" %
                        (self.ipSuccessSum, self.ipSum))

                    if ip in self.d:
                        del self.d[ip]
                    await self.q.put(ip)

        except (KeyboardInterrupt, SystemExit) as e:
            print("this worker")
            if self._running:
                self._running = False
                self.loop.create_task(self.stop())
        finally:
            self.now -= 1
            if not self.future.done():
                self.future.set_result("need task")

    async def Server(self):
        self.Running = asyncio.Future()
        self.startindexIndex = self.ipfactory.getIndex()
        context = ssl.create_default_context()
        context.check_hostname = False

        if(not self.scan):
            self.loop.create_task(self.SaveIp())

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl_context=context, force_close=True), conn_timeout=1, read_timeout=0.8) as self.session:
            self.start_time = time.time()
            #print("create session Success")
            #print("startindex Scan Ip")
            while self._running:
                if self.now < self.max:
                    self.now += 1
                    #print("create task at", self.now)
                    # print("startindex Task Sum: ", self.now)
                    self.loop.create_task(self.worker())
                    if self.now == self.max:
                        self.future = asyncio.Future()
                else:
                    await self.future

    async def stop(self):
        self._running = False
        if self.future is not None and not self.future.done():
            self.future.set_result("need stop")
        while self.now > 0:
            await asyncio.sleep(0.2)
            if(self.now == 1):
                await self.q.put("end")
            print("stopping  wait %2d worker stop" % self.now)
        # if(self.scan is False):
            # self.f.close()
            #print("file closed")
        #file_name = "ip_has_find" + str(self.num) + ".txt"
        #with open(file_name, "w") as f:
            #f.write(str(self.index))
        #print("index saved:", self.index)
        file_name = "find_log" + str(self.num) + ".txt"
        with open(file_name, "a") as f:
            for i in self.indexDict.items():
                print(i[0], ":", i[1])
                f.write(str(i[0]) + ":" + str(i[1]) + "\n")
        if not self.Running.done():
            self.Running.set_result("stoped")
        return True

    async def SaveIp(self):
        while self._running:
            ip = await self.q.get()
            if ip != "end":
                ipList.put(ip)
        self.now -= 1

    async def SuccessStop(self):
        if self.Running.done():
            pass
        else:
            await self.Running
        print("Success stop")
        return True


class CheckProcess(Process):
    def __init__(self, startindex, q, iprange, *, increasing=True):
        self.startindex = startindex
        self.q = q
        self.iprange = iprange
        self.increasing = increasing
        super().__init__()

    def run(self):
        try:
            loop = asyncio.get_event_loop()
            ipfactory = get_ip.ipFactory(self.startindex, self.q, self.iprange,
                                         increasing=self.increasing)
            testip = Test_Ip(loop, ipfactory)
            loop.create_task(testip.Server())
            loop.run_until_complete(testip.SuccessStop())

        except (KeyboardInterrupt, SystemExit) as e:
            loop.create_task(testip.stop())
            loop.run_until_complete(testip.SuccessStop())

        finally:
            loop.close()
            print("Task exit")


class Task:
    def __init__(self, startindex, iprange):
        self.startindex = startindex
        self.ipfactory = iprange
        self.q = Queue()
        self.q.put(perProcess * 2)

    def start(self):
        p1 = CheckProcess(self.startindex, self.q, self.ipfactory)
        p2 = CheckProcess(
            (self.startindex + perProcess * 2) % ipLineSum,
            self.q,
            self.ipfactory,
            increasing=False)
        p1.start()
        p2.start()


ipLineSum = 1835
ipHasFind = 0
ProcessSum = 4
perProcess = int(ipLineSum / ProcessSum)

if os.path.exists("ip_has_find.txt"):
    with open("ip_has_find0.txt", "r") as f:
        ipHasFind = int(f.read())
else:
    ipHasFind = random.randint(0, ipLineSum)

with open("ip_range.txt") as fd:
    iprange = fd.read()

for i in range(ProcessSum // 2):
    startindex = (ipHasFind + perProcess * i * 2) % ipLineSum
    task = Task(startindex, iprange)
    task.start()

try:
    with open("ip.txt", "w") as f:
        sum = 0
        while True:
            ip = ipList.get()
            s = ip + "|"
            f.write(s)
            sum += 1
            print("All Sucess Ip:%4d" % sum)
except (KeyboardInterrupt, SystemExit) as e:
    print("main exited")
