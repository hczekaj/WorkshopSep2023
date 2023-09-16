from cli import cli
import argparse
import csv

# Function to run the command
def run_show_process_cpu_platform_sorted():
    # Run the command
    output = cli("show processes cpu platform sorted")

    # Return the output
    return output

# Function to run the command
def run_show_process_cpu_sorted():
    # Run the command
    output = cli("show processes cpu sorted")

    # Return the output
    return output

# Function to analyze the output and display top CPU-consuming processes on platform level
def analyze_output_platform(output, sort_by, num_processes, export):
    # Split the output into lines
    lines = output.split("\n")
    
    # Find the starting index of the process table
    start_index = 0
    for i, line in enumerate(lines):
        if "   Pid    PPid    5Sec    1Min    5Min  Status        Size  Name" in line:
            start_index = i + 2
            break

    # Extract the process information
    processes = []
    for line in lines[start_index:]:
        if line.strip() != "":
            process_info = line.split()
            processes.append({
                "PID": process_info[0],
                "PPid": process_info[1],
                "5Sec": process_info[2],
                "1Min": process_info[3],
                "5Min": process_info[4],
                "Status": process_info[5],
                "Size": process_info[6],
                "Name": " ".join(process_info[7:]),
            })

    # Sort the processes by runtime
    sorted_processes = sorted(processes, key=lambda x: float(x[sort_by][:-1]), reverse=True)

    # Display the top CPU-consuming processes
    print(f"\nTop {num_processes} CPU-consuming platform processes:\n")
    for process in sorted_processes[:num_processes]:
        print(f"Utilization: {process['5Sec']} {process['1Min']} {process['5Min']}, Process: {process['Name']}")

    # Check the export flag and invoke file export function
    if export:
        save_to_csv(sorted_processes[:num_processes], "Platform processes")
        print("Append to file successfull")

# Function to analyze the output and display top CPU-consuming processes
def analyze_output_process(output, sort_by, num_processes, export):
    # Split the output into lines
    lines = output.split("\n")

    # Find the starting index of the process table
    start_index = 0
    for i, line in enumerate(lines):
        if " PID Runtime(ms)     Invoked      uSecs   5Sec   1Min   5Min TTY Process" in line:
            start_index = i + 1
            break

    # Extract the process information
    processes = []
    for line in lines[start_index:]:
        if line.strip() != "":
            process_info = line.split()
            processes.append({
                "PID": process_info[0],
                "Runtime": process_info[1],
                "Invoked": process_info[2],
                "uSecs": process_info[3],
                "5Sec": process_info[4],
                "1Min": process_info[5],
                "5Min": process_info[6],
                "Process": " ".join(process_info[8:]),
            })

    # Sort the processes by runtime
    sorted_processes = sorted(processes, key=lambda x: float(x[sort_by][:-1]), reverse=True)

    # Display the top CPU-consuming processes
    print(f"\nTop {num_processes} CPU-consuming IOSd processes:\n")
    for process in sorted_processes[:num_processes]:
        print(f"Utilization: {process['5Sec']} {process['1Min']} {process['5Min']} Process: {process['Process']}")

    # Check the export flag and invoke file export function
    if export:
        save_to_csv(sorted_processes[:num_processes], "IOSd processes")
        print("Append to file successfull")

# Arguments parser
def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", help="Interval for processes utilization sorting", choices=["5Sec","1Min","5Min"], default="1Min")
    parser.add_argument("-n", "--num_processes", help="Number of processes to be displayed", type=int, default=5)
    parser.add_argument("-e", "--export_to_file", help="Append results to the csv file", action="store_true")
    args = parser.parse_args()
    return args

# Function to save outputs to a file
def save_to_csv(processes, command):
    filename = "/bootflash/guest-share/cpu_processes.csv"
    timestamp = cli("show clock")
    title = command
    with open(filename, mode='a', newline='') as file:
        header_writer = csv.writer(file)
        header_writer.writerow("\n")
        header_writer.writerow([command])
        header_writer.writerow([timestamp])
        writer = csv.DictWriter(file, processes[0].keys(), restval='')
        writer.writeheader()
        writer.writerows(processes)
    print(f"Output saved to {filename}")

# Main program
if __name__ == "__main__":

    # Call for parameters parsing
    args = parser()

    # Run the command and get the output
    output_platform = run_show_process_cpu_platform_sorted()

    # Run the command and get the output
    output_process = run_show_process_cpu_sorted()

    # Analyze the output and display top processes
    analyze_output_platform(output_platform, args.interval, args.num_processes, args.export_to_file)
    
    # Analyze the output and display top processes
    analyze_output_process(output_process, args.interval, args.num_processes, args.export_to_file)