"""通信异常定义"""


class TransportError(Exception):
    """传输层异常基类"""
    pass


class ConnectionError(TransportError):
    """连接异常"""
    pass


class TimeoutError(TransportError):
    """超时异常"""
    pass


class SCPIError(Exception):
    """SCPI 协议异常"""
    pass
