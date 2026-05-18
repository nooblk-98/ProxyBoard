from dataclasses import dataclass
from typing import Literal, NewType, Protocol, TypedDict

ConfigId = NewType("ConfigId", str)
DomainName = NewType("DomainName", str)
EmailAddr = NewType("EmailAddr", str)

ProtocolType = Literal["vless", "vmess"]


@dataclass(frozen=True)
class Result:
    success: bool
    message: str = ""


class XrayConfigDict(TypedDict, total=False):
    id: str
    name: str
    domain: str
    protocol: str
    enabled: bool
    ws_enabled: bool
    ws_port: int
    ws_path: str
    ws_uuid: str
    ws_email: str
    ws_host: str
    tls_enabled: bool
    tls_port: int
    tls_path: str
    tls_uuid: str
    tls_email: str
    tls_cert: str
    tls_key: str
    tls_host: str
    dns: str
    fingerprint: str
    alpn: str


class ConfigStore(Protocol):
    def get_store(self) -> dict: ...
    def add(self, config: dict) -> Result: ...
    def update(self, config_id: str, fields: dict) -> Result: ...
    def delete(self, config_id: str) -> Result: ...
    def toggle(self, config_id: str) -> Result: ...
    def replace_all(self, configs: list[dict]) -> Result: ...
    def read_xray_config(self) -> str: ...
    def write_xray_config(self, config: dict) -> None: ...
