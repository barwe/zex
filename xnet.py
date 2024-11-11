import re
import socket


def is_ip_port_open(ip: str, port: int, timeout=1):
    """Whether the address `'{ip}:{port}'` is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        code = sock.connect_ex((str(ip), int(port)))
    except socket.gaierror:
        return False
    else:
        return code == 0


def is_valid_ip_str(ip: str):
    """Whether the ip is a visually valid string."""
    r = re.match(r"\d+\.\d+.\d+.\d+", ip)
    return r is not None
