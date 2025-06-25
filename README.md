# Network Router Configuration Management Tool

## Overview
This tool provides automated management of router configurations, focusing on BGP setup and traffic management between routers. It includes functionality for configuration backup, traffic shifting, and configuration updates using YAML templates and Jinja2.

## Features
- Router configuration backup and restoration
- Traffic shifting capabilities 
- BGP configuration management
- Pre and post-change verification
- Template-based configuration generation

## File Structure
- `dataext.py` - Main Python script containing core functionality
- `rtr_mgmt.yaml` - Router management configuration file
- `existing_router[1|2]_conf.yaml` - Current router configurations
- `new_router[1|2]_conf.yaml` - New router configurations to be applied
- `new_template.j2` - Jinja2 template for generating configurations
- `router[1|2]_bkup.conf` - Backup configuration files
- `.gitignore` - Git ignore file for version control

## Requirements
- Python 3.x
- YAML support
- Jinja2 templating engine
- Network access to managed routers

## Usage
The main script `dataext.py` provides several key functions:

1. Configuration Management:
   - Open and parse router management YAML files
   - Build new configurations from templates
   - Save and backup configurations

2. Traffic Management:
   - Shift traffic away from specific routers
   - Restore traffic patterns
   - Pre and post-change verification

3. Connection Handling:
   - Establish SSH connections to routers
   - Manage router credentials and access

## Key Functions
- `open_rtr_mgmt_yaml()`: Loads router management configuration
- `get_connection()`: Establishes router connections
- `traffic_shift_away()`: Redirects traffic from specified paths
- `build_config()`: Generates new configurations from templates
- `precheck()` and `post_check()`: Verifies configuration changes
- `restore_traffic()`: Restores original traffic patterns

## Configuration Files
- Router configurations are stored in YAML format
- Templates use Jinja2 syntax for configuration generation
- Backup configurations are maintained in .conf files

## Best Practices
1. Always verify configurations before applying changes
2. Maintain current backups of router configurations
3. Test traffic shifting in non-production environments first
4. Review generated configurations before deployment

## Contributing
Please follow standard Git practices when contributing:
1. Fork the repository
2. Create feature branches
3. Submit pull requests with detailed descriptions

## Backup and Recovery
The tool automatically maintains backup configurations in:
- `router1_bkup.conf`
- `router2_bkup.conf`

Use these files for recovery if needed.
