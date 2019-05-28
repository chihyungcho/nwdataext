from jinja2 import Environment, FileSystemLoader
import yaml

def open_yaml():
    with open("int.yaml") as int_yaml:
        interface_yaml = yaml.load(int_yaml)


def render_yaml():
    ENV = Environment(loader=FileSystemLoader('.'))
    template = ENV.get_template("core.j2")
    print(template.render(interfaces=interface_yaml))

def main():
    
if __name__ == "__main__":
    main()