#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import warnings
import aiohttp
import os
import ssl
import time
import get_ip


class Test_Ip:
    def __init__(self, loop, ipCreator, f):
        self.loop = loop
        self.indexDict = dict()
        self.d = dict()
        self.ipcreator = ipCreator
        self.q = asyncio.Queue()
        self.max = 64
        self.now = 1
        self._running = True
        # self.scan = True
        self.scan = False
        self.ipSum = 0
        self.ipSuccessSum = 0

        if(self.scan):
            self.now = 0
            self.ipcreator.scan_ip()
            self.generateIp = self.ipcreator.generate_for_scan
        else:
            self.f = f
            self.ipcreator.find_ip()
            self.generateIp = self.ipcreator.generate
        print("get ipcreator")
        self.future = None

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
                    # print(ip,"status:", resp.status ,"time_used:", time_used)
                    self.d[ip] = time_used
                    # if(self.scan):
                        # print(await resp.text())
                    return True

                if "gws" not in server_type and "Google Frontend" not in server_type and "GFE" not in server_type:
                    return False
                else:
                    end_time = time.time()
                    time_used = end_time - start_time
                    # print(ip, "time_used:", time_used)
                    self.d[ip] = time_used
                    return True

        except KeyboardInterrupt as e:
            # self.loop.run_until_complete(self.stop())
            if self._running:
                self._running = False
                loop.create_task(self.stop())
            if self._running:
                self._running = False
                loop.create_task(self.stop())
        except BaseException as e:
            # print(e)
            return False
            # print(e)

    async def worker(self):
        try:
            while self._running:
                if self.ipSuccessSum > 2000:
                    if self._running:
                        self._running = False
                        loop.create_task(self.stop())
                        break
                ip = await self.generateIp()
                if(ip is None):
                    break

                # print("test ip")
                if ip not in self.d:
                    self.d[ip] = 0
                success = await self.test(ip)
                self.ipSum += 1
                if success:
                    index = self.ipcreator.getIndex()
                    if index not in self.indexDict:
                        self.indexDict[index] = 1
                    else:
                        self.indexDict[index] += 1

                    self.ipSuccessSum += 1
                    print(ip, "Success delay:%.2f" % self.d[ip])
                    print("spend time:%d" % (time.time() - self.start_time))
                    print(
                        "Success:%d  All:%d" %
                        (self.ipSuccessSum, self.ipSum))
                    if ip in self.d:
                        del self.d[ip]
                    await self.q.put(ip)
                #print(ip, "Fail ")

        except KeyboardInterrupt as e:
            # self.loop.run_until_complete(self.stop())
            if self._running:
                self._running = False
                loop.create_task(self.stop())
        finally:
            self.now -= 1
            if not self.future.done():
                self.future.set_result("need task")
            # print("Task Done :", self.now)
            # self.now += 1
            # self.loop.create_task(self.worker())

    async def Server(self):
        self.Running = asyncio.Future()
        self.startIndex = self.ipcreator.getIndex()
        context = ssl.create_default_context()
        context.check_hostname = False
        print("create session")

        if(not self.scan):
            self.loop.create_task(self.SaveIp())

        print("creat SaveIp worker")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl_context=context, force_close=True), conn_timeout=0.5, read_timeout=0.5) as self.session:
            self.start_time = time.time()
            create = True
            print("create session Success")
            print("Start Scan Ip")
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
            print("stopping  wait %d worker stop" % self.now)
        if(self.scan is False):
            self.f.close()
            print("file closed")
        index = ipcreator.getIndex()
        with open("ip_has_find.txt", "w") as f:
            f.write(str(index))
        print("index saved:", index)
        print("Success stop")
        with open("find_log.txt", "a") as f:
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
            # await asyncio.sleep(1)
            s = ip + "|"
            self.f.write(s)
            # print("file writed", s)
        self.now -= 1

    async def SuccessStop(self):
        if self.Running.done():
            return True
        await self.Running
        return True


# os.fork()
# os.fork()
# os.fork()


try:
    ipcreator = get_ip.IpCreator()
    f = open("ip.txt", 'w')
    # f = None
    loop = asyncio.get_event_loop()
    testip = Test_Ip(loop, ipcreator, f)
    loop.create_task(testip.Server())
    loop.run_until_complete(testip.SuccessStop())

except KeyboardInterrupt as e:
    loop.create_task(testip.stop())
    loop.run_until_complete(testip.SuccessStop())

finally:
    loop.close()
