# DarkVeil

攻防一体安全评估平台 — Python + PyQt6 桌面应用

## 功能概览

| 模块 | 说明 |
|------|------|
| 控制中心 | 数据概览、漏洞分布图表、端口服务统计、最近活动 |
| 漏洞扫描 | TCP 端口扫描、服务识别、Web 漏洞检测、Nmap XML 导入 |
| 漏洞利用 | 27 个内置利用模块，分类筛选、搜索、检测/执行 |
| 渗透向导 | 自动化攻击链：扫描→识别→检测→利用→报告，一键完成 |
| 目标管理 | 目标列表、端口/漏洞详情、CVE 匹配、快照对比 |
| 实用工具 | 编码/解码（Base64/URL/Hex/Unicode/XOR/chr）、WAF 绕过 payload |
| 流量监控 | TCP/UDP/原始套接字捕获，多端口并发监听 |
| 蜜罐系统 | SSH/HTTP/Telnet 虚假服务，记录攻击者连接和数据 |
| 安全报告 | Markdown/HTML/PDF 三种格式导出 |
| 系统设置 | 6 套主题切换、代理配置 |

## 内置利用模块（27 个）

### 漏洞检测
- SQL 注入、SSRF、命令注入、文件上传、CVE 检查、CORS、未授权访问

### 暴力破解
- SSH、FTP、MySQL、RDP、SMB、SNMP、HTTP Basic、JWT、Redis、PostgreSQL、SMTP

### 信息收集
- SSH 版本枚举、子域名枚举、目录扫描、主机发现、DNS Zone Transfer、子域名接管

### 渗透利用
- 权限提升检查、API Fuzzing、反向 Shell 生成

## 主题

- Modern (Windows 10/11)
- XP Luna Blue / Silver / Olive
- Windows 2000
- Windows 98

## 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/darkveil.git
cd darkveil

# 安装依赖
pip install -r requirements.txt

# 启动
python main.py
```

### 可选依赖

```bash
# SSH 爆破需要
pip install paramiko

# MySQL 爆破需要
pip install pymysql
```

## 项目结构

```
darkveil/
├── main.py                    # 程序入口
├── core/
│   ├── config.py              # 配置管理
│   ├── db.py                  # SQLite 数据库
│   ├── engine.py              # 模块引擎
│   └── logger.py              # 日志系统
├── gui/
│   ├── main_window.py         # 主窗口
│   ├── pages/                 # 功能页面
│   │   ├── scanner_page.py    # 漏洞扫描
│   │   ├── exploit_page.py    # 漏洞利用
│   │   ├── autopilot_page.py  # 渗透向导
│   │   ├── target_page.py     # 目标管理
│   │   ├── tools_page.py      # 实用工具
│   │   ├── monitor_page.py    # 流量监控
│   │   ├── honeypot_page.py   # 蜜罐系统
│   │   └── report_page.py     # 安全报告
│   └── widgets/
│       ├── dashboard.py       # 控制中心
│       ├── result_table.py    # 通用表格
│       ├── terminal_widget.py # 终端
│       ├── global_search.py   # 全局搜索
│       ├── compare_dialog.py  # 扫描对比
│       └── themes/            # 主题引擎
├── modules/
│   ├── scanner/               # 扫描器
│   │   ├── port_scanner.py    # 端口扫描
│   │   ├── service_detector.py# 服务识别
│   │   └── web_scanner.py     # Web 扫描
│   ├── exploit/               # 利用模块
│   │   ├── manager.py         # 模块管理器
│   │   ├── dict_manager.py    # 字典管理
│   │   └── modules/           # 24 个利用模块
│   ├── report/                # 报告生成
│   │   ├── generator.py       # Markdown/HTML
│   │   └── pdf_generator.py   # PDF
│   ├── autopilot.py           # 自动化攻击链
│   ├── cve_matcher.py         # CVE 匹配
│   ├── nmap_importer.py       # Nmap 导入
│   └── http_utils.py          # HTTP 工具
└── resources/
    └── wordlists/             # 字典文件
```

## 使用说明

### 快速扫描
1. 在"漏洞扫描"页面输入目标 IP 或域名
2. 选择扫描类型（端口/Web/全面）
3. 点击"开始扫描"

### 渗透向导
1. 在"渗透向导"页面输入目标
2. 选择扫描模式（快速/全端口/自定义）
3. 可选启用"自动利用"
4. 点击"开始攻击"，7 个阶段自动执行

### CVE 匹配
1. 先扫描目标使其有端口和服务版本数据
2. 进入"目标管理"页面，点击"CVE 匹配扫描"
3. 自动匹配已知 CVE 并写入数据库

### 扫描对比
1. 扫描目标后点击"创建快照"
2. 一段时间后再次扫描，创建第二个快照
3. 点击"对比扫描"查看新增/消失的端口和漏洞

## 技术栈

- **语言**: Python 3.10+
- **GUI**: PyQt6
- **图表**: pyqtgraph + numpy
- **数据库**: SQLite
- **PDF**: fpdf2
- **网络**: requests, socket

## 许可证

MIT License
