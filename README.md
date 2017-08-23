# checkip
扫描Google ip的工具



扫描出来的ip支持https，使用Python3异步增加扫描速度，
http请求使用aiohttp模块



使用方法: 安装aiohttp模块后 python3 checkip.py
扫描出来的ip放在ip.txt中



注意：由于采用多进程+异步，扫描速度过于暴力，在扫描期间可能导致其他应用网络变差，甚至同局域网的其他主机网络变差
,停止扫描即可回复正常
