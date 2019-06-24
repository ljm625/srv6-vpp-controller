import json

import aiohttp




class ControllerApiHelper(object):
    def __init__(self,hostname,port):
        self.hostname=hostname
        self.port=port
        pass

    async def get(self,path):
        def build_url():
            return "http://{}:{}/api/v1/{}".format(self.hostname,self.port,path)

        async with aiohttp.ClientSession() as session:
            async with session.get(build_url()) as resp:
                if resp.status>=300:
                    raise Exception("Error")
                else:
                    result = await resp.json()
                    return result

    async def post(self,path,data):
        def build_url():
            return "http://{}:{}/api/v1/{}".format(self.hostname,self.port,path)

        async with aiohttp.ClientSession() as session:
            async with session.post(build_url(), json=data) as resp:
                if resp.status>=300:
                    raise Exception("Error")
                else:
                    result = await resp.text()
                    return json.loads(result)["sid_list"]



    async def get_device_list(self):
        device_list = await self.get("devices")
        return device_list

    async def calculate_path(self,source,dest,method,extra={}):
        payload ={
            "source":source,
            "dest":dest,
            "method":method,
            "extra":extra
        }
        result = await self.post("calculate",payload)
        return result

