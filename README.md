# VPP Controller module for SRv6 Underlay & Overlay Integration

This module is the VPP Controller module which use VPP API and other modules work together to implement Overlay & Underlay integration

### Requirements

Python 3.6+

VPP Python Module (vpp-papi)


First install vpp-papi module

```bash
vppctl show version
(If version is 18.07)
git clone https://github.com/FDio/vpp
cd vpp
git checkout stable1807
cd src/vpp-api/python
python3 setup.py install
```

Then clone this repo and modify the configuration file

```bash

git clone https://github.com/ljm625/srv6-vpp-controller
python3 -m pip install -r requirements.txt
vi config.json
```


```json
{
  "config": {
    "etcd_host": "jp.debug.com",
    "etcd_port": 2379,
    "controller_host": "jp.debug.com",
    "controller_port": "6888",
    "bsid_prefix": "fc00:1:999::"
  },
  "sla": [
    {
      "decap_sid":"fc00:2::a",
      "source":"RouterA",
      "dest": "RouterB",
      "method": "latency",
      "extra": {}
    }
  ]
}
```

Modify the config file, replace the config:

- etcd_host : The ETCD database hostname

- etcd_port : The ETCD database port

- controller_host : The xr-srv6-controller module host

- controller_port : The xr-srv6-controller module port

- bsid_prefix : The bsid prefix for VPP Policy, need to end in ::

SLA Part:

SLA part is a List, contains the SLA requirements from the host.

The SLA list can be dynamically adjusted when the module is running

The list contains:

- source : Source Node, Most time the Underlay device hostname which connects to VPP

- dest : Destination Node, the Underlay device hostname for the hosts to reach

- method : The method to calculate the path, latency or te or igp

- extra : The extra parameters, like do not pass specific node or link


### Run

python3 main.py



### Other modules

https://github.com/ljm625/srv6-vpp-controller - This repo, the VPP Agent module

https://github.com/ljm625/xr-srv6-etcd - The Agent for fetching SID info

https://github.com/ljm625/xr-srv6-controller - The Agent for calculating the route

https://github.com/ljm625/ios-xr-etcd - The IOS XR version ETCD database docker