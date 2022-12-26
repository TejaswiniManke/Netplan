#! /usr/bin/python3
################################################################################
# Hubcom SD-WAN software - Ninjanet.
# For more information go to https://hubcom.in
#
# Copyright (C) 2022  Hubcom Techno System LLP.
#
# This program is not free software: you cannot redistribute it and/or modify it under
# the terms of the Hubcom Techno System LLP License as published
# either version 3 of the License, or (at your option) any
# later version.
#
################################################################################

import yaml 
import sqlite3
from netaddr import IPAddress
import subprocess

NDB_database="//home//osboxes//yaml//Ndb.db"
filepath = '/etc/netplan/00-installer-config.yaml'

def NET_ADDR_CHECK(nic_name):
    with open(filepath) as f:
        LYAML_F = yaml.safe_load(f)
        for sys_interface in LYAML_F["network"]["ethernets"]:
            if sys_interface == nic_name:
                if not ('addresses' in LYAML_F["network"]["ethernets"][sys_interface]):
                    return "False"
                else:
                    TIP=LYAML_F["network"]["ethernets"][sys_interface]["addresses"]
                    return TIP

conn = sqlite3.connect(NDB_database)
curr=conn.cursor()

CHANGE_CO = 0
if conn:
    curr.execute ("SELECT IName,IType,ISubType,Col1,Col2,Col3 FROM Itab" )
    NDB_data = curr.fetchall()
    for NDB_interface in NDB_data:
        IType=NDB_interface[1]
        ISubType=NDB_interface[2]
        IName=NDB_interface[0]
        if IType == 'WAN' and ISubType == 'STATIC':            
            net_addr=IPAddress(NDB_interface[4]).netmask_bits()
            DB_net_addr=([str(NDB_interface [3])+'/'+str(net_addr)])            
            FILECHNETPLAN=NET_ADDR_CHECK(IName)
            if FILECHNETPLAN != DB_net_addr:
                CHANGE_CO = CHANGE_CO + 1
                subprocess.run(f"netplan set ethernets.{IName}.addresses={DB_net_addr}",shell=True)
        else:
            FILECHNETPLAN=NET_ADDR_CHECK(IName)
            if FILECHNETPLAN != "False":
                subprocess.run(f"netplan set ethernets.{IName}.addresses=[]",shell=True)
                subprocess.run('sed -ire "/addresses\: \[\]/d" /etc/netplan/00-installer-config.yaml',shell=True)
                CHANGE_CO = CHANGE_CO + 1

if CHANGE_CO > 0:
    subprocess.run("netplan apply",shell=True)
# else:
#     print("NO CHANGE")
# CHANGE_CO = CHANGE_CO + 1
