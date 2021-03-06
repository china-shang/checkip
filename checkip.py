#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from async_timeout import timeout
import ssl
import urllib.parse
import time
import os
from multiprocessing import Process, Queue
import random
import get_ip
import profile

ipTimeout = 1.5
ipList = Queue()
GoodIpRange = Queue()
with open("ip_range.txt") as fd:
    iprange = fd.read()
    iprangelen = iprange.count('\n')

if os.path.exists("ip_has_find.txt"):
    with open("ip_has_find.txt", "r") as f:
        ipHasFind = int(f.read()) % iprangelen
else:
    ipHasFind = random.randint(0, iprangelen - 1)

ProcessSum = 4
ActiveProcess = Queue()
ActiveProcess.put(ProcessSum)


class Test_Ip:
    def __init__(self, loop, ipfactory):
        global ipList
        self.loop = loop
        self.ipfactory = ipfactory
        self.q = asyncio.Queue()

        self.indexDict = dict()
        self.d = dict()

        self.max = 64
        self.now = 1

        self._running = True
        self.future = None

        self.scan = False
        self.num = 0

        self.ipSum = 0
        self.ipSuccessSum = 0

        self.getip = self.ipfactory.getIp

    async def test(self, ip):
        start_time = time.time()
        len = 0

        try:
            with timeout(ipTimeout):
                con = asyncio.open_connection(ip, 443, ssl=self.context)
                reader, writer = await con
                appid = "my-project-1-1469878073076"
                query = 'GET /_gh/ HTTP/1.1\r\nHost: %s.appspot.com\r\n\r\n' % appid
                writer.write(query.encode())

                while True:
                    line = await reader.readline()
                    if not line:
                        break
                    if line:
                        line = line.decode().rstrip()
                        #print('HTTP header> %s' % line)
                    if "Content-Length" in line:
                        len = int(line.split(":")[-1])
                        break
                writer.close()

            if int(len) == 86:
                end_time = time.time()
                time_used = end_time - start_time
                self.d[ip] = time_used
                return True

            return False

        except (KeyboardInterrupt, SystemExit) as e:
            print("this worker")
            if self._running:
                self._running = False
                self.loop.create_task(self.stop())

        except asyncio.TimeoutError as e:
            return False

        except BaseException as e:
            # print(e)
            return False

    async def worker(self):
        try:
            while self._running:
                ip = self.getip()
                self.index = self.ipfactory.getIndex()

                success = await self.test(ip)
                self.ipSum += 1
                if not self.ipSum % 2000:
                    print("Has check ip :%d" % self.ipSum)
                    print("speed:%d" % (self.ipSum /
                                        (time.time() - self.start_time)))

                if success:
                    if self.index not in self.indexDict:
                        self.indexDict[self.index] = 1
                    else:
                        self.indexDict[self.index] += 1

                    self.ipSuccessSum += 1
                    # print(
                        #"pid:", os.getpid(), "\ttime:%ds\t" %
                        #(time.time() - self.start_time))

                    print("speed:%d" % (self.ipSum /
                                        (time.time() - self.start_time)))
                    print(ip, "\tdelay:\t%.2f" % self.d[ip])
                    print(
                        "Success:%4d\tin:%4d" %
                        (self.ipSuccessSum, self.ipSum))

                    await self.q.put(ip)
                    if ip in self.d:
                        del self.d[ip]

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
        self.context = ssl.create_default_context()
        self.context.check_hostname = False

        if(not self.scan):
            self.loop.create_task(self.SaveIp())

            self.start_time = time.time()
            while self._running:
                if self.now < self.max:
                    self.now += 1
                    # print("create task at", self.now)
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
            # print("file closed")
        # file_name = "ip_has_find" + str(self.num) + ".txt"
        # with open(file_name, "w") as f:
            # f.write(str(self.index))
        # print("index saved:", self.index)
        if ProcessSum < 1:
            file_name = "find_log" + str(self.num) + ".txt"
            with open(file_name) as f:
                s = f.readlines()

            d = dict([[int(i.split(":")[0]), int(i.split(":")[-1])]
                      for i in list(map(lambda x:x[:-1], s))])

            d.update(self.indexDict)
            with open(file_name, "w") as f:
                for i in d.items():
                    print(i[0], ":", i[1])
                    f.write(str(i[0]) + ":" + str(i[1]) + "\n")
        else:
            GoodIpRange.put(self.indexDict)

        if not self.Running.done():
            self.Running.set_result("stoped")
        return True

    async def SaveIp(self):
        if ProcessSum > 1:
            while self._running:
                ip = await self.q.get()
                if ip != "end":
                    ipList.put(ip)
        else:
            with open("ip.txt", "w") as f:
                sum = 0
                while self._running:
                    ip = await self.q.get()
                    if ip == "end":
                        break
                    s = ip + "|"
                    f.write(s)
                    sum += 1
                    print("All Sucess Ip:%4d" % sum)

        self.now -= 1

    async def SuccessStop(self):
        if self.Running.done():
            pass
        else:
            await self.Running
        activeprocess = ActiveProcess.get()
        if activeprocess == 1:
            try:
                index = self.ipfactory.getIndex()
            except Exception as e:
                print(e)
            else:
                with open("ip_has_find.txt", "w") as f:
                    f.write(str(index))

        ActiveProcess.put(activeprocess - 1)
        print("Success stop")
        return True


class CheckProcess(Process):
    def __init__(self, q, iprange):
        self.q = q
        self.iprange = iprange
        super().__init__()

    def run(self):
        try:
            loop = asyncio.get_event_loop()
            ipfactory = get_ip.ipFactory(self.q, self.iprange)
            testip = Test_Ip(loop, ipfactory)
            loop.create_task(testip.Server())

            profile.runctx(
                "loop.run_until_complete(testip.SuccessStop())",
                globals(),
                locals())
            # loop.run_until_complete(testip.SuccessStop())

        except (KeyboardInterrupt, SystemExit) as e:
            loop.create_task(testip.stop())
            loop.run_until_complete(testip.SuccessStop())

        finally:
            loop.close()
            print("Task exit")


def main():
    global iprange, ipHasFind
    print("Process Sum:", ProcessSum)
    if ProcessSum > 1:
        q = Queue()
        q.put(ipHasFind)
        for i in range(ProcessSum):
            print("Start Process:", i)
            p = CheckProcess(q, iprange)
            p.start()

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
        finally:
            file_name = "find_log" + "0" + ".txt"
            with open(file_name) as f:
                s = f.readlines()

            d = dict([[int(i.split(":")[0]), int(i.split(":")[-1])]
                      for i in list(map(lambda x:x[:-1], s))])

            while GoodIpRange.qsize() > 0:
                nowdict = GoodIpRange.get()
                d.update(nowdict)

            with open(file_name, "w") as f:
                for i in d.items():
                    print(i[0], ":", i[1])
                    f.write(str(i[0]) + ":" + str(i[1]) + "\n")
    else:
        try:
            q = Queue()
            q.put(ipHasFind)

            loop = asyncio.get_event_loop()
            ipfactory = get_ip.ipFactory(q, iprange)

            testip = Test_Ip(loop, ipfactory)
            loop.create_task(testip.Server())

            profile.runctx(
                "loop.run_until_complete(testip.SuccessStop())",
                globals(),
                locals())
            # loop.run_until_complete(testip.SuccessStop())

        except (KeyboardInterrupt, SystemExit) as e:
            loop.create_task(testip.stop())
            loop.run_until_complete(testip.SuccessStop())

        finally:
            loop.close()
            print("Task exit")


if __name__ == "__main__":
    main()
