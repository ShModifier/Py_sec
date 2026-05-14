# test_taint_validation.py

import os
import subprocess
import pickle


# =========================
# 1. eval（有污点）→ 应该 HIGH
# =========================
def case_eval_tainted():
    user_input = input("code:")
    eval(user_input)


# =========================
# 2. eval（无污点）→ 应该 LOW（或不报）
# =========================
def case_eval_safe():
    code = "1+1"
    eval(code)


# =========================
# 3. command（有污点）→ HIGH
# =========================
def case_cmd_tainted():
    cmd = input("cmd:")
    os.system(cmd)


# =========================
# 4. command（无污点）→ MEDIUM
# =========================
def case_cmd_safe():
    os.system("ls -l")


# =========================
# 5. SQL（有污点）→ HIGH
# =========================
def case_sql_tainted(cursor):
    uid = input("id:")
    query = "select * from user where id=" + uid
    cursor.execute(query)


# =========================
# 6. SQL（无污点）→ 不报 或 LOW
# =========================
def case_sql_safe(cursor):
    query = "select * from user where id=1"
    cursor.execute(query)


# =========================
# 7. Path（有污点）→ HIGH
# =========================
def case_path_tainted():
    filename = input("file:")
    open("/tmp/" + filename)


# =========================
# 8. Path（无污点）→ 不报
# =========================
def case_path_safe():
    open("/tmp/test.txt")


# =========================
# 9. XSS（有污点）→ HIGH
# =========================
def case_xss_tainted():
    name = input("name:")
    render_template("index.html", name=name)


# =========================
# 10. XSS（无污点）→ 不报
# =========================
def case_xss_safe():
    render_template("index.html", name="admin")


# =========================
# 11. pickle（固定漏洞）→ 一定报
# =========================
def case_pickle():
    data = input("pickle:")
    pickle.loads(data)