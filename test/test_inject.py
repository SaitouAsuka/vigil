import time
from functools import wraps

def process_list(items):
    result = []  # 第1行
    for item in items:  # 第2行
        result.append(item * 2)  # 第3行
    return result  # 第4行

# 添加类方法注入测试
class Calculator:
    def multiply(self, a, b):
        result = a * b  # 第2行
        return result   # 第3行
    

# 测试修饰器
def timer(func):
    start_time = time.time()
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    end_time = time.time()
    print("cost time:{}".format(end_time -start_time))
    return wrapper


@timer
def calculate(a, b):
    result = 0  # 第1行
    result += a  # 第2行
    result += b  # 第3行
    return result  # 第4行