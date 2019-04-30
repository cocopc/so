# -*- coding: utf-8 -*-
import sys
import pexpect
import signal
import yaml
import os
import shutil
import time

password_yaml = """ssh: 
  - id: 1
    name: demo1
    user: fqiyou
    password: xxx
    host: 1.1.1.1
    port: 20755
  - id: 2
    name: demo2
    user: fqiyou
    password: xxx
    host: 1.1.1.1
    port: 39986
  - id: 3
    name: demo3
    user: root
    password: demo.pem
    host: 1.1.1.1
    port: 22
"""
keys_demo_pem = """-----BEGIN RSA PRIVATE KEY-----
xxxxx
-----END RSA PRIVATE KEY-----
"""



def _exit(*args, **kwargs):
    print('You choose to stop so.')
    sys.exit(1)


def _get_hosts_by_config():
    try:
        so_dir = os.path.join(os.path.expanduser('~'), ".so")
        password_yaml_file = os.path.join(so_dir, "password.yaml")
        keys_dir = os.path.join(so_dir, "keys")
        return yaml.load(open(password_yaml_file, 'r').read())["ssh"], keys_dir
    except Exception as e:
        print("获取配置文件错误", e)
        exit(1)
        return

def _login_ssh(user, password, host, port):
    if password.endswith('.pem'):
        child = pexpect.spawn('ssh %s@%s -p %s -i %s' % (user, host, port, password))
    else:
        child = pexpect.spawn('ssh %s@%s -p %s' % (user, host, port))
    i = child.expect(['nodename nor servname provided', 'Connection refused', pexpect.TIMEOUT, '[Pp]assword:', 'continue connecting (yes/no)?', '#'])
    if i <= 2:
        print(child.before, child.after)
        return
    elif i == 3:
        child.sendline(password)
    elif i == 4:
        child.sendline('yes')
        child.expect('[Pp]assword:')
        child.sendline(password)
    elif i == 5:
        pass
    else:
        print(i)
        print(child.before, child.after)
        return
    print('Login Success!')
    child.sendline('')
    child.interact()

def _print_head():
    print("##############################################")
    print("\033[0;36m               SU Login Platform              \033[0m")
    print("##############################################")

def _print_underline():
    print("----------------------------------------------")

def _print_remind():
    print("[*] 选择主机:")


def _print_host_list(host_list):
    _print_underline()
    print("  序号  |       主机      |   说明   " )
    _print_underline()
    for i in host_list:
        print("\033[0;31m%4s\033[0m\t| %15s | %s\t" % (i['id'], i['host'], i['name']))
    _print_underline()

def _login(info, keys_dir):
    user = info["user"]
    password = info["password"]
    host = info["host"]
    port = info["port"]
    if password.endswith('.pem'):
        password = os.path.join(keys_dir,password)
    _login_ssh(user=user, password=password, host=host, port=port)

def run():
    config_host_list, key_dir = _get_hosts_by_config()
    config_host_map = dict(zip([str(i["id"]) for i in config_host_list], config_host_list))
    # 信号
    signal.signal(signal.SIGINT, _exit)
    signal.signal(signal.SIGTERM, _exit)
    _print_head()
    while True:
        _print_host_list(config_host_list)
        _print_remind()
        cmd_args = sys.stdin.readline().replace("\n", "")
        if cmd_args in config_host_map:
            _login(config_host_map[cmd_args], key_dir)
        elif cmd_args == "q" or cmd_args == "exit" or cmd_args == "quit":
            return
        else:
            print("未知参数:%s" % cmd_args)


def run_install():
    so_dir = os.path.join(os.path.expanduser('~'), ".so")
    if os.path.exists(so_dir):
        shutil.move(so_dir, so_dir+"_" + str(int(time.time() * 1000)))
    os.mkdir(so_dir)
    os.mkdir(os.path.join(so_dir, "keys"))
    with open(os.path.join(so_dir, 'password.yaml'), 'w') as f:
        f.write(password_yaml)
    with open(os.path.join(so_dir, "keys", 'demo.pem'), 'w') as f:
        f.write(password_yaml)





