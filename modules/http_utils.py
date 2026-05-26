import requests

requests.packages.urllib3.disable_warnings()


def get_session(config=None):
    """Create a requests.Session with proxy and default settings from config."""
    session = requests.Session()
    session.verify = False
    session.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    if config:
        proxy_cfg = config.get("proxy", {})
        if isinstance(proxy_cfg, dict) and proxy_cfg.get("enabled"):
            proxies = {}
            http_proxy = proxy_cfg.get("http", "").strip()
            https_proxy = proxy_cfg.get("https", "").strip()
            socks5_proxy = proxy_cfg.get("socks5", "").strip()

            if socks5_proxy:
                proxies = {
                    "http": f"socks5h://{socks5_proxy}",
                    "https": f"socks5h://{socks5_proxy}",
                }
            else:
                if http_proxy:
                    proxies["http"] = http_proxy
                if https_proxy:
                    proxies["https"] = https_proxy

            if proxies:
                session.proxies = proxies

        timeout = config.get("scan.web_timeout", 10)
        session.timeout = timeout

    return session


def get_proxies_dict(config):
    """Get a proxies dict for requests.get/post calls."""
    if not config:
        return None
    proxy_cfg = config.get("proxy", {})
    if not isinstance(proxy_cfg, dict) or not proxy_cfg.get("enabled"):
        return None

    proxies = {}
    socks5 = proxy_cfg.get("socks5", "").strip()
    if socks5:
        return {"http": f"socks5h://{socks5}", "https": f"socks5h://{socks5}"}

    http_proxy = proxy_cfg.get("http", "").strip()
    https_proxy = proxy_cfg.get("https", "").strip()
    if http_proxy:
        proxies["http"] = http_proxy
    if https_proxy:
        proxies["https"] = https_proxy
    return proxies or None
