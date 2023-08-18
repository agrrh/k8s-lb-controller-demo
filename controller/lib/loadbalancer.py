from dataclasses import dataclass
from typing import Optional
from kubecrd import KubeResourceBase


@dataclass
class Port(object):
    name: str = "http"
    port: int = 80


@dataclass
class Service(object):
    name: str
    namespace: Optional[str]
    port: Port


@dataclass
class LoadBalancer(KubeResourceBase):
    __group__ = "agrrh.com"
    __version__ = "v1alpha1"

    port: Port
    service: Service
    ready: bool = False
    address: str = ""


if __name__ == "__main__":
    print(LoadBalancer.crd_schema())
