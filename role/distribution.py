from time import sleep
from typing import List

from pysyncobj import SyncObj

from ..config.env import env
from ..config.logger import log
from .discovery import host_ip, port


class Distributed(SyncObj):
    # Peer data structure
    cluster_name = env["CLUSTER"]["NAME"]
    peers: List[str] = env["CLUSTER"]["INITIAL_PEERS"]
    distributed_objects: List["Distributed"] = []

    def __init__(self, name: str, consumers: List[str] = None):
        if not consumers:
            consumers = []
        SyncObj.__init__(self, f"{host_ip}:{port}", Distributed.peers, consumers=consumers)
        Distributed.distributed_objects.append(self)
        self.waitReady()
        while not self.isReady():
            log.debug(f"Waiting to acquire initial data for {name}")
            sleep(1)