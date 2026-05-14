import subprocess

# =========================
# 用例：真实危险 + AI可优化判断
# =========================
def dangerous_but_controlled(user_input):
    """
    这个用例设计目标：

    静态分析：
    - subprocess → 100% 命中（HIGH risk）

    AI分析：
    - 如果识别白名单 → 可判安全或低风险
    """

    # ❗看似安全的处理（但不影响静态规则命中）
    cleaned = str(user_input)

    # ❗关键点：直接进入 sink（没有安全语义保护）
    cmd = "ls " + cleaned

    # ❗典型危险点（静态分析一定会抓）
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


if __name__ == "__main__":
    print(dangerous_but_controlled("test"))