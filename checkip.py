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

q = Queue()
q.put(0)
ipList = Queue()


ipLineSum = 1835
ipHasFind = 0
ProcessSum = 4
perProcess = int(ipLineSum / ProcessSum)


class Test_Ip:
    def __init__(self, loop, ipCreator):
        self.loop = loop
        self.indexDict = dict()
        self.d = dict()
        self.num = q.get()
        q.put(self.num + 1)
        self.ipcreator = ipCreator
        self.q = asyncio.Queue()
        self.max = 64
        self.now = 1
        self._running = True
        self.future = None
        # self.scan = True
        self.scan = False
        self.ipSum = 0
        self.ipSuccessSum = 0

        if(self.scan):
            self.now = 0
            self.ipcreator.scan_ip()
            self.generateIp = self.ipcreator.generate_for_scan
        else:
            #file_name = "ip" + str(self.num) + ".txt"
            #self.f = open(file_name, 'w')
            self.ipcreator.find_ip()
            self.generateIp = self.ipcreator.generate

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

                if "gws" not in server_type and "Google Frontend" not in server_type and "GFE" not in server_type:
                    return False
                else:
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
                self.index = self.ipcreator.getIndex()
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
        self.startIndex = self.ipcreator.getIndex()
        context = ssl.create_default_context()
        context.check_hostname = False

        if(not self.scan):
            self.loop.create_task(self.SaveIp())

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl_context=context, force_close=True), conn_timeout=0.5, read_timeout=0.5) as self.session:
            self.start_time = time.time()
            create = True
            #print("create session Success")
            #print("Start Scan Ip")
            while self._running:
                if self.now < self.max and create:
                    self.now += 1
                    #print("create task at", self.now)
                    # print("start Task Sum: ", self.now)
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
        file_name = "ip_has_find" + str(self.num) + ".txt"
        with open(file_name, "w") as f:
            f.write(str(self.index))
        print("index saved:", self.index)
        print("Success stop")
        file_name = "find_log" + str(self.num) + ".txt"
        with open(file_name, "a") as f:
            for i in self.indexDict.items():
                print(i[0], ":", i[1])
                f.write(str(i[0]) + ":" + str(i[1]) + "\n")
        if not self.Running.done():
            print("set Running result")
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
            return True
        await self.Running
        return True


def Task(start, q, IprangeStr, *, add=True):
    try:
        loop = asyncio.get_event_loop()
        ipcreator = get_ip.IpCreator(start, q, IprangeStr, add=add)
        testip = Test_Ip(loop, ipcreator)
        loop.create_task(testip.Server())
        loop.run_until_complete(testip.SuccessStop())

    except (KeyboardInterrupt, SystemExit) as e:
        print("this Task")
        loop.create_task(testip.stop())
        loop.run_until_complete(testip.SuccessStop())

    finally:
        loop.close()
        print("Task exit")


if os.path.exists("ip_has_find.txt"):
    with open("ip_has_find.txt", "r") as f:
        ipHasFind = int(f.read())
else:
    ipHasFind = random.randint(0, ipLineSum)

with open("ip_range.txt") as fd:
    IprangeStr = fd.read()
processList = []
for i in range(int(ProcessSum / 2)):
    start = (ipHasFind + perProcess * i * 2) % ipLineSum
    end = (start + perProcess * i * 2) % ipLineSum
    q = Queue()
    q.put(perProcess * 2)
    Process(target=Task, args=(start, q, IprangeStr)).start()
    Process(target=Task, args=(end, q, IprangeStr),
            kwargs={"add": False}, 
            ).start()
with open("ip.txt", "w") as f:
    sum = 0
    while True:
        ip = ipList.get()
        s = ip + "|"
        f.write(s)
        sum += 1
        print("All Sucess Ip:%4d" % sum)
