# Smart Doc Generator

**自动从源代码生成专业的 API 文档**

[English](README.md) | 简体中文

---

## 📖 简介

Smart Doc Generator 是一款智能代码文档生成工具，能够自动分析源代码并生成格式规范的 Markdown API 文档。支持 Python、JavaScript、TypeScript 等多种编程语言。

## ✨ 特性

- 🚀 **多语言支持**: Python、JavaScript、TypeScript
- 📝 **智能解析**: 自动提取函数签名、参数、返回值
- 🎨 **美观的输出**: 生成格式规范的 Markdown 文档
- 🔧 **简单易用**: 支持 CLI 和 Python API
- 📂 **批量处理**: 支持目录递归扫描

## 🛠️ 安装

```bash
# 克隆项目
git clone https://github.com/196408245/smart-doc-gen.git
cd smart-doc-gen

# 安装依赖
pip install -r requirements.txt
```

## 📚 使用方法

### CLI 使用

```bash
# 分析单个文件
python main.py --source main.py --output docs/api.md

# 分析整个目录
python main.py --source ./src --output docs/api.md --name "MyProject"

# 使用项目名
python main.py --source ./src --name "AwesomeProject" --output README.md
```

### Python API

```python
from main import SmartDocGenerator

# 创建生成器
generator = SmartDocGenerator(author="your@email.com")

# 生成文档
doc = generator.generate_docs(
    source_path="./src",
    output_path="docs/api.md",
    project_name="MyProject"
)

print(doc)
```

## 📋 输出示例

生成的文档包含：

- 项目标题和元信息
- 自动生成的目录
- 每个函数的详细文档
  - 函数名和签名
  - 装饰器列表
  - 参数列表
  - 返回值类型
  - 文档字符串

## 🧪 示例

### 输入代码

```python
def calculate_sum(a: int, b: int) -> int:
    """
    计算两个数的和
    
    Args:
        a: 第一个数
        b: 第二个数
    
    Returns:
        两数之和
    """
    return a + b
```

### 生成的文档

```markdown
# MyProject API Documentation

**Source File:** `main.py`

---

## Functions

### `calculate_sum`

**Parameters:**
- `a`
- `b`

**Returns:** `int`

**Description:**
计算两个数的和

Args:
    a: 第一个数
    b: 第二个数

Returns:
    两数之和
```

## 🔧 配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--source` | 源代码路径 | 必需 |
| `--output` | 输出文件路径 | 标准输出 |
| `--name` | 项目名称 | 文件/目录名 |
| `--recursive` | 递归扫描目录 | False |

## 📦 依赖

- Python 3.7+

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👤 作者

**邮箱**: 196408245@qq.com

**GitHub**: [196408245](https://github.com/196408245)
