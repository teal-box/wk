import os, csv
import click
import sdwan
from tabulate import tabulate
import pandas as pd

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = sdwan.mySDWAN()

##@cli.command()
##@click.argument('src')
##@click.argument('dest', required=False)
##@click.pass_obj
##def clone(repo, src, dest):
##    pass

@cli.command()
@click.pass_obj
def getDevices(sdObj):
    devices = sdObj.getDevices()
    df = pd.DataFrame(devices)
    sdwan.pdPrint(devices,fields = ['site-name', 'deviceId', 'host-name', 'reachability', 'status', 'device-type', 'board-serial', 'uuid', 'device-model',"connectedVManages", 'testbed_mode'])
##    fields = ['site-name', 'deviceId', 'host-name', 'reachability', 'status', 'device-type', 'board-serial', 'uuid', 'device-model',"connectedVManages", 'testbed_mode']
##    df1 = df[fields]
##    print( tabulate(df1, headers="keys") )
##    pass
##getDeviceTemplates
##getFeatureTemplates


@cli.command()
@click.pass_obj
def getVedges(sdObj):
    devices = sdObj.getVedges()
    sdwan.pdPrint(devices, fields = ["deviceType", "chasisNumber", "serialNumber", "configOperationMode", "deviceModel","managed-by","reachability"])
    pass

@cli.command()
@click.pass_obj
def getDeviceTemplates(sdObj):
    devices = sdObj.getDeviceTemplates()
    sdwan.pdPrint(devices, fields = ['templateId', 'templateName', 'deviceType', 'resourceGroup', 'templateClass', 'configType', 'factoryDefault', 'devicesAttached'])
    pass

@cli.command()
@click.pass_obj
def getFeatureTemplates(sdObj):
    devices = sdObj.getFeatureTemplates()
    sdwan.pdPrint(devices, fields = ['templateId', 'templateName', 'templateDescription', 'templateType', 'deviceType'])
    pass

@cli.command()
@click.option("--deviceid", help="Device ID")
@click.option("--deviceip", help="Device IP")
@click.pass_obj
def detachDTemplate(sdObj,deviceid, deviceip):
    """e.g. python c7.py  detachdtemplate --deviceid C8K-928337B2-728D-822A-E11C-1DEEED262293  --deviceip 10.10.1.15"""
    sdObj.detachDTemplate(deviceid, deviceip)


@cli.command()
@click.option("--templatecsv", help="Device Template in CSV format/Only one device at the time")
@click.option("--templateid", help="Template ID to apply on the Device")
@click.pass_obj
def attachDTemplate(sdObj,templatecsv, templateid):
    """e.g. python c7.py attachdtemplate --templatecsv Site2-cEdge01.csv --templateid  e817727c-d53f-466b-af56-1a0bc659c54b """
    # templatecsv = r"C:\work\sdwan\Site2-cEdge01.csv"
    with open(templatecsv, "r") as tcsv:
        temp = csv.DictReader(tcsv)
        tdata = [row for row in temp]
        sdObj.attachDTemplate(templateid, tdata[0])


if __name__ == '__main__':
    cli()

