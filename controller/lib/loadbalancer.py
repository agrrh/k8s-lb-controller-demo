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
class Loadbalancer(KubeResourceBase):
    __group__ = "agrrh.com"
    __version__ = "v1alpha1"

    port: Port
    service: Service

    # TODO: Move this to ".status"
    ready: bool = False
    address: str = ""


if __name__ == "__main__":
    print(Loadbalancer.crd_schema())
