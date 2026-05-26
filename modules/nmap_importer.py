import xml.etree.ElementTree as ET


def parse_nmap_xml(xml_path):
    """Parse nmap XML output and return structured results."""
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        raise ValueError(f"XML 解析失败: {e}")
    except FileNotFoundError:
        raise ValueError(f"文件不存在: {xml_path}")

    root = tree.getroot()
    results = []

    for host_elem in root.findall(".//host"):
        host_info = {"hostnames": [], "ports": [], "os": "", "state": ""}

        # Host state
        status = host_elem.find("status")
        if status is not None:
            host_info["state"] = status.get("state", "")

        # IP address
        addr_elem = host_elem.find("address[@addrtype='ipv4']")
        if addr_elem is None:
            addr_elem = host_elem.find("address[@addrtype='ipv6']")
        if addr_elem is not None:
            host_info["ip"] = addr_elem.get("addr", "")

        # Hostnames
        for hostname in host_elem.findall(".//hostname"):
            name = hostname.get("name", "")
            if name:
                host_info["hostnames"].append(name)

        # Ports
        for port_elem in host_elem.findall(".//port"):
            port_info = {}

            port_id = port_elem.get("portid", "")
            protocol = port_elem.get("protocol", "tcp")
            try:
                port_info["port"] = int(port_id)
            except (ValueError, TypeError):
                continue
            port_info["protocol"] = protocol

            # State
            state_elem = port_elem.find("state")
            if state_elem is not None:
                port_info["state"] = state_elem.get("state", "")

            # Service
            service_elem = port_elem.find("service")
            if service_elem is not None:
                port_info["service"] = service_elem.get("name", "")
                port_info["version"] = ""
                product = service_elem.get("product", "")
                version = service_elem.get("version", "")
                extra = service_elem.get("extrainfo", "")
                if product:
                    port_info["version"] = product
                    if version:
                        port_info["version"] += " " + version
                elif version:
                    port_info["version"] = version
                port_info["banner"] = f"{product} {version} {extra}".strip()

                # Also store raw service fingerprint fields
                port_info["product"] = product
                port_info["service_extra"] = extra

            host_info["ports"].append(port_info)

        # OS detection
        for osmatch in host_elem.findall(".//osmatch"):
            host_info["os"] = osmatch.get("name", "")
            break

        if host_info.get("ports"):
            results.append(host_info)

    return results


def import_to_db(results, db, logger=None):
    """Import parsed nmap results into the database."""
    imported_hosts = 0
    imported_ports = 0

    for host_info in results:
        ip = host_info.get("ip", "")
        hostnames = host_info.get("hostnames", [])
        host = hostnames[0] if hostnames else ip

        if not host:
            continue

        target_id = db.get_or_create_target(host, ip)
        if not target_id:
            continue

        imported_hosts += 1

        for port_info in host_info.get("ports", []):
            if port_info.get("state") not in ("open", "open|filtered"):
                continue

            service = port_info.get("service", "")
            version = port_info.get("version", "")
            banner = port_info.get("banner", "")

            db.add_port(
                target_id,
                port_info["port"],
                port_info.get("state", "open"),
                service or None,
                version or None,
                banner or None,
            )
            imported_ports += 1

    if logger:
        logger.info(f"Nmap 导入完成: {imported_hosts} 个主机, {imported_ports} 个端口")

    return imported_hosts, imported_ports


def import_nmap_file(xml_path, db, logger=None):
    """Parse and import nmap XML file to database in one step."""
    results = parse_nmap_xml(xml_path)
    return import_to_db(results, db, logger)
