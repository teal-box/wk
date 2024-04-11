#-------------------------------------------------------------------------------
# Author:      ashok.chauhan
#-------------------------------------------------------------------------------

################## Import Session of Lib & Modules. ############
import click
import requests
import json, csv, time
import pandas as pd
from tabulate import tabulate
import requests, json, re
import requests.packages
from typing import List, Dict
from pprint import pprint
# from casUtils import *

# noinspection PyUnresolvedReferences
requests.packages.urllib3.disable_warnings()

################## Global Paramenters ############


def rprint(item, *keys):
    print([item[key] if key in item.keys() else None for key in keys])

def isJson(jString):
    # if jstring bytes convert to str
    if isinstance(jString, (bytes,)):
        jString = str(jString, encoding='utf-8')
        # other method byte_string.decode("utf-8")
    if not isinstance(jString, (str,)):
        return False
    try:
        json.loads(jString)
        return True
    except ValueError:
        return False
##    except JSONDecodeError:
##        return False

def pdPrint(devices, fields="all"):
    df = pd.DataFrame(devices)
    if fields == "all":
        # fields = ["deviceType", "chasisNumber", "serialNumber", "configOperationMode", "deviceModel","managed-by","reachability"]
        fields = devices[0].keys()
    df1 = df[fields]
    print( tabulate(df1, headers="keys") )



############### Base Class for CISCO-SDWAN Viptela ###########
class mySDWAN:
    # create for the ops of NSX4 tasks
    # required requests

    def __init__(self, vManage="10.10.20.90", username = "admin", passcode="C1sco12345", gs="GoldenConfigMcD.xlsx"):
        self.devices = {}
        self.s = requests.Session()
        self.s.verify = False
        self.headers = {
          "Accept-Encoding": "gzip",
          "Content-Type": "application/x-www-form-urlencoded",
          "Accept": "application/json",
        }
        self.baseUrl = f"https://{vManage}/dataservice"
        payload = {
            "j_username" : username,
            "j_password" : passcode
            }
        loginAPI = f"https://{vManage}/j_security_check"
        res = self.s.post(loginAPI, headers = self.headers ,data=payload)
        if res.content != b'':
            print ("Authentication fail Please check username/password!")
            exit()

        cookies = res.headers["Set-Cookie"]
        jsessionid = cookies.split(";")
        # split to list
        token1=jsessionid[0]
##        print ('token1=',token1)
        ####### Token - 2
        self.headers = {'Content-Type': "application/json",'Cookie': token1}

        token_url=f"{self.baseUrl}/client/token"
        res = self.s.get(url=token_url, headers=self.headers)
        token2=res.text
##        print("Content: ", res.content)
##        print("Text: ", res.text)
##        if isJson(res.content):
##            print("Json: ", res.json())
##        else:
##            print("Not Json: ", res.content)
        self.headers.setdefault("X-XSRF-TOKEN", res.content)
##        wb = fast_openpyxl(gs)
##        self.gs = wb[1]

################## API method for Heavy lifting of API Calls ############
    def __do(self, method="GET", api="", payload={}):
        url = f"{self.baseUrl}{api}"
        if method == "GET":
          response = self.s.get(url, headers = self.headers)
          if response.status_code >= 200 and response.status_code <= 299:
            if isJson(response.content):
                return response.json()
            else:
                return response.content
          else:
            print("API Call: ", url)
            print("Not able to GET api, please check for API Token/credentials!!")
            return None
        if method == "POST":
          response = self.s.post(url, headers = self.headers, data=payload)
          print(response.content)
          if response.status_code >= 200 and response.status_code <= 299:
            if isJson(response.content):
                return response.json()
            else:
                return response.content
          else:
            print("API Call: ", url)
            print("Not able to GET api, please check for API Token/credentials!!")
            return None

    def getDevices(self):
##        dict_keys(['deviceId', 'system-ip', 'host-name', 'reachability', 'status', 'personality', 'device-type', 'timezone',
##        'device-groups', 'lastupdated', 'bfdSessionsUp', 'domain-id', 'board-serial', 'certificate-validity', 'max-controllers',
##        'uuid', 'bfdSessions', 'controlConnections', 'device-model', 'version', 'connectedVManages', 'site-id', 'ompPeers',
##        'latitude', 'longitude', 'isDeviceGeoData', 'platform', 'uptime-date', 'statusOrder', 'validity', 'state', 'state_description',
##        'model_sku', 'local-system-ip', 'total_cpu_count', 'linux_cpu_count', 'testbed_mode', 'layoutLevel', 'site-name'])
        api = f"/device"
        res = self.__do(method="GET", api=api, payload={})
        if "data" in res:
            return res['data']
        else:
            res


    def getDeviceTemplates(self):
##        dict_keys(['deviceType', 'lastUpdatedBy', 'resourceGroup', 'templateClass', 'configType', 'templateId', 'factoryDefault',
##        'templateName', 'devicesAttached', 'templateDescription', 'draftMode', 'lastUpdatedOn', 'templateAttached'])
        api = f"/template/device"
        res = self.__do(method="GET", api=api, payload={})
        if "data" in res:
            return res['data']
        else:
            res

    def getFeatureTemplates(self):
##         dict_keys(['templateId', 'templateName', 'templateDescription', 'templateType', 'deviceType', 'lastUpdatedBy',
##        'lastUpdatedOn', 'factoryDefault', 'devicesAttached', 'attachedMastersCount', 'templateMinVersion', 'configType',
##        'createdBy', 'createdOn', 'resourceGroup', 'templateDefinition'])
        api = f"/template/feature"
        res = self.__do(method="GET", api=api, payload={})
        if "data" in res:
            return res['data']
        else:
            res

    def getEncryptedString(self, string):
        payload = json.dumps({
            "inputString": string
            })
        api = f"/template/security/encryptText/encrypt"
        res = self.__do(method="POST", api=api, payload=payload)
        return res

    def getDeviceInventory(self):
        d = self.getDevices()
        for item in d:
            self.devices.setdefault(item["uuid"], item)

    def getVedges(self):
        # https://x.x.x.x/dataservice/system/device/vedges
        api = f"/system/device/vedges"
        res = self.__do(method="GET", api=api, payload={})
        if "data" in res:
            return res['data']
        else:
            res

    def attachDTemplate(self, templateId, deviceCSV):
        api = r"/template/device/config/attachment"
        payload = json.dumps({
          "deviceTemplateList": [
            {
              "templateId": f"{templateId}",
              "device": [
                deviceCSV,
              ],
              "isEdited": False,
              "isMasterEdited": False,
              "isDraftDisabled": False
            }
          ]
        })
        # print(payload)

##        payload = json.dumps(
##                    {
##                      "deviceTemplateList": [
##                        {
##                          "templateId": "e817727c-d53f-466b-af56-1a0bc659c54b",
##                          "device": [
##                            {"csv-deviceId": "C8K-928337B2-728D-822A-E11C-1DEEED262293", "csv-deviceIP": "10.10.1.15", "csv-host-name": "Site2-cEdge01", "/1/vpn-instance/ip/route/vpn_1_ip_route/prefix": "TEMPLATE_IGNORE", "/1/vpn-instance/ip/route/vpn_1_ip_route/next-hop/vpn_1_next_hop_ip_address/address": "TEMPLATE_IGNORE", "/1/vpn_1_if_name/interface/if-name": "GigabitEthernet3", "/1/vpn_1_if_name/interface/description": "port.site2-sw01", "/1/vpn_1_if_name/interface/ip/address": "10.10.22.22/24", "/512/vpn-instance/ip/route/0.0.0.0/0/next-hop/vpn_512_next_hop_ip_address/address": "10.10.20.254", "/512/vpn_512_if_name/interface/if-name": "GigabitEthernet1", "/512/vpn_512_if_name/interface/description": "port.sbx-mgmt", "/512/vpn_512_if_name/interface/ip/address": "10.10.20.175/24", "/0/vpn-instance/ip/route/0.0.0.0/0/next-hop/vpn_0_mpls_next_hop_ip_add/address": "10.10.23.13", "/0/vpn-instance/ip/route/0.0.0.0/0/next-hop/vpn_0_internet_next_hop_ip_add/address": "10.10.23.45", "/0/vpn_0_internet_int_name/interface/if-name": "GigabitEthernet4", "/0/vpn_0_internet_int_name/interface/description": "internet-link", "/0/vpn_0_internet_int_name/interface/ip/address": "10.10.23.46/30", "/0/vpn_0_mpls_int_name/interface/if-name": "GigabitEthernet2", "/0/vpn_0_mpls_int_name/interface/description": "mpls-link", "/0/vpn_0_mpls_int_name/interface/ip/address": "10.10.23.14/30", "//system/host-name": "Site2-cEdge01", "//system/system-ip": "10.10.1.15", "//system/site-id": "1002"}
##                          ],
##                          "isEdited": "false",
##                          "isMasterEdited": "false",
##                          "isDraftDisabled": "false"
##                        }
##                      ]
##                    }
##
##        )

        res = self.__do(method="POST", api=api, payload=payload)
##        res = json.dumps(res.decode("utf-8"))
##        if 'id' in res:
##            print(f"Publishing template {templateId} on Device {deviceCSV['csv-deviceId']}")
##        else:
##            print(f"Error in Attaching template {templateId} on Device {deviceCSV['csv-deviceId']} ...")

    def detachDTemplate(self,deviceId, deviceIP):
        api = r"/template/config/device/mode/cli"
        payload = json.dumps(
            {
              "deviceType":"vedge",
              "devices":[
                {
                "deviceId": f"{deviceId}",
                "deviceIP": f"{deviceIP}"
                }
              ]
            }
        )
        res = self.__do(method="POST", api=api, payload=payload)
##        res = json.dumps(res.decode("utf-8"))
##        if 'id' in res:
##            print(f"Detaching template from Device {deviceid} ...")
##        else:
##            print(f"Error in Detaching template from Device {deviceid} ...")


##def main():
##    a = mySDWAN()
##    devices = a.getDevices()
##    for device in devices:
##        print(device["deviceId"],device["host-name"], device["personality"], device["personality"], device["personality"], device["connectedVManages"],device['device-type'], device['site-name'], device['site-id'],device['uuid'])
##
##    ft = a.getFeatureTemplates()
##    # print(ft)
##    a.getEncryptedString("Hello123")
##    templateCSV = r"C:\work\sdwan\Site2-cEdge01.csv"
##
##    with open(templateCSV, "r") as tcsv:
##        temp = csv.DictReader(tcsv)
##        tdata = [row for row in temp]
##
##    a.attachDTemplate("e817727c-d53f-466b-af56-1a0bc659c54b", tdata[0])
####    a.detachDTemplate("C8K-928337B2-728D-822A-E11C-1DEEED262293","10.10.1.15")
##    time.sleep(20)
##    pass
##
##if __name__ == "__main__":
##    main()
