
from cli import execute

def parse_cdp_neighbor_detail():
    output = execute("show cdp neighbor detail")
    lines = output.splitlines()
    neighbors = []
    neighbor = {}
    mgmt_ip = False
    check_flag = False
    for i in range(len(lines)):
        line = lines[i].strip()  # Remove leading/trailing whitespaces
        if line.startswith("Device ID:"):
            check_flag = True
            neighbor['device_id'] = line.split(':')[1].strip()
            device_line = lines[i+2].strip()
            if device_line.startswith("IP address"):
                device_ip = device_line.split(':')[1].strip()
                neighbor['ip_address'] = device_ip
            else:
                neighbor['ip_address'] = "Not available"
        elif line.startswith("Interface:"):
            split_line = line.split(",")
            part1 = split_line[0].strip()
            part2 = split_line[1].strip()
            neighbor['interface'] = part1.split(':')[1].strip()
            neighbor['port_id'] = part2.split(':')[1].strip()
        elif line.startswith("Management address(es):"):
            mgmt_ip == True
            if i+1 < len(lines):
                management_line = lines[i+1].strip()
                if management_line.startswith("IP address"):
                    management_ip = management_line.split(':')[1].strip()
                    neighbor['management_ip'] = management_ip
            else:
                # Neighbor does not have a management address
                neighbor['management_ip'] = "Not available"
            neighbors.append(neighbor)
            neighbor = {}
        elif mgmt_ip==False and check_flag and line.startswith("---"):
            neighbor['management_ip'] = "Not available"
            neighbors.append(neighbor)
            neighbor = {}
    return neighbors

parsed_neighbors = parse_cdp_neighbor_detail()
filtered_data = [neighbor for neighbor in parsed_neighbors if len(neighbor) > 1]

for neighbor in filtered_data:
    print("Device ID:", neighbor['device_id'])
    print("IP address:", neighbor['ip_address'])
    print("Interface:", neighbor['interface'])
    print("Port ID (outgoing port):", neighbor['port_id'])
    print("Management IP:", neighbor['management_ip'])
    print()

