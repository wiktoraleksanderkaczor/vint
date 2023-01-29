from typing import Callable, List

from pydantic import AnyUrl
from pysyncobj import SyncObj, SyncObjConf, SyncObjConsumer
from pysyncobj.batteries import replicated

from config.discovery import host_ip
from config.env import env
from config.logger import log
from role.interface.distribution import DistributedInterface


class Distributed(DistributedInterface, SyncObj):
    # Peer data structure
    cluster_name = env.cluster.name
    peers: List[AnyUrl] = env.cluster.initial_peers
    distributed_objects: List["Distributed"] = []
    syncobj_conf = SyncObjConf(dynamicMembershipChange=True)

    def __init__(self, name: str, consumers: List[SyncObjConsumer]):
        if not consumers:
            consumers = []
        SyncObj.__init__(
            self, f"{host_ip}:{env.cluster.port}", Distributed.peers, consumers=consumers, conf=Distributed.syncobj_conf
        )
        Distributed.distributed_objects.append(self)
        while not self.isReady():
            log.debug(f"Waiting to acquire initial data for {name}...")
            self.waitReady()

    # Check if master node
    def is_master(self):
        return self.getStatus()["leader"] == self.selfNode

    # Only execute on master raft node (pysyncobj) decorator
    @replicated
    def only_on_master(self, func) -> Callable:
        def wrapper(*args, **kwargs):
            if self.is_master():
                return func(*args, **kwargs)
            else:
                return lambda *args, **kwargs: None

        return wrapper

    def is_synced(self) -> bool:
        status = self.getStatus()
        return status["leader_commit_idx"] == status["commit_idx"]

    def local_sync(self):
        while not self.is_synced():
            self.waitReady()
            self.doTick()

    @replicated
    def global_sync(self):
        self.local_sync()