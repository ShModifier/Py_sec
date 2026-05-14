import os
import subprocess
import sqlite3
import pickle


# =========================
# 1. 命令执行类（真实漏洞）
# =========================
def rce_case_1(user_input):
    os.system("ls " + user_input)  # RCE 1


def rce_case_2(cmd):
    subprocess.run(cmd, shell=True)  # RCE 2（高危）


def rce_case_3(name):
    subprocess.Popen("echo " + name, shell=True)  # RCE 3


# =========================
# 2. SQL注入类（真实漏洞）
# =========================
def sql_case_1(user_id):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    query = "SELECT * FROM user WHERE id = '%s'" % user_id  # SQLi 1
    cursor.execute(query)


def sql_case_2(username):
    conn = sqlite3.connect("test.db")
    conn.execute(f"SELECT * FROM user WHERE name = '{username}'")  # SQLi 2


# =========================
# 3. 不安全反序列化（真实漏洞）
# =========================
def pickle_case(data):
    return pickle.loads(data)  # RCE 4


# =========================
# 4. 文件路径问题（真实漏洞）
# =========================
def file_case_1(filename):
    return open("/data/" + filename).read()  # Path traversal


def file_case_2(user_path):
    with open(user_path, "r") as f:  # Path traversal 2
        return f.read()


# =========================
# 5. AI可纠正误报（重点）
# =========================

# ❗误报点1：其实安全（AI应识别为低风险或无风险）
def safe_case_1(filename):
    allowed = ["a.txt", "b.txt", "c.txt"]
    if filename not in allowed:
        raise ValueError("invalid file")

    with open(filename, "r") as f:
        return f.read()  # ✔ 安全（白名单）


# ❗误报点2：看似拼接，但实际安全
def safe_case_2(name):
    # 这里是日志输出，不是命令执行
    log = "USER:" + name
    print(log)  # ✔ AI应识别不是RCE


# ❗误报点3：SQL拼接但未执行（AI可判断）
def safe_case_3(user_id):
    query = "SELECT * FROM user WHERE id = '" + user_id + "'"
    print(query)  # ✔ 未执行SQL


# =========================
# 6. 混合复杂场景（AI上下文测试）
# =========================
def mixed_case(user_input):
    # 上下文5行内 AI必须判断
    sanitized = user_input.strip()
    sanitized = sanitized.replace(";", "")
    sanitized = sanitized.replace("&", "")

    os.system("echo " + sanitized)  # ❗可能误报/需判断


# =========================
# 7. 嵌套调用（增加难度）
# =========================
def wrapper(input_data):
    return inner(input_data)


def inner(data):
    subprocess.run("ls " + data, shell=True)  # RCE 5


# =========================
# 8. 更多SQLi
# =========================
def sql_case_3(email):
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    sql = f"SELECT * FROM users WHERE email = '{email}'"  # SQLi 3
    cursor.execute(sql)


# =========================
# 9. 综合误报点（AI关键测试）
# =========================
def safe_but_complex(user_input):
    # 多层过滤（AI应该判断安全）
    clean = user_input.replace("|", "")
    clean = clean.replace(";", "")
    clean = clean.strip()

    # 只是字符串拼接，不执行
    command = "echo " + clean
    print(command)  # ✔ 非执行


# =========================
# 10. 额外真实漏洞补充
# =========================
def eval_case(code):
    eval(code)  # RCE 6


def exec_case(code):
    exec(code)  # RCE 7