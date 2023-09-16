from cli import cli
import re


def check_output_drops():
    output = cli('show interfaces')
    interfaces = output.split('swapped out')[1:]

    for interface in interfaces:
        if 'Total output drops' in interface:
            name = interface.split()[0]
            output_drops = int(interface.split('Total output drops:')[1].split()[0])
            if output_drops > 0:
                print(f"\nInterface {name} has {output_drops} total output packet drops in the following queues:")
                sw_num = sw_num = re.search(r'\d+', name).group()
                queue_output = cli(f'show platform hardware fed switch {sw_num} qos queue stats interface {name}')
                queue_map_output = cli(f'show platform hardware fed switch {sw_num} qos queue label2qmap qmap-egress-data interface {name}').split('\n')
                queue_map = label2queue_map(queue_map_output)
                queue_lines = queue_output.split('\n')
                queue_ids = [str(' '+str(i)) for i in range(8)]
                non_zero_queues = {}
                index = 0
                for line in queue_lines:
                    if 'Hardware Drop Counters' in line:
                        index = queue_lines.index(line) + 5
                for line in queue_lines[index:]:
                    if line.startswith(tuple(queue_ids)):
                        queue_id = line.split()[0]
                        queue_counters = line.split()[1:]
                        for counter in queue_counters:
                            if int(counter) > 0 and queue_id in non_zero_queues:
                                non_zero_queues[queue_id].append([queue_counters.index(counter), counter])
                            elif int(counter) > 0:
                                non_zero_queues[queue_id] = [queue_counters.index(counter), counter]
                if non_zero_queues:
                    for queue, counter in non_zero_queues.items():
                        dscp = ", ".join(queue_map[int(queue)][f"{counter[0]}"])
                        print(f"\nQueue {queue} has {counter[1]} bytes drops on Threshold-{counter[0]} for packets with the following DSCP values:\n - {dscp}")
    

def label2queue_map(queue_map_output):
    dict = {
    "1":"Default",
    "9":"CS1",
    "11":"AF11",
    "13":"AF12",
    "15":"AF13",
    "17":"CS2",
    "19":"AF21",
    "21":"AF22",
    "23":"AF23",
    "25":"CS3",
    "27":"AF31",
    "29":"AF32",
    "31":"AF33",
    "33":"CS4",
    "35":"AF41",
    "37":"AF42",
    "39":"AF43",
    "41":"CS5",
    "47":"EF",
    "49":"CS6",
    "57":"CS7",
    }
    queue_map = [{},{},{},{},{},{},{}]
    cli_result = [item for row in [item.split() for item in queue_map_output[4:(len(queue_map_output)-9)]] for item in row]
    del cli_result[4-1::4]
    cli_result = [cli_result[i:i+3] for i in range(0, len(cli_result), 3)] 
    
    for element in cli_result:
        if element[2] in queue_map[int(element[1])] and element[0] in dict.keys():
            queue_map[int(element[1])][element[2]].append(dict[element[0]])
        elif element[0] in dict.keys():
            queue_map[int(element[1])][element[2]] = [dict[element[0]]]
    
    return(queue_map)


check_output_drops()

