# -*- coding: UTF-8 -*-
import os
import fnmatch
import ipaddress

from vpp_papi import VPP

import logging
# logger = logging.getLogger('vpp_papi.vpp_papi')

# CLIENT_ID = "Vppclient"
# VPP_OLD_JSON_DIR = '/usr/share/vpp/api/'
# VPP_JSON_DIR = '/usr/share/vpp/api/core/'
# VPP_PLUGIN_JSON_DIR = '/usr/share/vpp/api/plugins/'
# API_FILE_SUFFIX = '*.api.json'
#
# def load_json_api_files(json_dir=VPP_JSON_DIR, suffix=API_FILE_SUFFIX):
#     jsonfiles = []
#     for root, dirnames, filenames in os.walk(json_dir):
#         for filename in fnmatch.filter(filenames, suffix):
#             jsonfiles.append(os.path.join(json_dir, filename))
#
#     if not jsonfiles:
#         print('Error: no json api files found')
#         exit(-1)
#
#     return jsonfiles
#
#
# def connect_vpp(jsonfiles):
#     vpp = VPP(jsonfiles)
#     r = vpp.connect("CLIENT_ID")
#     print("VPP api opened with code: %s" % r)
#     return vpp
#
#
# def dump_sr_policies():
#     print("Sending dump interfaces. Msg id: sw_interface_dump")
#     for policy in vpp.api.sr_policies_dump():
#         print(policy)
#         print(ipaddress.IPv6Address(policy.bsid.addr))
#         print("===================")
#
# def insert_sr_policies(bsid, sid_list, weight=1):
#     sids=[]
#     for sid in sid_list:
#         sids.append({"addr":ipaddress.IPv6Address(unicode(sid)).packed})
#     sids.extend([{"addr":ipaddress.IPv6Address(u"0::0").packed}]*(16-len(sids)))
#     vpp.api.sr_policy_add(bsid_addr=ipaddress.IPv6Address(unicode(bsid)).packed, is_encap=1, type=0, fib_table=0,
#                           sids={"num_sids":len(sid_list),"weight":weight,"sids":sids})
#
#

class VppPolicyApi(object):
    def __init__(self):
        # self.json_files=[]
        # for dir in json_dirs:
        #     self.json_files.extend(self.load_json_api_files(dir))
        self.connect_vpp()

    def load_json_api_files(self,json_dir, suffix="*.api.json"):
        jsonfiles = []
        for root, dirnames, filenames in os.walk(json_dir):
            for filename in fnmatch.filter(filenames, suffix):
                jsonfiles.append(os.path.join(json_dir, filename))

        if not jsonfiles:
            print('Error: no json api files found')
            # exit(-1)
        return jsonfiles
    def connect_vpp(self):
        self.vpp = VPP()
        r = self.vpp.connect("Vppclient")
        print("VPP api opened with code: %s" % r)

    def dump_sr_policies(self,debug=True):
        sr_bsid_list=[]
        for policy in self.vpp.api.sr_policies_dump():
            if debug:
                print(policy)
                print(ipaddress.IPv6Address(policy.bsid.addr))
                print("===================")
            sr_bsid_list.append(ipaddress.IPv6Address(policy.bsid.addr))
        return sr_bsid_list


    def insert_sr_policies(self,bsid, sid_list, weight=1):
        sids = []
        for sid in sid_list:
            sids.append({"addr": ipaddress.IPv6Address(sid).packed})
        sids.extend([{"addr": ipaddress.IPv6Address(u"0::0").packed}] * (16 - len(sids)))
        bsid_list = self.dump_sr_policies(debug=False)
        if ipaddress.IPv6Address(bsid) in bsid_list:
            self.delete_sr_policies(bsid)
            self.vpp.api.sr_policy_add(bsid_addr=ipaddress.IPv6Address(bsid).packed, is_encap=1, type=0, fib_table=0,
                                  sids={"num_sids": len(sid_list), "weight": weight, "sids": sids})
        else:
            self.vpp.api.sr_policy_add(bsid_addr=ipaddress.IPv6Address(bsid).packed, is_encap=1, type=0, fib_table=0,
                                  sids={"num_sids": len(sid_list), "weight": weight, "sids": sids})

    def delete_sr_policies(self,bsid):
        self.vpp.api.sr_policy_del(bsid_addr = {"addr": ipaddress.IPv6Address(bsid).packed})

    def add_sr_steering(self,bsid):
        pass

    def delete_sid(self,bsid):
        self.vpp.api.sr_localsid_add_del(is_del=True,localsid={"addr":ipaddress.IPv6Address(bsid).packed})


    def create_sid(self,bsid,type,interface,nexthop):
        behaviour=0
        if type=="end.dx4":
            behaviour=7
        elif type =="end.dx6":
            behaviour=6

        intf_list=self.dump_interfaces()
        intf_index=0
        for intf in intf_list:
            if interface in intf:
                intf_index=intf_list.index(intf)

        self.vpp.api.sr_localsid_add_del(is_del=False,localsid={"addr":ipaddress.IPv6Address(bsid).packed},behavior=behaviour,sw_if_index=intf_index,nh_addr4=ipaddress.IPv4Address(nexthop).packed,end_psp=0,fib_table=0)
        return True

    def dump_localsid(self):
        for sid in self.vpp.api.sr_localsids_dump():
            print(sid)

    def dump_interfaces(self):
        intf_list=[]
        # print("Sending dump interfaces. Msg id: sw_interface_dump")
        for intf in self.vpp.api.sw_interface_dump():
            # print("\tInterface, message id: sw_interface_details, interface index: %s" % intf.interface_name.decode())
            intf_list.append(intf.interface_name.decode())
        return intf_list

    def add_steering(self,bsid,prefix_addr,mask):

        # Temporary fix
        os.system("vppctl sr steer l3 {}/{} via bsid {}".format(prefix_addr,mask,bsid))
        # Currently having issues because of APIs. Might work in v19.
        # prefix_addr=ipaddress.ip_address(prefix_addr).packed
        # result =self.vpp.api.sr_steering_add_del(is_del=False,bsid_addr=ipaddress.IPv6Address(bsid).packed,prefix_addr=prefix_addr,traffic_type=4,mask_width=mask,sw_if_index=0,table_id=0)
    def dump_steering(self):

        steer_list = self.vpp.api.sr_steering_pol_dump()
        for steer in steer_list:
            print(steer)


# if __name__ == '__main__':
#
#     # IF VPP is 18.07 Version:
#     # jsons = load_json_api_files(json_dir=VPP_OLD_JSON_DIR)
#     # IF VPP is 18.07 Version:
#
#     # IF VPP is 19 Version
#     jsons = load_json_api_files()
#     jsons.extend(load_json_api_files(json_dir=VPP_PLUGIN_JSON_DIR))
#     # IF VPP is 19 Version
#
#     vpp = connect_vpp(jsons)
#
#     # Dump SR Policies
#     dump_sr_policies()
#     # vpp.api.vl_api_srv6_sid_list_t()
#
#     insert_sr_policies("fc00:100:1::200",["fc00:1:a::1","fc00:1:a::2"])
#     # sids=[{"addr":ipaddress.IPv6Address(u"fc00:3:8::100").packed}]
#     # sids.extend([{"addr":ipaddress.IPv6Address(u"0::0").packed}]*(16-len(sids)))
#     # vpp.api.sr_policy_add(bsid_addr=ipaddress.IPv6Address(u"fc00:1:8::100").packed, is_encap=1, type=0, fib_table=0,
#     #                       sids={"num_sids":1,"weight":1,"sids":sids})
#
#     exit(vpp.disconnect())

if __name__ == '__main__':
    vpp = VppPolicyApi()
    vpp.dump_sr_policies()