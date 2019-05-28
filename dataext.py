from jinja2 import Environment, FileSystemLoader
import yaml

def open_yaml():
    with open("int.yaml") as int_yaml:
        interface_list = yaml.load(int_yaml)
        
    print("interface list: {}".format(interface_list))
    return interface_list

def render_yaml(interface_list):
    ENV = Environment(loader=FileSystemLoader("."))
    template = ENV.get_template("core.j2")
    print(template.render(interface_list = interface_list))

def main():
    render_yaml(open_yaml())
    
if __name__ == "__main__":
    main()