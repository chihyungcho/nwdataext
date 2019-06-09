from jinja2 import Environment, FileSystemLoader
from ciscoconfparse import CiscoConfParse 
from netmiko import ConnectHandler
import yaml
import re

def open_rtr_mgmt_yaml():
    with open('rtr_mgmt.yaml') as rtr_mgmt:
        mgmt = yaml.load(rtr_mgmt)
    return mgmt

#def render_yaml(rtr_list):
#    ENV = Environment(loader=FileSystemLoader("."))
#    template = ENV.get_template("core.j2")
#    print(template.render(rtr_list = rtr_list))

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
    for obj in parse.find_objects(r'interface'):
        print ('Object: ', obj)
        print ('Config text: ', obj.text)

#def save_in_yaml(parsed_data)
    #   saving config in a YAML file

#def precheck():
    #   precheck function

#def traffic_shift_away():
    #   Traffice shifts away


#def config_push():
    #   the config push

#def post_check():
    #   post check

#def traffic_restore():
    #   traffic restore

def main():

    mgmt = open_rtr_mgmt_yaml()
    print('router mgmt: {}'. format(mgmt))
    ip1 = mgmt[0]['mgmt_ip']
    id1 = mgmt[0]['id']
    pw1 = mgmt[0]['pw']
    ip2 = mgmt[1]['mgmt_ip']
    id2 = mgmt[1]['id']
    pw2 = mgmt[1]['pw']
    print('Connecting to Router IP: {0}'.format(ip1))
    net_connect1 = get_connection(ip1, id1, pw1)
#    print('Connecting to Router IP: {0}'.format(ip2))
#    net_connect2 = get_connection(ip2, id2, pw2)
    print(net_connect1.find_prompt())
#    print(net_connect2.find_prompt())
    net_connect1.send_command('terminal length 0')
#    net_connect2.send_command('terminal length 0')
    output1 = net_connect1.send_command('show run')
#    output2 = net_connect2.send_command('show run')
    print(output1)
    print('Saving the router1 config...')
    with open('router1_bkup.conf', 'w') as router1_bkup:
        router1_bkup.write(output1)
#    print(output2)

    
if __name__ == "__main__":
    main()