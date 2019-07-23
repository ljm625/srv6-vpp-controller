# This controller is used for vpp plugin integration.

import asyncio
import json

from controller_api import ControllerApiHelper
from etcd_helper import EtcdHelper
from sid_helper import SidHelper
from vpp_api import VppPolicyApi


class MainLogic(object):
    def __init__(self,config):
        self.config_path=config
        self.config=None
        self.calculated_sla = []
        self.old_config=None

    def hash(self,sla_list):
        result=set()
        for sla in sla_list:
            result.add(json.dumps(sla))
        return result

    def reload_config(self):
        with open(self.config_path) as file:
            json_data=file.read()
            data=json.loads(json_data)
            self.config = data["config"]
            self.sla = data["sla"]
            self.sid_info = data["sid"]

    def check_config(self):
        self.reload_config()

    async def run(self):
        # Dynamically read config file
        while True:
            self.check_config()
            while not self.config:
                print("Config not present. Waiting.")
                await asyncio.sleep(1)
            if self.config != self.old_config:
                print("INFO : Reloading configs")
                self.etcd=EtcdHelper(self.config["etcd_host"],self.config["etcd_port"])
                self.controller = ControllerApiHelper(self.config["controller_host"],self.config["controller_port"])
                self.vpp = VppPolicyApi()
                self.sid_helper = SidHelper(self.etcd,self.vpp,self.sid_info)
                await self.sid_helper.update_sid_to_etcd(self.config["bsid_prefix"])

            print("INFO : Application running and updating Policies.")
            for sla in (self.hash(self.sla) - self.hash(self.calculated_sla)):
                sla_dict=json.loads(sla)
                print(sla_dict)
                await self.calculate_route(sla_dict,cache=False)
            # First check if exist in etcd.
            self.old_config=self.config
            await asyncio.sleep(10)





    async def calculate_route(self,sla, cache=True):

        # First check etcd, if not exist, then api, finally watch
        key = "{}__{}__{}__{}".format(sla["source"],sla["dest"],sla["method"],json.dumps(sla["extra"]))
        print("Calculating Route: {}".format(key))
        result = await self.etcd.get(key)
        if result and cache:
            # Start watch task
            result=json.loads(result)
        else:
            # Get result in controller
            result = await self.controller.calculate_path(sla["source"],sla["dest"],sla["method"],sla["extra"])
        await self.update_policy(sla,result)
        self.create_watch_task(self.etcd.watch(key, sla, self.update_policy))

    async def update_policy(self,sla,sid_list):
        try:
            self.calculated_sla.index(sla)
        except ValueError:
            self.calculated_sla.append(sla)
        decap_sid = await self.query_decap_sid(sla["dest_ip"],sla["vrf_name"])
        sid_list.append(decap_sid)
        print("INFO : Updating BSID: {}{}".format(self.config["bsid_prefix"],self.calculated_sla.index(sla)+1))
        self.vpp.insert_sr_policies("{}{}".format(self.config["bsid_prefix"],self.calculated_sla.index(sla)+1),sid_list)
        self.vpp.add_steering("{}{}".format(self.config["bsid_prefix"],self.calculated_sla.index(sla)+1),sla["dest_ip"].split('/')[0],int(sla["dest_ip"].split('/')[1]))

    async def query_decap_sid(self,ip_range,vrf_name):
        result =await self.etcd.get("{}_{}".format(ip_range,vrf_name))
        if not result:
            raise Exception("ERROR : Error occured in program! The defined ip range not found.")
        return json.loads(result)["sid"]

    def create_watch_task(self,coro):
        asyncio.ensure_future(coro)

if __name__ == '__main__':
    # This controller will listen to the requests and dynamically update the VPP. Most of the code are made with coroutine support.

    loop = asyncio.get_event_loop()

    # One task to execute forever

    coro = MainLogic("config.json").run()
    asyncio.ensure_future(coro)

    loop.run_forever()
