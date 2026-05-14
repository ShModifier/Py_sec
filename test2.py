# test_vulnerable_app.py
import os
import subprocess
import pickle


def test_eval():
    code = input("Enter code: ")
    eval(code)  # RCE: EvalExecRule


def test_exec():
    user_code = input("cmd: ")
    exec(user_code)  # RCE: EvalExecRule


def test_command_exec():
    cmd = input("command: ")
    os.system(cmd)  # RCE: CommandExecRule / CommandInjectionRule


def test_subprocess():
    user_cmd = input("command: ")
    subprocess.Popen(user_cmd, shell=True)  # CommandExecRule


def test_sql_injection(cursor):
    user_id = input("id: ")
    query = "SELECT * FROM users WHERE id=" + user_id
    cursor.execute(query)  # SQLInjectionRule


def test_pickle():
    data = input("pickle data: ")
    pickle.loads(data)  # PickleLoadRule


def test_path_traversal():
    filename = input("filename: ")
    with open("/tmp/" + filename, "r") as f:  # PathTraversalRule
        print(f.read())



if __name__ == "__main__":
    print("Running tests")
    print("Vulnerable test file loaded")