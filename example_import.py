from test.test_inject import process_list, calculate, timer
from test.test_inject import Calculator as CR
from vigil import ci

ci.assign_function(timer)

ci.register(calculate, line_number=1, code='print("After line 1: result=", result); result = 100', position='+')
ci.register(calculate, line_number=2, code='print("Before return: result=", result); result += 50', position='-')

ci.register(process_list, line_number=3, code='print("Processing item:", item)', position='+')
ci.register(process_list, line_number=4, code='print("List length after processing:", len(result))', position='-')

calc = CR()
# 创建实例并注册类方法注入
ci.register(CR.multiply, line_number=2, code='print("Before multiply: a=", a, ", b=", b); result = 100', position='-')
ci.register(CR.multiply, line_number=2, code='print("After multiply: result=", result); result += 50', position='-')


if __name__ == "__main__":
    ci.enable()
    print("=== 注入已应用 ===")
    print("calculate(2, 3) =", calculate(2, 3))
    print("process_list([1, 2, 3]) =", process_list([1, 2, 3]))
    print("calc.multiply(3, 4) =", calc.multiply(3, 4))

    ci.restore()
    print("\n=== 恢复原始函数后 ===")
    print("calculate(2, 3) =", calculate(2, 3))
    print("process_list([1, 2, 3]) =", process_list([1, 2, 3]))
    print("calc.multiply(3, 4) =", calc.multiply(3, 4))



