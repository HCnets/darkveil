# Changelog

## v1.0.0 (2026-05-27)

### 核心架构
- Python + PyQt6 桌面应用框架
- SQLite 持久化存储（目标/端口/漏洞/利用/扫描历史）
- 插件式利用模块架构（pkgutil 自动发现）
- 主题引擎（6 套主题运行时切换）

### 扫描能力
- TCP 端口扫描（多线程，最多 200 并发）
- 服务指纹识别（SSH/FTP/SMTP/MySQL/Redis/HTTP）
- Web 漏洞扫描（敏感文件/SQLi/XSS/安全头审计）
- Nmap XML 导入解析

### 利用模块（24 个）
- 漏洞检测: SQL注入、SSRF、命令注入、文件上传、CVE检查、CORS、未授权访问
- 暴力破解: SSH、FTP、MySQL、RDP、SMB、SNMP、HTTP Basic、JWT
- 信息收集: SSH版本枚举、子域名枚举、目录扫描、主机发现、DNS Zone Transfer、子域名接管
- 渗透利用: 权限提升检查、API Fuzzing、反向Shell生成
- 爆破框架: 共用基类 + 字典管理器（笛卡尔积/按行配对）

### 自动化
- AutoPilot 渗透向导（7 阶段攻击链）
- 服务→模块自动匹配（9 种协议映射）
- 一键渗透：扫描→识别→检测→利用→报告

### 安全检测
- CVE 版本匹配（18 种服务本地数据库 + NVD API）
- 权限提升检测（SUID/sudo/kernel/cron/Windows 服务）

### UI/UX
- 10 个功能页面（侧边栏导航）
- Dashboard 数据可视化（pyqtgraph 柱状图）
- 全局搜索（跨目标/端口/漏洞）
- 分类筛选 + 关键词过滤（利用模块页面）
- 扫描对比（快照 diff，新增/消失高亮）
- 手动添加/删除目标

### 报告导出
- Markdown 格式
- HTML 格式（内联 CSS）
- PDF 格式（fpdf2，中文支持）

### 工具集
- 编码/解码: Base64、URL、HTML Entity、Hex、Unicode、ROT13、XOR、PHP chr()、JS fromCharCode
- WAF 绕过: SQL注入/XSS/命令注入/路径遍历（4 类 32 种 payload）

### 网络功能
- 流量监控: TCP/UDP/原始套接字捕获
- 蜜罐系统: SSH/HTTP/Telnet 虚假服务
- 代理支持: HTTP/HTTPS/SOCKS5

### 工程化
- 日志持久化（darkveil.log）
- 配置持久化（darkveil.json）
- 线程安全（QThread + SQLite Lock）
- AV 安全编码（payload 分片/编码避免启发式检测）
