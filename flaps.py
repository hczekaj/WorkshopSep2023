from cli import cli, configurep
from datetime import datetime, timedelta
from collections import defaultdict
import argparse

def get_current_time():
    clock_output = cli('show clock')
    current_time = datetime.strptime(clock_output, "*%H:%M:%S.%f %Z %a %b %d %Y\n") 
    return current_time

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--span", help="Span for link flap check (default 2 min)", type=int, default=2)
    parser.add_argument("-n", "--num_of_flaps", help="Number of flaps to disable interface (default 5)", type=int, default=5)
    args = parser.parse_args()
    return args

args = parser()
log_output = cli('show logging')
interface_changes = []
current_time = get_current_time()

lines = log_output.split('\n')
for line in lines:
    if "%LINK-3-UPDOWN" in line or "%LINEPROTO-5-UPDOWN" in line:
        parts = line.split("Interface")
        if len(parts) < 2:
            continue
        interface_info = parts[1].split(",")
        if len(interface_info) < 2:
            continue
        interface = interface_info[0].strip()
        state = interface_info[1].split("changed state to")[-1].strip()
        timestamp_str = parts[0].strip().split(': %LINK-3-UPDOWN:')[0].split(': %LINEPROTO-5-UPDOWN: Line protocol on')[0]  # Extract timestamp string
        timestamp = datetime.strptime(timestamp_str, "*%b %d %H:%M:%S.%f")
        timestamp = timestamp.replace(year = current_time.year)  # Parse timestamp
        interface_changes.append({
            'interface': interface,
            'state': state,
            'timestamp': timestamp
        })

# Group interface changes by interface
interface_groups = defaultdict(list)
for change in interface_changes:
    interface_groups[change['interface']].append(change)

# Check if any interface changed status more than ten times in the last 5 minutes
five_minutes_ago = current_time - timedelta(minutes=args.span)

for interface, changes in interface_groups.items():
    changes.sort(key=lambda x: x['timestamp'])
    count = 0
    for change in changes:
        if change['timestamp'] >= five_minutes_ago:
            count += 1
        else:
            count = 1
        if count > args.num_of_flaps:
            print("Interface %s changed status more than %s times in the last %s minutes", interface, args.num_of_flaps, args.span)
            configurep(["interface %s" % (interface), "shut", "end"])
            break


