# Changelog

## v2.0.0 (2026-05-27)

### 漏洞情报对接
- 新增 NVD 漏洞库客户端（关键词/CVE-ID/CPE 查询，API key 支持，缓存）
- 新增 Shodan 资产情报客户端（主机查询/搜索/漏洞关联，可选 shodan 库）
- 新增 Fofa 资产搜索引擎客户端（Base64 编码查询，email+key 认证）
- 新增"情报中心"页面，三 Tab 布局（NVD/Shodan/Fofa），异步查询
- 情报查询结果自动缓存到 intel_queries 表（TTL 可配置）

### 后渗透扩展（7 个新模块）
- lateral_psexec: SMB PsExec 横向移动（impacket，服务创建执行）
- lateral_wmi: WMI 远程执行（DCOM 连接，Win32_Process.Create）
- cred_dump: 凭据提取（SAM/Shadow/SSH 密钥/浏览器密码/WiFi 密码）
- tunnel_reverse: 反向 Shell 监听器（等待目标回连，交互式会话）
- tunnel_portforward: TCP 端口转发（本地端口映射到远程端口）
- persistence_check: 持久化机制检测（计划任务/启动项/服务/SSH/WMI/Systemd）
- persistence_install: 持久化安装/清除（cron/startup/systemd/ssh/profile）

### 报告升级
- 新增 OWASP Top 10 2021 合规映射（15 种 vuln_type 自动分类）
- 新增 CIS Benchmark 合规映射（12 个控制项）
- 新增风险矩阵（严重程度 × 可能性 网格）
- PDF 导出新增封面页（公司名称/Logo/日期/机密标记）
- PDF 导出新增目录页
- PDF 导出新增 OWASP/CIS/风险矩阵章节
- 报告页面新增公司信息栏（名称输入 + Logo 路径浏览）
- 报告页面新增合规复选框（OWASP Top 10/CIS Benchmark/风险矩阵）
- CVE 匹配和 AutoPilot 写入漏洞时自动标记 OWASP 分类

### 新增主题（3 个）
- Cyberpunk: 深黑底 + 霓虹青/品红发光边框，Cascadia Mono 字体，赛博朋克黑客风
- Dracula: 紫调暗色主题，社区经典配色，Cascadia Mono 字体
- Nord: 冷蓝灰暗色，极简克制的北欧风，Segoe UI 字体

### 新增功能模块（8 个）
- ping_sweep: 网络主机发现（ICMP 原始套接字 + TCP 连接回退，CIDR/范围解析）
- ssl_checker: SSL/TLS 证书分析（协议版本枚举、密码套件、证书有效性/密钥/签名算法）
- sniffer: 本地网络嗅探统计（原始套接字 SYN 捕获 + netstat 连接分析）
- header_analyzer: HTTP 安全头审计（8 项安全头检查）+ 响应信息泄露检测 + Cookie 安全 + CORS
- xxe_scanner: XXE 注入检测（文件读取/SSRF/参数实体/JSON XXE/SVG payload）
- open_redirect: 开放重定向检测（30+ 常见重定向参数 + Meta refresh/JS 重定向）
- host_header_inject: Host Header 注入（X-Forwarded-Host/X-Host/双 Host 头/缓存投毒）
- hash_crack: 哈希识别 + 字典破解（MD5/SHA1/SHA256/SHA512/NTLM/bcrypt，盐值支持）

### 红队对抗测试模块（10 个，用于 Formless 杀软验证）
- eicar_generator: EICAR 标准测试文件生成（静态检测验证，多种变体：压缩/编码/嵌入/双扩展名）
- shellcode_injector: 进程注入测试（远程线程注入/DLL 注入/进程镂空，NOP+INT3 无害 payload）
- ransomware_sim: 勒索软件行为模拟（文件发现→密钥生成→批量加密→勒索信投放，干跑模式安全）
- keylogger_sim: 键盘记录行为模拟（GetAsyncKeyState 轮询/SetWindowsHookEx 钩子）
- file_encryptor: 文件批量加密测试（XOR/RC4/AES，干跑模式，支持恢复）
- c2_beacon: C2 信标行为模拟（HTTP/HTTPS/DNS/TCP 回连，随机 UA+抖动间隔）
- process_hollow: 进程镂空/傀儡进程测试（NtUnmapViewOfSection/WriteProcessMemory/APC 注入）
- av_evasion: 杀软规避技术测试（AMSI 绕过/ETW 补丁/UAC 绕过/Defender 规避）
- credential_dump: 凭据转储测试（LSASS 内存/SAM 注册表/DPAPI/浏览器凭据/Credential Guard）

### 基础设施
- DB 新增 intel_queries 表（情报缓存）
- vulnerabilities 表新增 owasp_category 和 cwe_id 列
- Config 新增 intel 配置节（NVD/Shodan/Fofa API key + 缓存 TTL）

## v1.3.2 (2026-05-27)

### 输入验证
- 扫描页面新增目标格式验证（IP/域名/URL 格式检查）
- 利用页面新增目标格式验证
- 配置文件启动时自动验证（max_threads/timeout 范围检查）

### 代码质量
- Logger 回调异常现在记录到日志而非静默吞掉
- 模块加载失败时列出所有失败模块及原因
- 配置验证错误自动修正并保存

## v1.3.1 (2026-05-27)

### 安全修复
- 修复报告生成器 XSS 漏洞：HTML 输出现在正确转义用户内容
- 修复 privesc_check 模块 shell=True 风险：改用 shlex.split 参数列表
- 修复 socket.setdefaulttimeout 全局竞争条件：subdomain_enum/subdomain_takeover 改用单 socket 超时

### 线程安全修复
- 修复 brute-base _stop 标志线程安全：改用 threading.Event
- 修复 DB 抽象绕过：honeypot_page/target_page 不再直接访问 db._lock 和 db.conn
- 新增 db.delete_target() 和 db.clear_honeypot_captures() 方法

### 代码质量
- 修复 ExploitBase 可变类默认值：targets/options 改为 None + __init__ 初始化
- 修复 http_utils session.timeout 无效：改用 session._default_timeout 存储
- Dashboard 定时器仅在可见时刷新，避免无效 SQL 查询
- 应用退出时清理所有运行中的 worker 线程和数据库连接
- 修正 README 模块数量（24→27）

## v1.3.0 (2026-05-27)

### 流量监控增强
- TCP 模式新增协议解析：自动识别 HTTP 请求/响应、SSH 握手、DNS 查询
- 新增"解析模式"复选框，可切换原始数据/协议解析视图

### 报告增强
- 新增执行摘要：风险评分（0-100）、Top 3 关键发现、修复建议
- 新增章节选择：可勾选执行摘要/目标详情/漏洞汇总/高危详情/扫描历史
- 风险等级自动计算：高危（50+）、中危（20+）、低危（1+）、安全（0）

## v1.2.0 (2026-05-27)

### 新增模块
- redis_brute: Redis AUTH 弱口令爆破（原生 socket，支持无密码检测）
- postgres_brute: PostgreSQL 弱口令爆破（需 psycopg2）
- smtp_brute: SMTP LOGIN 弱口令爆破（标准库 smtplib，支持 STARTTLS）

### 蜜罐增强
- 蜜罐捕获数据持久化到 honeypot_captures 表，重启后不丢失
- 新增"捕获历史"tab，显示近 100 条捕获记录
- 支持清空历史记录

### AutoPilot 增强
- 攻击链新增 Redis/PostgreSQL/SMTP 服务自动匹配

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
