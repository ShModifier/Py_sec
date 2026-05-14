# -*- coding: utf-8 -*-

import os
import sqlite3
import subprocess
import pickle

# =========================
# 模拟危险 sink 函数
# =========================

def execute_sql(sql):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def run_cmd(cmd):
    return os.system(cmd)

def render_html(content):
    return f"<html>{content}</html>"

def unsafe_deserialize(data):
    return pickle.loads(data)

def eval_code(code):
    return eval(code)

# =========================
# 26个测试用例
# =========================

# 1 SQL注入（典型）
def case1(user_input):
    sql = "SELECT * FROM users WHERE name = '" + user_input + "'"
    return execute_sql(sql)

# 2 SQL注入（拼接）
def case2(uid):
    return execute_sql("SELECT * FROM user WHERE id=" + uid)

# 3 命令注入
def case3(cmd):
    return run_cmd("ping " + cmd)

# 4 命令注入
def case4(ip):
    os.system("tracert " + ip)

# 5 XSS
def case5(data):
    return render_html("<div>" + data + "</div>")

# 6 XSS
def case6(name):
    html = "<h1>" + name + "</h1>"
    return render_html(html)

# 7 反序列化
def case7(payload):
    return unsafe_deserialize(payload)

# 8 eval执行
def case8(expr):
    return eval_code(expr)

# 9 文件路径穿越
def case9(filename):
    path = "/data/" + filename
    return open(path).read()

# 10 文件路径穿越
def case10(user_file):
    return open("../uploads/" + user_file)

# 11 SQL注入（format）
def case11(name):
    sql = f"SELECT * FROM user WHERE name='{name}'"
    return execute_sql(sql)

# 12 命令执行（format）
def case12(host):
    return os.system(f"ping {host}")

# 13 LDAP注入模拟
def case13(user):
    query = "(uid=" + user + ")"
    return query

# 14 代码拼接执行
def case14(code):
    return eval(code)

# 15 XSS
def case15(comment):
    return render_html(comment)

# 16 日志注入
def case16(msg):
    log = "ERROR: " + msg
    print(log)

# 17 SQL拼接
def case17(a):
    return execute_sql("SELECT * FROM t WHERE a=" + a)

# 18 命令拼接
def case18(file):
    return os.system("cat " + file)

# 19 pickle反序列化
def case19(data):
    return pickle.loads(data)

# 20 HTML注入
def case20(text):
    return render_html("<p>" + text + "</p>")


# =========================
# ⚠️ AI可判定为无风险（误报测试）
# =========================

# 21 ❗误报：整数输入，不可控SQL拼接
def case21(user_id: int):
    sql = "SELECT * FROM user WHERE id=" + str(user_id)
    return execute_sql(sql)
# EXPECT: AI should mark SAFE

# 22 ❗误报：常量字符串拼接
def case22():
    sql = "SELECT * FROM user WHERE role=" + "'admin'"
    return execute_sql(sql)
# EXPECT: SAFE

# 23 ❗误报：内部固定变量
def case23():
    cmd = "ls -la"
    return os.system(cmd)
# EXPECT: SAFE

# 24 ❗误报：静态HTML拼接无外部输入
def case24():
    return render_html("<h1>hello world</h1>")
# EXPECT: SAFE

# 25 ❗误报：pickle加载固定数据
def case25():
    data = pickle.dumps({"a": 1})
    return pickle.loads(data)
# EXPECT: SAFE

# 26 ❗误报：eval固定表达式
def case26():
    return eval("1 + 1")
# EXPECT: SAFE