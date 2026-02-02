# Clash订阅合并工具

## 项目简介
本项目采用 Vibe Coding 模式开发——核心逻辑全靠 AI，代码产出全凭氛围。

本工具专为 Clash Party 覆写功能量身定制，旨在快速生成配置文件。

避坑指南： 作者是一位有着 14 年经验的 Java 后端老兵，对 Python 的理解仅限于“能跑”。如果您在使用中遇到 Bug 或想提 Issue，建议直接 Fork 一份，让您的 AI 助教帮您改改——毕竟，代码是 AI 写的，它更懂它自己。

### 背景说明

在 Clash Party 中使用覆写功能时，通过 Sub-Store 方式组合多个订阅后，生成的配置只包含 `proxies` 配置，没有分流规则。本工具的作用是：

1. 从多个订阅源下载并合并代理节点
2. 生成**不含 `proxies:` 的覆写配置文件**
3. 用于 Clash Party 的覆写功能中，实现代理节点的快速合并

### 使用场景

```
Sub-Store 组合订阅 → [本工具处理] → 覆写配置文件 → Clash Party 覆写功能
```

生成的覆写文件可直接导入 Clash Party 的覆写功能，无需手动合并节点。

## 功能特性

- **多订阅源支持**：支持从多个 URL 订阅源下载配置文件
- **智能合并**：自动提取并合并所有订阅中的代理节点
- **Base64 解码**：支持自动解码 Base64 编码的订阅内容
- **URI 格式解析**：支持解析 trojan://、ss://、vless://、vmess:// 等多种 URI 格式
- **覆写专用输出**：生成仅含代理组和规则的覆写配置（不生成 `proxies:` 配置段）
- **格式转换**：将多行 YAML 格式转换为紧凑的 JSON 单行格式
- **灵活配置**：支持自定义配置和输出路径
- **日志记录**：详细的运行日志便于调试

## 项目结构

```
clash-party-merged-overwrite-pub/
├── clash_subscription_merger.py  # 主程序入口
├── requirements.txt              # 项目依赖
├── subscriptions.conf           # 订阅配置文件（示例）
├── README.md                    # 项目文档
├── modules/                     # 功能模块目录
│   ├── __init__.py
│   ├── config_parser.py         # 配置解析器
│   ├── http_downloader.py       # HTTP下载器
│   ├── yaml_processor.py        # YAML处理器
│   ├── format_converter.py      # 格式转换器
│   └── config_generator.py      # 配置生成器
├── sub-yamls/                   # 下载的订阅文件目录
├── merged-yamls/                # 合并后的输出目录
└── logs/                        # 日志目录
```

## 开发方式

本项目采用 **Vibe Coding（氛围编程）** 方式开发，通过 AI 辅助工具快速实现功能。

### 使用的工具

- **OpenCode**：AI 编程助手，提供智能代码补全、重构建议和上下文理解
- **OMO（OhMyOpenCode）**：专业的代码编排系统，具备：
  - 多代理协同工作能力（Sisyphus、Oracle、Metis、Momus 等）
  - 任务规划与分解
  - 代码质量检查
  - 自动化测试与验证

### 开发特点

- **快速迭代**：通过 AI 辅助快速实现功能，无需繁琐的重复性编码
- **代码质量**：AI 工具帮助保持代码风格一致性、类型安全和最佳实践
- **智能重构**：自动识别代码异味，提供重构建议
- **上下文感知**：AI 理解项目结构，减少上下文切换成本

### 技术栈

- **后端语言**：Python 3.8+
- **HTTP 库**：requests
- **配置解析**：PyYAML
- **开发工具**：OpenCode + OMO 插件

## 环境要求

- Python 3.8 或更高版本
- pip 包管理器

## 安装步骤（使用 venv）

### 1. 创建虚拟环境

```bash
# 进入项目目录
cd clash-party-merged-overwrite-pub

# 创建Python虚拟环境
python3 -m venv .venv 
```

### 2. 激活虚拟环境

**macOS/Linux：**
```bash
source .venv/bin/activate
```

**Windows：**
```bash
.venv\Scripts\activate
```

### 3. 安装依赖

```bash
# 升级pip（可选但推荐）
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 4. 验证安装

```bash
python clash_subscription_merger.py --help
```

如果看到帮助信息，说明安装成功。

## 配置说明

### 订阅配置文件格式

编辑 `subscriptions.conf` 文件，添加订阅配置：

```conf
# 格式：文件名|订阅URL
# 可以添加或删除订阅行来配置要合并的文件

subscription1.yaml|https://example.com/subscribe1
subscription2.yaml|https://example.com/subscribe2
```

### 配置项说明

- **文件名**：保存的订阅文件名（.yaml 或 .yml 后缀）
- **URL**：订阅源的完整 URL 地址

## 使用方法

### 基本用法

激活虚拟环境后，直接运行：

```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 运行程序
python clash_subscription_merger.py
```

### 命令行参数

```bash
# 查看所有可用参数
python clash_subscription_merger.py --help

# 参数说明：
#   --config, -c     订阅配置文件路径（默认：subscriptions.conf）
#   --output-dir, -o 输出目录路径（默认：merged-yamls）
#   --download-dir, -d 下载目录路径（默认：sub-yamls）
#   --dry-run, -n    预演模式，只显示结果不保存文件
#   --verbose, -v    详细日志输出
```

### 使用示例

```bash
# 基本运行
python clash_subscription_merger.py

# 预演模式（不保存文件）
python clash_subscription_merger.py --dry-run

# 使用自定义配置文件
python clash_subscription_merger.py --config my_subscriptions.conf

# 输出到指定目录
python clash_subscription_merger.py --output-dir ./output

# 详细日志输出
python clash_subscription_merger.py --verbose
```

### 关闭虚拟环境

```bash
deactivate
```

## 依赖说明

项目依赖以下 Python 包：

```
pyyaml>=6.0      # YAML解析库
requests>=2.28.0 # HTTP请求库
```

可选依赖（可在 requirements.txt 中取消注释）：

```
colorlog>=6.7.0  # 彩色控制台输出
tqdm>=4.64.0     # 进度条显示
```

## 输出说明

### 生成的文件

运行成功后，会在 `merged-yamls/` 目录下生成 `sub_by_opencode.yaml` 文件。

### 文件结构

生成的覆写配置文件包含以下部分（**不包含 `proxies:` 配置段**）：

```yaml
proxy-groups:
  - {...}
  - {...}
  - {...}
rules:
  - {...}
  - {...}
  ...
```

### 与普通 Clash 配置的区别

| 配置段 | 普通配置文件 | 本工具输出（覆写配置） |
|--------|-------------|----------------------|
| `proxy-groups` | ✅ 包含 | ✅ 包含 |
| `proxies` | ✅ 包含 | ❌ **不包含** |
| `rules` | ✅ 包含 | ✅ 包含 |
| `dns` | ✅ 包含 | ❌ 不包含 |
| `mixed-port` | ✅ 包含 | ❌ 不包含 |

覆写配置仅包含 `proxy-groups` 和 `rules` 部分，用于覆写到已有的完整配置中。

### 代理组说明

- **手动选择**：手动选择代理节点
- **自动选择**：自动测试并选择延迟最低的节点
- **故障转移**：在节点故障时自动切换到其他节点

## 常见问题

### 1. 虚拟环境相关

**问：如何确认虚拟环境已激活？**
激活虚拟环境后，命令行提示符会显示 `(venv)` 前缀。

**问：如何删除虚拟环境？**
```bash
deactivate
rm -rf .venv  # 删除虚拟环境目录
```

### 2. 订阅下载相关

**问：下载失败怎么办？**
- 检查 URL 是否正确
- 检查网络连接
- 使用 `--verbose` 参数查看详细错误信息

**问：支持哪些订阅格式？**
- Base64 编码的 YAML
- 原生 YAML 格式
- URI 格式（trojan://、ss://、vless://、vmess:// 等）

### 3. 代理节点相关

**问：为什么提取的节点数为 0？**
- 检查订阅内容是否有效
- 确认订阅包含 `proxies` 配置段
- 使用 `--verbose` 查看详细日志

### 4. 输出文件相关

**问：输出文件在哪里？**
默认输出到 `merged-yamls/sub_by_opencode.yaml`

**问：如何自定义输出文件名？**
修改 `clash_subscription_merger.py` 第 48 行：
```python
self.output_file = self.output_dir / "你的文件名.yaml"
```

## 更新日志

### v1.0.0 (2026)
- 初始版本发布
- 支持多订阅源下载和合并
- 支持多种代理协议
- 内置完整规则集

## 许可证

本项目基于 MIT 许可证开源。
