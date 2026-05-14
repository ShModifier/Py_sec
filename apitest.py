import os
import sys
from openai import OpenAI


def get_multiline_input(prompt="请输入多行内容（单独一行输入'EOF'结束）："):
    """获取多行用户输入"""
    print(prompt)
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == 'EOF':
                break
            lines.append(line)
        except EOFError:
            break
    return '\n'.join(lines) if lines else ""


def main():
    # 初始化配置
    client = OpenAI(
        api_key="sk-dc645e66db3f4c4fa2a31dc48df3f9d4",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    messages = [
        {'role': 'system',
         'content': 'You are a helpful assistant. Please respond concisely and keep each reply under 100 words.'}
    ]

    print("===== 多轮对话开始 =====")
    print("输入多行内容后输入'EOF'结束，输入'exit'退出")

    try:
        while True:
            # 获取多行用户输入
            user_input = get_multiline_input("\n用户: ")

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit']:
                print("对话已结束")
                break

            # 更新消息列表
            messages.append({'role': 'user', 'content': user_input})

            try:
                # 调用API
                completion = client.chat.completions.create(
                    model="qwen-plus",
                    messages=messages,
                    max_tokens=500
                )

                # 处理响应
                response = completion.choices[0].message.content
                print(f"\n助手: {response}")

                # 将助手回复加入历史
                messages.append({'role': 'assistant', 'content': response})

            except Exception as e:
                print(f"\nAPI调用错误: {str(e)}")
                print("错误详情可参考: https://help.aliyun.com/model-studio/developer-reference/error-code")
                messages = messages[-10:]  # 保留最后10条消息

    except KeyboardInterrupt:
        print("\n程序已终止")
    except Exception as e:
        print(f"系统错误: {str(e)}")


if __name__ == "__main__":
    main()
