#! /usr/bin/env/python

from jinja2 import Environment, FileSystemLoader
from ciscoconfparse import CiscoConfParse
from netmiko import ConnectHandler
import yaml
import re

def open_rtr_mgmt_yaml():
    with open('rtr_mgmt.yaml') as rtr_mgmt:
        mgmt = yaml.safe_load(rtr_mgmt.read())
    return mgmt

def get_connection(sship, sshid, sshpw):
    router = {
        'device_type': 'cisco_ios',
        'ip': sship,
        'username': sshid,
        'password': sshpw
        }
    net_connect = ConnectHandler(**router)
    return net_connect

# Parsing cisco config using CiscoConfParse library.
class BGP_Extraction:
    def __init__(self, confdata):
        self.confdata = confdata
        self.parse = CiscoConfParse(confdata)
        self.bgp_cmds = self.parse.find_objects(r'^router bgp \d+$')

# Extracting BGP AS Number
    def as_num(self):
        asnum = self.bgp_cmds[0].text[len('router bgp '):]
        return asnum

# Extracting bgp router ID
    def rtr_id(self):
        rtrids = self.bgp_cmds[0].re_search_children\
                    (r'^ bgp router-id [1-2]?[0-9]?[0-9](\.[1-2]?[0-9]?[0-9]){3}$')
        rtrid = rtrids[0].text[len(' bgp router-id '):]
        return rtrid

# Extracting BGP Neighbor
    def nei(self):
        neis = self.bgp_cmds[0].re_search_children\
                    (r'^ neighbor [1-2]?[0-9]?[0-9](\.[1-2]?[0-9]?[0-9]){3} remote-as \d{1,5}$')
        i = 0
        nei_dict = []
        for nei in neis:
            neigh = nei.text[1:].split()
            nei_dict.append([neigh[1], neigh[3]])
            i += 1
        return nei_dict

# Extracting BGP Network
    def net(self):
        nets = self.bgp_cmds[0].re_search_children\
                    (r'^ network [1-2]?[0-9]?[0-9](\.[1-2]?[0-9]?[0-9]){3} mask [1-2]?[0-9]?[0-9](\.[1-2]?[0-9]?[0-9]){3}')
        j = 0
        net_dict = []
        for net in nets:
            network = net.text[1:].split()
            net_dict.append([network[1], network[3]])
            j += 1
        return net_dict

# Extracting BGP maximum-paths
    def maxpath(self):
        maxpaths = self.bgp_cmds[0].re_search_children(r'^ maximum-paths \d+$')
        maxpath = maxpaths[0].text[len(' maximum-paths '):]
        return maxpath

# saving config in a YAML file
def save_in_yaml(parsed_data, rtr_name):
    with open('existing_'+rtr_name+'_conf.yaml', 'w') as ext_yaml:
        yaml.dump(parsed_data, ext_yaml, default_flow_style=False)

# Precheck - permitted device version
def precheck(device):
    sh_ver = device.send_command('show version')
    pattern = r'Version \d{1,2}\.\d\(\d{1,2}\)\w'
    dev_ser = re.search(pattern, sh_ver)
    if dev_ser.group() == 'Version 12.4(11)T':
        return True
    else:
        print('Version mismatch')

# Traffice shifts away
def traffic_shift_away(connect, as_number, neighbor, opp_as_number):
    if (as_number != opp_as_number):
        if connect.send_config_set('do show run | se route-map as_tshift'):
            cmd1 = [('router bgp '+as_number), ('neighbor '+neighbor+' route-map as_tshift out')]
            connect.send_config_set(cmd1)
        else:
            print('no route-map as_tshift exist')
        if connect.send_config_set('do show run | se route-map lp_tshift'):
            cmd2 = [('router bgp '+as_number), ('neighbor '+neighbor+' route-map lp_tshift in')]
            connect.send_config_set(cmd2)
        else:
            print('no route-map lp_tshift exist')
    else:
        print('Skipping the IBGP neighbor: '+neighbor)

# Build config
def build_config(conf_data):
    ENV = Environment(loader = FileSystemLoader('.'))
    template = ENV.get_template('new_template.j2')
    return template.render(conf_data)

# post check
def post_check(device, router):
    show_run = device.send_command('show run')
    with open(router+'_temp.conf', 'w') as router_temp:
        router_temp.write(show_run)
    parse = CiscoConfParse(router+'_temp.conf')
    match = parse.find_objects(r'router bgp \d+$')
    routemap = match[0].re_search_children(r'^ neighbor [1-2]?[0-9]?[0-9](\.[1-2]?[0-9]?[0-9]){3} remote-as \d+$')
    return routemap

# traffic restore
def restore_traffic(connect, as_number, neighbor, opp_as_number):
    if (as_number != opp_as_number):
        cmd1 = [('router bgp '+as_number), ('no neighbor '+neighbor+' route-map as_tshift out')]
        connect.send_config_set(cmd1)
        cmd2 = [('router bgp '+as_number), ('no neighbor '+neighbor+' route-map lp_tshift in')]
        connect.send_config_set(cmd2)
    else:
        print('Skipping the IBGP neighbor.')

# Pulling the management connection info from a YAML.
def main():
    mgmt = open_rtr_mgmt_yaml()
    ip1 = mgmt[0]['mgmt_ip']
    id1 = mgmt[0]['id']
    pw1 = mgmt[0]['pw']
    ip2 = mgmt[1]['mgmt_ip']
    id2 = mgmt[1]['id']
    pw2 = mgmt[1]['pw']

# Connecting to the routers.
    print('Connecting to Router1 IP: {0}'.format(ip1))
    net_connect1 = get_connection(ip1, id1, pw1)
    print('Connecting to Router2 IP: {0}'.format(ip2))
    net_connect2 = get_connection(ip2, id2, pw2)

# Pulling the configs
    net_connect1.send_command('terminal length 0')
    net_connect2.send_command('terminal length 0')
    output1 = net_connect1.send_command('show run')
    output2 = net_connect2.send_command('show run')
    print('\nSaving the router1 config...')
    with open('router1_bkup.conf', 'w') as router1_bkup:
        router1_bkup.write(output1)
    print('Saving the router2 config...')
    with open('router2_bkup.conf', 'w') as router2_bkup:
        router2_bkup.write(output2)

# Parsing the config
    rtr1 = BGP_Extraction("router1_bkup.conf")
    rtr2 = BGP_Extraction("router2_bkup.conf")
    bgp_conf1 = {'asnum': rtr1.as_num(), 'rtrid': rtr1.rtr_id(), 'nei': rtr1.nei(), 'net': rtr1.net(), 'maxpath': rtr1.maxpath()}
    bgp_conf2 = {'asnum': rtr2.as_num(), 'rtrid': rtr2.rtr_id(), 'nei': rtr2.nei(), 'net': rtr2.net(), 'maxpath': rtr2.maxpath()}
    save_in_yaml(bgp_conf1, 'router1')
    save_in_yaml(bgp_conf2, 'router2')

# Precheck and T-Shift by changing BGP Local Pref
    if (precheck(net_connect1) & precheck(net_connect2)):
        print('\nRouter1 precheck passed.')
        print('Router2 precheck passed.')
        print('\nShifting away the traffic on Router1...')
        for i in rtr1.nei():
            print('neighbor:', i[0], 'remote-as:', i[1])
            traffic_shift_away(net_connect1, rtr1.as_num(), i[0], i[1])
        print('Shifting away the traffic on Router2...')
        for i in rtr2.nei():
            print('neighbor:', i[0], 'remote-as:', i[1])
            traffic_shift_away(net_connect2, rtr2.as_num(), i[0], i[1])
        output1 = net_connect1.send_command('clear ip bgp * soft')
        print('\nInitiating router1 BGP Soft reset...'+output1)
        output2 = net_connect2.send_command('clear ip bgp * soft')
        print('Initiating router2 BGP Soft reset...'+output2)
    else:
        print('Precheck failed.')

# Validate no traffic flow on the device


# Config changes on the devices
    with open('new_router1_conf.yaml') as new_rtr1_conf:
    rtr1_conf_data = yaml.safe_load(new_rtr1_conf.read()))
    with open('new_router2_conf.yaml') as new_rtr2_conf:
    rtr2_conf_data = yaml.safe_load(new_rtr2_conf.read()))
    print('\nConfiguring the Router1...')
    net_connect1.send_config_set(build_config(rtr1_conf_data))
    print('Configuring the Router2...')
    net_connect2.send_config_set(build_config(rtr2_conf_data))

# Post check
    if post_check(net_connect1, 'router1'):
        print('\nRouter1 Post check passed.')
    else:
        print('\nRouter1 Post check failed.')
    if post_check(net_connect2, 'router2'):
        print('Router2 Post check passed.')
    else:
        print('Router2 Post check failed.')

# Traffic Restore
    print('\nRestoring traffic on R1...')
    for i in rtr1.nei():
        print('neighbor:', i[0], 'remote-as:', i[1])
        restore_traffic(net_connect1, rtr1.as_num(), i[0], i[1])
    print('Restoring traffic on R2...')
    for i in rtr2.nei():
        print('neighbor:', i[0], 'remote-as:', i[1])
        restore_traffic(net_connect2, rtr2.as_num(), i[0], i[1])
    output1 = net_connect1.send_command('clear ip bgp * soft') # to reset specific neighbor
    print('\nInitiating router1 BGP Soft reset...'+output1)
    output2 = net_connect2.send_command('clear ip bgp * soft') # to reset specific neighbor
    print('Initiating router2 BGP Soft reset...'+output2)

if __name__ == "__main__":
    main()