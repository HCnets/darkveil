# DarkVeil 技术手册

## 1. 架构概述

DarkVeil 采用分层架构：

```
┌─────────────────────────────────────┐
│           GUI Layer (PyQt6)         │
│  main_window → pages → widgets      │
├─────────────────────────────────────┤
│         Module Layer                │
│  scanner / exploit / report / autopilot │
├─────────────────────────────────────┤
│         Core Layer                  │
│  engine / db / config / logger      │
└─────────────────────────────────────┘
```

### 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| Engine | `core/engine.py` | 模块注册、事件系统、自动发现 |
| Database | `core/db.py` | SQLite CRUD、线程安全、快照管理 |
| Config | `core/config.py` | JSON 配置、点分路径访问、深合并 |
| Logger | `core/logger.py` | 多通道日志（控制台/文件/GUI回调）|

## 2. 数据库 Schema

```sql
-- 目标
CREATE TABLE targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host TEXT NOT NULL,
    ip TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- 端口
CREATE TABLE ports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id INTEGER NOT NULL,
    port INTEGER NOT NULL,
    state TEXT NOT NULL,
    service TEXT,
    version TEXT,
    banner TEXT,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (target_id) REFERENCES targets(id)
);

-- 漏洞
CREATE TABLE vulnerabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id INTEGER NOT NULL,
    port_id INTEGER,
    vuln_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    evidence TEXT,
    recommendation TEXT,
    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (target_id) REFERENCES targets(id)
);

-- 利用记录
CREATE TABLE exploits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vuln_id INTEGER,
    module_name TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vuln_id) REFERENCES vulnerabilities(id)
);

-- 扫描历史（含快照）
CREATE TABLE scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_type TEXT NOT NULL,
    target TEXT NOT NULL,
    status TEXT NOT NULL,
    results_json TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP
);
```

## 3. 利用模块开发规范

### 接口要求

每个利用模块必须放在 `modules/exploit/modules/` 目录下，实现 `Exploit` 类：

```python
class Exploit:
    name = "module_name"           # 模块唯一标识
    description = "模块描述"        # 一句话说明
    author = "作者名"
    version = "1.0"
    vuln_type = "sqli"             # 漏洞类型
    severity = "HIGH"              # CRITICAL/HIGH/MEDIUM/LOW
    targets = ["Web"]              # 适用目标类型
    options = {                    # 可配置参数
        "timeout": {"type": "int", "default": 10, "desc": "超时"},
    }

    def __init__(self):
        self._output = []

    def log(self, msg):
        self._output.append(str(msg))

    def get_output(self):
        return "\n".join(self._output)

    def clear_output(self):
        self._output = []

    def check(self, target, port=None, **kwargs):
        """非破坏性漏洞检测，返回: vulnerable/not_vulnerable/error"""
        ...

    def execute(self, target, port=None, **kwargs):
        """执行利用，返回: success/failed/error"""
        ...
```

### 自动发现

`modules/exploit/manager.py` 的 `discover()` 方法使用 `pkgutil.iter_modules` 自动扫描 `modules/exploit/modules/` 目录，加载所有以 `_` 开头除外的模块。新模块放入目录即可自动加载。

### 爆破模块基类

继承 `modules/exploit/modules/_brute_base.py` 的 `BruteForceBase`：

```python
class MyBrute(BruteForceBase):
    protocol = "myproto"
    default_port = 1234

    def _check_service(self, target, port, timeout):
        """检测服务是否可用"""
        ...

    def _try_login(self, target, port, user, pwd, timeout):
        """尝试登录，返回 True/False"""
        ...
```

## 4. 主题系统

### 架构

```
ThemeBase (engine.py)     # 抽象基类，定义颜色属性
    ├── ModernTheme        # Windows 10/11
    ├── XPLunaBase         # XP Luna 共用样式
    │   ├── XPLunaBlue
    │   ├── XPLunaSilver
    │   └── XPLunaOlive
    ├── Win2000Theme
    └── Win98Theme
```

### 添加新主题

1. 在 `gui/widgets/themes/` 创建新文件
2. 继承 `ThemeBase`，实现所有颜色属性
3. 在 `__init__.py` 的 `ALL_THEMES` 列表中注册
4. 主题通过 `objectName` 匹配 QSS 选择器，不使用内联样式

### 关键 objectName

| objectName | 用途 |
|------------|------|
| `panel` | 面板容器 |
| `panel_header` | 面板标题栏 |
| `panel_body` | 面板内容区 |
| `stat_value` | 统计数字 |
| `stat_label` | 统计标签 |
| `activity_item` | 活动列表项 |
| `nav_btn` | 侧边栏导航按钮 |
| `title` / `subtitle` | 页面标题/副标题 |
| `terminal` | 终端输出区 |
| `primary` / `danger` | 主按钮/危险按钮 |

## 5. 线程模型

- GUI 线程: PyQt6 事件循环
- 工作线程: `QThread` 子类（ScanWorker、ExploitWorker、AutoPilotWorker、HoneypotWorker、CaptureWorker）
- 信号桥: `pyqtSignal` 从工作线程传递数据到 GUI 线程
- 数据库锁: `threading.Lock` 保护 SQLite 写操作
- 取消机制: `cancelled` 标志位 + `stop()` 方法

## 6. 配置系统

配置文件 `darkveil.json`，使用点分路径访问：

```python
config.get("scan.max_threads", 100)    # 读取
config.set("proxy.enabled", True)      # 写入（自动保存）
```

### 配置项

| 路径 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `scan.max_threads` | int | 100 | 最大扫描线程 |
| `scan.timeout` | float | 2.0 | TCP 连接超时 |
| `scan.web_timeout` | int | 10 | HTTP 请求超时 |
| `proxy.enabled` | bool | false | 代理开关 |
| `proxy.http` | str | "" | HTTP 代理 |
| `proxy.https` | str | "" | HTTPS 代理 |
| `proxy.socks5` | str | "" | SOCKS5 代理 |
| `ui.theme` | str | "modern" | 当前主题 |
| `ui.window_width` | int | 1400 | 窗口宽度 |
| `ui.window_height` | int | 900 | 窗口高度 |

## 7. 报告系统

### Markdown/HTML

`modules/report/generator.py` 的 `ReportGenerator` 类从数据库读取数据生成报告：
- `generate_markdown()`: 返回 Markdown 字符串
- `generate_html()`: 返回 HTML 字符串（内联 CSS）
- `_md_to_html()`: 基础 Markdown→HTML 转换

### PDF

`modules/report/pdf_generator.py` 使用 fpdf2：
- 自动检测系统中文字体（微软雅黑/宋体/黑体）
- `generate_pdf(db, output_path)`: 生成 PDF 文件
- 支持表格、严重程度颜色编码、分页

## 8. 依赖

| 包 | 用途 | 必需 |
|----|------|------|
| PyQt6 | GUI 框架 | 是 |
| requests | HTTP 请求 | 是 |
| pyqtgraph | 图表 | 是 |
| numpy | 数值计算 | 是 |
| fpdf2 | PDF 生成 | 是 |
| paramiko | SSH 爆破 | 否 |
| pymysql | MySQL 爆破 | 否 |

## 9. 安全注意事项

- 所有 payload 使用分片/编码存储，避免 AV 启发式检测
- 数据库使用参数化查询，防止 SQL 注入
- HTTP 请求禁用 SSL 验证（`verify=False`）用于测试环境
- 代理配置持久化在本地 JSON 文件
