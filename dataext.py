from jinja2 import Environment, FileSystemLoader
from ciscoconfparse import CiscoConfParse 
from netmiko import ConnectHandler
import yaml
import re

def open_rtr_mgmt_yaml():
    with open('rtr_mgmt.yaml') as rtr_mgmt:
        mgmt = yaml.load(rtr_mgmt)
    return mgmt

# def render_yaml(rtr_list):
#     ENV = Environment(loader=FileSystemLoader("."))
#     template = ENV.get_template("core.j2")
#     print(template.render(rtr_list = rtr_list))

def get_connection(sship, sshid, sshpw): 
    router1 = {
        'device_type': 'cisco_ios',
        'ip': sship,
        'username': sshid,
        'password': sshpw
        }
    net_connect = ConnectHandler(**router1)  
    return net_connect

def parse_ciscoconfig(confdata):
#   parsing cisco config using ciscoconfparse library and tranform the data into YAML format.
    parse = CiscoConfParse(confdata)

# Extracting BGP AS Number
    bgp_cmds = parse.find_objects(r'^router bgp \d+$')
    bgp_asnum = bgp_cmds[0].text[len('router bgp '):]

# Extracting bgp router ID
    bgp_rtrids = bgp_cmds[0].re_search_children\
                (r'^ bgp router-id [1-2]?[0-9]?[0-9](\.[1-2]?[0-9]?[0-9]){3}$')
    bgp_rtrid = bgp_rtrids[0].text[len(' bgp router-id '):]

# Extracting Neighbor
    bgp_neis = bgp_cmds[0].re_search_children\
                (r'^ neighbor [1-2]?[0-9]?[0-9](\.[1-2]?[0-9]?[0-9]){3} remote-as \d{1,5}$')
    i = 0
    nei_dict = {}
    for nei in bgp_neis:
        i += 1
        neigh = nei.text[1:].split()
        nei_dict["neigh"+str(i)] = [neigh[1], neigh[3]]
    print('nei_dict: ', nei_dict)

# Extracting BGP Network
    bgp_nets = bgp_cmds[0].re_search_children\
                (r'^ network [1-2]?[0-9]?[0-9](\.[1-2]?[0-9]?[0-9]){3} mask [1-2]?[0-9]?[0-9](\.[1-2]?[0-9]?[0-9]){3}')
    j = 0
    net_dict = {}
    for net in bgp_nets:
        j += 1
        net = net.text[1:].split()
        net_dict["network"+str(j)] = [net[1], net[3]]
    print('net_dict: ', net_dict)

# Extracting BGP maximum-paths
    bgp_maxpaths = bgp_cmds[0].re_search_children(r'^ maximum-paths \d$')
    bgp_maxpath = bgp_maxpaths[0].text[len(' maximum-paths '):]
    print('bgp_maxpath: ', bgp_maxpath)


# def save_in_yaml(parsed_data)
#     #   saving config in a YAML file

# def precheck():
#     #   precheck function

# def traffic_shift_away():
#     #   Traffice shifts away


# def config_push():
#     #   the config push

# def post_check():
#     #   post check

# def traffic_restore():
#     #   traffic restore

def main():
# Pulling the management connection info from a YAML.
    mgmt = open_rtr_mgmt_yaml()
    print('router mgmt: {}'. format(mgmt))
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
    print("Router1 Prompt: ", net_connect1.find_prompt())
    print("Router2 Prompt: ", net_connect2.find_prompt())

# Pulling the configs
    net_connect1.send_command('terminal length 0')
    net_connect2.send_command('terminal length 0')
    output1 = net_connect1.send_command('show run')
    output2 = net_connect2.send_command('show run')
    print(output1)
    print('Saving the router1 config...')
    with open('router1_bkup.conf', 'w') as router1_bkup:
        router1_bkup.write(output1)
    print(output2)
    print('Saving the router2 config...')
    with open('router2_bkup.conf', 'w') as router2_bkup:
        router2_bkup.write(output2)

# Parsing the config
    parse_ciscoconfig("router1_bkup.conf")
    parse_ciscoconfig("router2_bkup.conf")



if __name__ == "__main__":
    main()