from collections import defaultdict
import ast, astor
import inspect
from vigil.ast_injector import InjectorTransformer


class CodeInjector:

    __disable = False

    def __init__(self):
        self.injections = defaultdict(lambda:defaultdict(list))
        self.original_functions = {}
        self.scope = {}

    def assign_function(self, func):
        self.scope[func.__name__] = func
        return self


    def register(self, func, line_number:int, code:str, position:str='-'):
        """动态注入"""
        if not inspect.isfunction(func) and not inspect.ismethod(func):
            raise TypeError("Target must be a function or a method")

        if func in self.original_functions:
            # 函数已经被存储了
            original_code, lines, start_line = self.original_functions[func]
        else:
            # 函数如果没被存储，则从获取并存储
            try:
                lines, start_line = inspect.getsourcelines(func)
            except (IOError, OSError) as e:
                raise ValueError("Could not get the source code for the function")

        self.original_functions[func] = (func.__code__, lines, start_line)

        # 如果行号不在合法范围内，直接报错
        if line_number < 1 or line_number > len(lines) - 1:
            raise ValueError(f"Line number {line_number} is out of range for function {func.__name__}. Valid line numbers are 1 to {len(lines)-1}")
        
        # 存储所有的修改
        self.injections[func][line_number + 1].append({'code':code, 'position':position})

        return self


    def _modify_function(self, func):
        # 获取原始函数信息
        original_code, lines, start_line = self.original_functions[func]

        func_name = func.__name__

        # 如果是其他层级的方法,需要将前面的indent全部去掉
        layer_indent = len(lines[0]) - len(lines[0].lstrip())
        if layer_indent > 0:
            # 存在其他层级
            # 需要将其他的层级进行往前去缩进
            lines = [line[layer_indent:] for line in lines]
            # 重新命名func_name
            func_name = "{}_{}".format(func.__qualname__.replace(".","_"), func.__name__)

        func_source_code = ''.join(lines)
        tree = ast.parse(func_source_code)

        # 主要函数主体节点
        func_node = tree.body[0] 

        # 重新命名函数
        func_node.name = func_name

        # 收集所有的注入
        injections = []
        for line_number, line_injections in self.injections[func].items():
            for inject in line_injections:
                injections.append((line_number, inject))

        # 排序
        injections.sort(key=lambda x:(x[0], 0 if  x[1]['position'] == "-" else 1))

        transformer = InjectorTransformer(injections=injections)
        modified_tree = transformer.visit(func_node)
        # 修复行号信息
        ast.fix_missing_locations(modified_tree)
        # print([n.lineno for n in modified_tree.body])

        # 重新编译函数
        modified_source_code = astor.to_source(modified_tree)
        # print(modified_source_code)
        # 在原始函数的全局命名空间中执行修改后的代码
        # scope = func.__globals__.copy()
        # 在ci里面构建一个scope环境
        exec(modified_source_code, self.scope)
        modified_func = self.scope[func_name]
        # 修改原始函数的__code__属性而非替换函数引用
        func.__code__ = modified_func.__code__


    def restore(self, func=None):
        """恢复"""
        if CodeInjector.__disable:
            return self

        CodeInjector.__disable = True

        if func is None:
            # 恢复所有函数
            for func, original in self.original_functions.items():
                original_code = original[0]
                func.__code__ = original_code
        else:
            if func in self.original_functions:
                original_code, _, _ = self.original_functions[func]  # 提取原始代码对象
                func.__code__ = original_code  # 恢复函数代码对象

        return self


    def enable(self, func=None):
        """启动应用"""
        CodeInjector.__disable = False

        if func is None:
            # 启动所有注入
            for func in self.injections.keys():
                self._modify_function(func)
        else:
            if func in self.injections:
                self._modify_function(func)

        return self


ci = CodeInjector()

