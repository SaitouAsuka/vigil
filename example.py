from vigil import ci

def calculate(a, b):
    result = 0  # 第1行
    result += a  # 第2行
    result += b  # 第3行
    return result  # 第4行

# 示例函数2：循环函数
def process_list(items):
    result = []  # 第1行
    for item in items:  # 第2行
        result.append(item * 2)  # 第3行
    return result  # 第4行

# 使用函数调用方式注册代码注入
ci.register(calculate, line_number=1, code='print("After line 1: result=", result); result = 100', position='+')
ci.register(calculate, line_number=2, code='print("Before return: result=", result); result += 50', position='-')
ci.register(process_list, line_number=3, code='print("Processing item:", item)', position='+')
ci.register(process_list, line_number=4, code='print("List length after processing:", len(result))', position='-')

# 添加类方法注入测试
class Calculator:
    def multiply(self, a, b):
        result = a * b  # 第2行
        return result   # 第3行

calc = Calculator()
# 创建实例并注册类方法注入
ci.register(Calculator.multiply, line_number=2, code='print("Before multiply: a=", a, ", b=", b); result = 100', position='-')
ci.register(Calculator.multiply, line_number=2, code='print("After multiply: result=", result); result += 50', position='-')


# 演示注入功能
if __name__ == "__main__":
    ci.enable()
    print("=== 注入已应用 ===")
    print("calculate(2, 3) =", calculate(2, 3))
    print("process_list([1, 2, 3]) =", process_list([1, 2, 3]))
    print("calc.multiply(3, 4) =", calc.multiply(3, 4))
    calc2 = Calculator()
    print("calc2.multiply(3, 4) =", calc2.multiply(3, 4))

    ci.restore()
    print("\n=== 恢复原始函数后 ===") 
    print("calculate(2, 3) =", calculate(2, 3))
    print("process_list([1, 2, 3]) =", process_list([1, 2, 3]))
    print("calc.multiply(3, 4) =", calc.multiply(3, 4))
    print("calc2.multiply(3, 4) =", calc2.multiply(3, 4))