import ast
from collections import defaultdict, deque
import hashlib


class InjectorTransformer(ast.NodeTransformer):

    def __init__(self, injections):
        self.injections = defaultdict(list)
        # 展开注入代码，用行数进行存储
        for line, inject in injections:
            self.injections[line].append(inject)

        self.curr_body = None
        self.body_stack = []
        # 改用更稳定的标识符来跟踪已注入的位置
        self.injected_markers = set()
        

    def _create_injection_marker(self, original_lineno, inject_code, position):
        """创建唯一的注入标记"""
        marker_content = f"{original_lineno}:{inject_code}:{position}"
        return hashlib.md5(marker_content.encode()).hexdigest()[:16]

    def _has_injection_marker(self, node, marker):
        """检查节点是否已经包含注入标记"""
        if hasattr(node, '_injection_markers'):
            return marker in node._injection_markers
        return False

    def _add_injection_marker(self, node, marker):
        """为节点添加注入标记"""
        if not hasattr(node, '_injection_markers'):
            node._injection_markers = set()
        node._injection_markers.add(marker)

    def _is_injected_node(self, node):
        """检查节点是否为之前注入的节点"""
        return hasattr(node, '_is_injected') and node._is_injected

    def _mark_as_injected(self, node):
        """标记节点为注入节点"""
        node._is_injected = True
    
    def _reassign_line_numbers(self, body):
        """重新分配body中所有语句的行号，确保连续性"""
        if not body:
            return
            
        # 找到第一个原始节点的行号作为基准
        base_lineno = 1
        for stmt in body:
            if (hasattr(stmt, 'lineno') and 
                stmt.lineno > 0 and 
                not self._is_injected_node(stmt)):
                base_lineno = stmt.lineno
                break
        
        # 重新分配所有语句的连续行号
        current_lineno = base_lineno
        for stmt in body:
            stmt.lineno = current_lineno
            # 设置结束行号
            if hasattr(stmt, 'end_lineno'):
                stmt.end_lineno = current_lineno
            current_lineno += 1

    def visit(self, node):
        # 进入作用域：压栈并更新当前body
        if hasattr(node, 'body'):
            self.body_stack.append(self.curr_body)
            self.curr_body = node.body
        
        result = super().visit(node)
        
        # 在访问完所有子节点后，一次性处理当前body的所有注入
        if hasattr(node, 'body') and self.curr_body:
            self._process_body_injections(self.curr_body)
        
        # 退出作用域：弹栈恢复父级body
        if hasattr(node, 'body'):
            self.curr_body = self.body_stack.pop()
        
        return result
    
    def _process_body_injections(self, body):
        """一次性处理整个body的所有注入,确保正确的顺序"""
        if not body:
            return
            
        # 收集所有需要注入的操作：(原始索引, 插入位置偏移, 注入顺序, 注入节点列表)
        all_injections = []
        injection_order = 0  # 用于保持注入的原始顺序
        
        for i, stmt in enumerate(body):
            if hasattr(stmt, 'lineno') and isinstance(stmt, ast.stmt) and stmt.lineno in self.injections and not self._is_injected_node(stmt):
                # 有行号而且是语句而且该行号有注入且该语句并非注入
                original_lineno = stmt.lineno
                indent = getattr(stmt, 'col_offset', 0)
                
                for inject in self.injections[original_lineno]:
                    # 创建注入标记
                    marker = self._create_injection_marker(
                        original_lineno, inject["code"], inject["position"]
                    )
                    
                    # 检查是否已经注入过
                    if self._has_injection_marker(stmt, marker):
                        continue
                    
                    # 创建注入节点
                    try:
                        injected_nodes = ast.parse(inject["code"]).body
                    except SyntaxError:
                        print("[WARING] Inject code has syyntax error:{}".format(inject["code"]))
                        continue
                    
                    # 处理注入节点
                    processed_nodes = []
                    for inj_node in injected_nodes:
                        inj_node.col_offset = indent
                        inj_node.lineno = 0  # 待分配
                        self._mark_as_injected(inj_node)
                        processed_nodes.append(inj_node)
                    
                    # 确定插入位置
                    if inject["position"] == "-":
                        # 在当前语句前插入
                        all_injections.append((i, 0, injection_order, processed_nodes))
                    else:  # position == "+"
                        # 在当前语句后插入
                        all_injections.append((i, 1, injection_order, processed_nodes))
                    
                    injection_order += 1
                    
                    # 标记已注入
                    self._add_injection_marker(stmt, marker)
        
        # 按原始索引、偏移和注入顺序排序，确保插入顺序正确
        all_injections.sort(key=lambda x: (x[0], x[1], x[2]))
        
        # 从后往前执行插入，避免索引偏移问题
        for original_idx, offset, _, nodes in reversed(all_injections):
            insert_pos = original_idx + offset
            # 逆序插入节点组，保持组内顺序
            for inj_node in reversed(nodes):
                body.insert(insert_pos, inj_node)
        
        # 重新分配行号
        if all_injections:
            self._reassign_line_numbers(body)

