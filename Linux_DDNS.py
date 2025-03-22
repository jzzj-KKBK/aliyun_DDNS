import subprocess
import time
from ping3 import ping
import os
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DeleteDomainRecordRequest import DeleteDomainRecordRequest
import re

ACCESS_KEY_ID = 'You_ACCESS_KEY_ID'
ACCESS_KEY_SECRET = 'You_ACCESS_KEY_SECRET'
DOMAIN_NAME = 'sz.DNS.info' #改为你的DNS地址

REGION_ID = 'cn-hangzhou' #默认配置
# 初始化AcsClient
client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION_ID)


#查询DNS解析地址
def Describe_SubDomain_Records(client, record_type, subdomain):
    request = DescribeSubDomainRecordsRequest()
    request.set_accept_format('json')

    request.set_Type(record_type)
    request.set_SubDomain(subdomain)

    response = client.do_action_with_exception(request)
    response = str(response, encoding='utf-8')
    relsult = json.loads(response)
    return relsult
# 以下是函数调用以及说明
#des_relsult = Describe_SubDomain_Records(client, "A", "sz.DNS.info")
#print(des_relsult)

#创建DNS解析地址
def add_record(client,priority,ttl,record_type,value,rr,domainname):
    request = AddDomainRecordRequest()
    request.set_accept_format('json')

    request.set_Priority(priority)
    request.set_TTL(ttl)
    request.set_Value(value)
    request.set_Type(record_type)
    request.set_RR(rr)
    request.set_DomainName(domainname)

    response = client.do_action_with_exception(request)
    response = str(response, encoding='utf-8')
    relsult = json.loads(response)
    return relsult

def ping_ip(ip_address):
    delay = ping(ip_address)  # 返回延迟（秒），失败返回None或False
    return delay * 1000 if delay else None  # 转换为毫秒

def check_netstat_port(port):
    try:
        # 执行netstat命令
        result = subprocess.run(
            ["netstat", "-anp"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # 按行过滤端口
        filtered_lines = []
        for line in result.stdout.split('\n'):
            if f":{port}" in line or f" {port} " in line:
                filtered_lines.append(line.strip())
        return filtered_lines
    except Exception as e:
        return [f"Error: {str(e)}"]

def check_gost_process(keyword):
    try:
        # 执行ps命令
        result = subprocess.run(
            ["ps", "-aux"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # 过滤包含关键字的行（排除grep自身）
        filtered_lines = []
        for line in result.stdout.split('\n'):
            if keyword in line and "grep" not in line:
                filtered_lines.append(line.strip())
        return filtered_lines
    except Exception as e:
        return [f"Error: {str(e)}"]
def DNS_change(IPv4):
    des_relsult = Describe_SubDomain_Records(client, "A", DOMAIN_NAME)
    aaa = des_relsult['DomainRecords']['Record']
    for i in aaa:
        request = DeleteDomainRecordRequest()
        request.set_RecordId(i['RecordId'])
        client.do_action_with_exception(request)
    add_relsult = add_record(client, "5", "600", "A", IPv4, "sz", "DNS.info")# 倒数第二个为DNS前缀，最后一个为DNS地址

if __name__ == '__main__':
    gosts=[]
    gost_processes = check_gost_process("gost")
    try:
        for proc in gost_processes:
            gost1=proc.split()[-1].split("@")[1].split(":")[0]
            if gost1!='44.44.44.44': #排除掉你不想要添加到线路的IP地址
                dict1={gost1:proc.split()[1]}
                gosts.append(dict1)
    except:
        print("没开gost")
    print("\nPS输出（已经过滤禁止解析的gost进程）:")
    print(gosts)
    #建议刷新一下，不过不刷新不影响
    #DNS_change("11.11.11.11")

    #开始循环
    while True:

        Delays=[]
        for i in gosts:
            delay = ping_ip(list(i.keys())[0])
            Delays.append(delay)
        command = "netstat -anp |grep 25566|grep gost" #这里需要更换成你的服务器端口

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            # 匹配所有符合 "数字/进程名" 模式的部分
            pid_matches = re.findall(r'(\d+)/\S+', result.stdout)
            if pid_matches:
                # 去重后输出所有关联的PID
                unique_pids = pid_matches
        try:
            if type(unique_pids)==list:
                ii=-1
                mount={}
                for i in gosts:
                    ii=ii+1
                    for j in gosts[ii]:
                        a=i[j]
                        mount[[i for i in list(i.keys())][0]]=unique_pids.count(a)
                print(mount)
                #配置负载
                # 如果11.11.11.11的连接数大于二，且22.22.22.22的连接数小于二，则将DNS解析地址改为22.22.22.22
                if mount['11.11.11.11'] >=2 and mount['22.22.22.22']<2:
                    DNS_change("22.22.22.22")
                if mount['22.22.22.22'] >=2 and mount['11.11.11.11']<2:
                    DNS_change("11.11.11.11")
                if mount['11.11.11.11'] >= 3 and mount['22.22.22.22'] >= 3:
                    DNS_change("33.33.33.33")

        except:
            pass
        unique_pids=1
        #刷新时间，建议大于3
        time.sleep(3)
