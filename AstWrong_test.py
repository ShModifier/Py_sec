import os
import json


class UserService:
    def __init__(self, db):
        self.db = db

    def get_user(self, user_id):
        query = "SELECT * FROM users WHERE id=" + user_id
        return self.db.execute(query)

    def create_user(self, name, age):
        if not name:
            raise ValueError("name required")

        data = {
            "name": name,
            "age": age,
        }

        return self.db.insert("users", data)


def load_config(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


def process_request():
    config = load_config("config.json")

    user_input = input("Enter user id: ")

    service = UserService(db=None)

    # 正常逻辑
    if config.get("debug"):
        print("Debug mode")

    if user_input.isdigit()  #if漏写冒号
        print("Valid id")

    return service.get_user(user_input)

def calculate(a, b):
    result = a + b
    if (result > 10)):#多写一个括号
        return result
    return result * 2

def build_command():
    cmd = input("cmd: ")
    full_cmd = "echo " + cmd  #字符串未闭合
    return full_cmd

def run():
    command = build_command()
    exec(command  #函数调用缺少右括号


def main():
    try:
        result = process_request()
        print("Result:", result)

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    main()