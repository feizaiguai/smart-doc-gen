#!/usr/bin/env python3
"""
Smart Doc Generator - 自动从源代码生成 API 文档
Author: 196408245@qq.com
"""

import ast
import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class DocGenerator:
    """文档生成器核心类"""
    
    def __init__(self, source_path: str, output_path: str = "docs"):
        self.source_path = Path(source_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    def extract_docstring(self, node: ast.AST) -> Optional[str]:
        """提取文档字符串"""
        if isinstance(node, ast.FunctionDef) and ast.get_docstring(node):
            return ast.get_docstring(node)
        if isinstance(node, ast.ClassDef) and ast.get_docstring(node):
            return ast.get_docstring(node)
        return None
    
    def get_function_signature(self, node: ast.FunctionDef) -> str:
        """获取函数签名"""
        args = node.args
        params = []
        
        # 处理普通参数
        for arg in args.args:
            param_name = arg.arg
            param_type = self._get_type_annotation(arg.annotation)
            if param_type:
                params.append(f"{param_name}: {param_type}")
            else:
                params.append(param_name)
        
        # 处理 *args 和 **kwargs
        if args.vararg:
            params.append(f"*{args.vararg.arg}")
        if args.kwarg:
            params.append(f"**{args.kwarg.arg}")
        
        return f"({', '.join(params)})"
    
    def _get_type_annotation(self, annotation) -> Optional[str]:
        """获取类型注解"""
        if annotation is None:
            return None
        return ast.unparse(annotation)
    
    def get_class_methods(self, node: ast.ClassDef) -> List[Dict]:
        """获取类的所有方法"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    'name': item.name,
                    'signature': self.get_function_signature(item),
                    'docstring': self.extract_docstring(item),
                    'is_static': any(isinstance(d, ast.StaticMethod) for d in item.decorator_list),
                    'is_classmethod': any(isinstance(d, ast.ClassMethod) for d in item.decorator_list),
                }
                methods.append(method_info)
        return methods
    
    def parse_file(self, filepath: Path) -> Dict:
        """解析单个 Python 文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            module_doc = ast.get_docstring(tree)
            
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': self.extract_docstring(node),
                        'methods': self.get_class_methods(node),
                        'bases': [ast.unparse(base) for base in node.bases if isinstance(base, ast.Name)]
                    }
                    classes.append(class_info)
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    # 模块级函数
                    func_info = {
                        'name': node.name,
                        'signature': self.get_function_signature(node),
                        'docstring': self.extract_docstring(node)
                    }
                    functions.append(func_info)
            
            return {
                'filepath': str(filepath),
                'module_doc': module_doc,
                'classes': classes,
                'functions': functions
            }
            
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return {'filepath': str(filepath), 'error': str(e), 'classes': [], 'functions': []}
    
    def generate_class_docs(self, class_info: Dict) -> str:
        """生成类的文档"""
        md = f"\n### Class: `{class_info['name']}`\n"
        
        if class_info['bases']:
            md += f"*Inherits from: {', '.join(class_info['bases'])}*\n"
        
        if class_info['docstring']:
            md += f"\n{class_info['docstring']}\n"
        
        if class_info['methods']:
            md += "\n**Methods:**\n"
            for method in class_info['methods']:
                md += f"\n#### `{method['name']}{method['signature']}`\n"
                if method['is_static']:
                    md += "*@staticmethod*\n"
                elif method['is_classmethod']:
                    md += "*@classmethod*\n"
                if method['docstring']:
                    md += f"{method['docstring']}\n"
        
        return md
    
    def generate_function_docs(self, func_info: Dict) -> str:
        """生成函数的文档"""
        md = f"\n### Function: `{func_info['name']}{func_info['signature']}`\n"
        if func_info['docstring']:
            md += f"\n{func_info['docstring']}\n"
        return md
    
    def generate_markdown(self, parsed_data: Dict) -> str:
        """生成 Markdown 文档"""
        filename = Path(parsed_data['filepath']).stem
        md = f"# {filename.title()} 模块文档\n\n"
        md += f"*Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        if parsed_data.get('error'):
            md += f"⚠️ **Error parsing file:** {parsed_data['error']}\n"
            return md
        
        if parsed_data.get('module_doc'):
            md += f"## 模块说明\n\n{parsed_data['module_doc']}\n"
        
        # 模块级函数
        if parsed_data['functions']:
            md += "\n## 模块函数\n"
            for func in parsed_data['functions']:
                md += self.generate_function_docs(func)
        
        # 类
        if parsed_data['classes']:
            md += "\n## 类\n"
            for cls in parsed_data['classes']:
                md += self.generate_class_docs(cls)
        
        return md
    
    def process(self) -> List[str]:
        """处理所有 Python 文件并生成文档"""
        output_files = []
        
        if self.source_path.is_file():
            files = [self.source_path]
        else:
            files = list(self.source_path.rglob("*.py"))
        
        for filepath in files:
            # 跳过 __pycache__ 和测试文件
            if '__pycache__' in str(filepath) or filepath.name.startswith('test_'):
                continue
            
            print(f"Processing: {filepath}")
            parsed = self.parse_file(filepath)
            md_content = self.generate_markdown(parsed)
            
            # 生成输出文件名
            rel_path = filepath.relative_to(self.source_path) if self.source_path.is_dir() else filepath.name
            output_file = self.output_path / f"{rel_path.stem}.md"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            output_files.append(str(output_file))
            print(f"  -> Generated: {output_file}")
        
        return output_files


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description='Smart Doc Generator - 从源代码自动生成 API 文档')
    parser.add_argument('source', help='源代码文件或目录路径')
    parser.add_argument('-o', '--output', default='docs', help='输出目录 (默认: docs)')
    parser.add_argument('-v', '--version', action='version', version='Smart Doc Generator v1.0.0')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source):
        print(f"Error: Source path '{args.source}' does not exist")
        return
    
    generator = DocGenerator(args.source, args.output)
    output_files = generator.process()
    
    print(f"\n✅ Successfully generated {len(output_files)} documentation files!")
    print(f"📁 Output directory: {args.output}")


if __name__ == "__main__":
    main()
