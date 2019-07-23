import json


class SidHelper(object):
    def __init__(self,etcd,vpp,sids):
        self.etcd=etcd
        self.sids=sids
        self.vpp=vpp
        pass

    async def update_sid_to_etcd(self,prefix):
        index=1
        for sid_info in self.sids:
            bsid = "{}{}".format(prefix,str(index)+'a')
            result = self.vpp.create_sid(bsid,sid_info["action"],sid_info["interface"],sid_info["gateway"])
            if result:
                data = {
                    "sid":bsid,
                    "action":sid_info["action"],
                    "interface": sid_info["interface"],
                    "gateway": sid_info["gateway"]
                }
                await self.etcd.put("{}_{}".format(sid_info["ip_range"],sid_info["vrf_name"]),json.dumps(data))
            else:
                print("ERROR : {} could not create".format(bsid))
            index=index+1

