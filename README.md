# Code Injector

一个轻量级Python模块，允许在不修改函数源码的情况下动态注入代码，支持Python 3.5及以上版本。

## 功能特点
- 在指定函数的特定行号前后注入代码
- 支持动态开启/关闭注入功能
- 不修改原始函数源代码
- 支持Python 3.5及以上版本

## 安装
## 使用示例
### 基本用法

```python
from vigil import ci

# 定义一个简单函数
def example_function(a, b):
    result = 0
    result += a  # 第3行
    result += b  # 第4行
    return result

# 注册注入规则：在example_function第3行之前注入代码
ci.register(example_function, line_number=4, code='print("After line 4: result=", result)', position='+')

# 启用注入
ci.enable()

# 调用函数，将执行注入的代码
print(example_function(2, 3))

# 禁用注入
ci.disable()

# 再次调用函数，不会执行注入的代码
print(example_function(2, 3))
```

### 输出结果
```
Before line 3: a= 2
After line 4: result= 5
5
5
```

## API文档

### 注册注入规则

#### 函数调用方式
```python
ci.register(target_function, line_number=X, code='注入代码', position='-|+')
```

参数说明：
- `target_function`: 目标函数对象
- `line_number`: 整数，函数内要注入代码的行号(从1开始)
- `code`: 字符串，要注入的Python代码
- `position`: 字符串，'-'表示在指定行之前注入，'+'表示在指定行之后注入

### 控制注入状态

#### 启用注入
```python
ci.enable()
```

#### 禁用注入
```python
ci.disable()
```

## 注意事项
1. 注入的代码可以访问和修改函数内的局部变量
2. 行号是相对于函数定义的源代码行号，不包括空行和注释行
3. 对于动态生成的函数或没有源代码的函数(如内置函数)，注入将失败
4. 在多线程环境中使用时需要注意线程安全

## 原理说明
使用ast的形式对整体代码进行注入，注入后对lineno进行重排重新生成注入后的函数。python 3.12以上新增了模块sys.monitoring使用了更快捷的方法实现这种效果（如dowhen模块），但是ast更好的支持不同版本的python。

## 不足
目前对被修饰器修饰过的函数没有办法进行很好的注入，后续版本会进行优化。

