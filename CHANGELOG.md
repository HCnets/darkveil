# Changelog

## v1.1.0 (2026-05-27)

### 缺陷修复
- 代理支持打通：所有 HTTP 利用模块（24个中的12个）现在正确使用 http_utils 共享 Session，代理配置生效
- rdp_brute 空壳修复：集成 xfreerdp 进行真实 RDP 爆破（需安装 xfreerdp）
- smb_brute 空壳修复：集成 impacket 进行 SMB 认证爆破（需安装 impacket），含空会话检测
- AutoPilot 攻击链接入 cve_checker 模块，自动检测 CVE/框架漏洞
- Dashboard refresh() 异常处理改进，不再静默吞掉错误

### Dashboard 增强
- QTimer 每 15 秒自动刷新，无需手动切页
- 新增漏洞趋势折线图（近 30 天，调用 get_vuln_timeline）
- 扫描状态指示器（绿点=扫描中，灰点=空闲）
- 活动列表增量更新，避免每次刷新重建

### 通知系统
- 新增 Toast 通知组件（gui/widgets/toast.py）
- 扫描完成时自动弹出通知（底部右侧滑入，5秒淡出）
- 发现高危漏洞时弹出红色告警通知

### 扫描器增强
- 新增"扫描历史"tab，显示近 50 条扫描记录
- 进度条显示当前扫描端口 + 预估剩余时间（ETA）
- 扫描结果自动写入 scan_history 表

### 利用页面增强
- 新增严重程度筛选下拉（全部/CRITICAL/HIGH/MEDIUM/LOW）
- Execute 按钮前增加确认对话框，防止误操作
- 选中模块时显示可编辑选项表单（timeout/threads 等），替代空 dict

### 目标页面增强
- 新增备注编辑区（QTextEdit + 保存按钮），数据持久化到 targets.notes
- 漏洞表格双击弹出详情对话框（完整描述/证据/修复建议/严重程度颜色编码）

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
