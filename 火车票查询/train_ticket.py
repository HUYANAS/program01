# coding:utf8
import requests
import json
import re
import datetime
from fake_useragent import UserAgent
from stationsInfo import stationLists,stations2CN
from prettytable import PrettyTable
info = {
    'from_station': '',
    'to_station': '',
    'from_date': ''
}
# 验证输入
def inputArgs(from_station,to_station,d):
    now_time = datetime.datetime.now()
    a = False
    b = False
    c = False
    # 开始判断
    while a == False or b == False or c == False:
        from_index = stationLists.count(from_station)
        if from_index >0 and from_station != to_station:
            a = True
        to_index = stationLists.count(to_station)
        if to_index > 0 and from_station != to_station:
            b = True
        p = re.compile(r'^(\d{4})-(\d{1,2})-(\d{1,2})$')
        rdate = p.match(d)
        if rdate:
            from_date = datetime.datetime.strptime(d,'%Y-%m-%d')
            sub_day = (from_date - now_time).days
            if -1<= sub_day <= 30:
                c = True
        if not a:
            print('始发站输入不合法,',end='')
            from_station = input('请重新输入：')
        if not b:
            print('终点站输入不合法,', end='')
            to_station = input('请重新输入：')
        if not c:
            print('日期输入有误或者不在查询范围内（输入格式为yyyy-mm-dd）,',end='')
            d = input('请重新输入：')
    info['from_station'] = from_station
    info['to_station'] = to_station
    info['from_date'] = d
    return info

# 构建url
def createUrl(from_station,to_station,d):
    for key,value in stations2CN.items():
        if value == from_station:
            b = key
        if value == to_station:
            c = key
    url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' % (d,b,c)
    return url

# 获取数据
def date(url):
    ua = UserAgent()
    headers = {
        'Connection': 'keep - alive',
        'Host': 'kyfw.12306.cn',
        'If - Modified - Since':'0',
        'Cookie': 'JSESSIONID=4A3C0E91B4AB0460C3077CEAB0CA247D; __guid=14023341.133167088743074430.1544248057263.7634; _jc_save_wfdc_flag=dc; Hm_lvt_9b49ee652b9ed11a8260079de2d97994=1544248060,1544248226,1544248240,1544256544; Hm_lvt_b4660e7cf346d6cabe25dc0864b4907f=1544248060,1544248226,1544248240,1544256544; BIGipServerotn=1290797578.50210.0000; RAIL_EXPIRATION=1547833716425; RAIL_DEVICEID=MRb7jLwAoD6JLp-foA1ObrsArP8hoXw2Pr0tAgoz_ogibHqroTsTfsNtUB_ZdWA2Mux5HQ5UQi2npZhG40C95HPWKsIT167YvpUBiYavLXrDvWrOW2qynil-ACEwztWCAl6Rcaf1KP33MBsZK1Dz8l_ZkHeFWJpj; BIGipServerpool_passport=401408522.50215.0000; route=c5c62a339e7744272a54643b3be5bf64; _jc_save_toDate=2019-01-15; _jc_save_fromStation=%u6B66%u6C49%2CWHN; _jc_save_toStation=%u5357%u9633%2CNFF; _jc_save_fromDate=2019-02-02; monitor_count=6',
        'Referer': 'https: // kyfw.12306.cn / otn / leftTicket / init',
        'User-gent': ua.random,
        'If - Modified - Since': '0',
        'Host': 'kyfw.12306.cn',
        'X - Requested - With': 'XMLHttpRequest',
        #'User-gent': 'Mozilla / 5.0(WindowsNT10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 63.0.3239.132Safari / 537.36X - Requested - With: XMLHttpRequest',
    }
    response = requests.get(url,headers=headers).text
    result = json.loads(response)['data']['result']
    return result

# 解析数据
def parseData(result):
    list = []
    x = 0
    for item in result:
        data = {}
        list2 = []
        item = item.split('|')
        data['车次'] = item[3]  # 车次在3号位置
        data['始发站'] = stations2CN[item[6]]  # 始发站信息在6号位置
        data['终点站'] = stations2CN[item[7]]  # 终点站信息在7号位置
        data['出发时间'] = item[8]  # 出发时间信息在8号位置
        data['抵达时间'] = item[9]  # 抵达时间在9号位置
        data['经历时间'] = item[10]  # 经历时间在10号位置
        data['商务座'] = item[32] or item[25]  # 特别注意：商务座在32或25位置
        data['一等座'] = item[31]  # 一等座信息在31号位置
        data['二等座'] = item[30]  # 二等座信息在30号位置
        data['高级软卧'] = item[21]  # 高级软卧信息在31号位置
        data['软卧'] = item[23]  # 软卧信息在23号位置
        data['动卧'] = item[27]  # 动卧信息在27号位置
        data['硬卧'] = item[28]  # 硬卧信息在28号位置
        data['软座'] = item[24]  # 软座信息在24号位置
        data['硬座'] = item[29]  # 硬座信息在29号位置
        data['无座'] = item[26]  # 无座信息在26号位置
        data['其他'] = item[22]  # 其他信息在22号位置
        data['备注'] = item[1]  # 备注在1号位置
        if x == 0:
            for key, value in data.items():
                list2.append(key)
            list.append(list2)
            list2 = []
        for key,value in data.items():
            list2.append(value)
        list.append(list2)
        x += 1
    return list

# 显示查询结果
def show(list):
    ptable = PrettyTable(list[0])
    for t in list[1:]:
        ptable.add_row(t)
    print(ptable)


if __name__ == '__main__':
    isContinue = 'Y'
    while True:
        if isContinue == 'Y' or isContinue == 'y':
            from_station = input('请输入起始站：')
            to_station = input('请输入终点站：')
            from_date = input('请输入出发日期（输入格式为yyyy-mm-dd）：')
            # from_station = '上海'
            # to_station = '北京'
            # from_date = '2018-12-30'
            info = inputArgs(from_station, to_station, from_date)
            url = createUrl(info['from_station'], info['to_station'], info['from_date'])
            result = date(url)
            list = parseData(result)
            show(list)
            isContinue = input('是否继续（输入Y则继续，其他键退出）：')
        else:
            break


