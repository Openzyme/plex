import json
import os
import subprocess

from tempfile import TemporaryDirectory
from typing import Dict, List, Union


def run_plex(io: Union[Dict, List[Dict]], concurrency=1, local=False, verbose=False, retry=False, plex_path="./plex"):
    if not (isinstance(io, dict) or (isinstance(io, list) and all(isinstance(i, dict) for i in io))):
        raise ValueError('io must be a dict or a list of dicts')

    io_json_path = ""
    # Use a context manager for the temporary directory
    with TemporaryDirectory() as temp_dir:

        # Generate the JSON file name in the temporary directory
        json_file_path = os.path.join(temp_dir, 'io_data.json')

        # Save the io data to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(io, json_file, indent=4)

        cwd = os.getcwd()
        plex_work_dir = os.environ.get("PLEX_WORK_DIR",os.path.dirname(os.path.dirname(cwd)))
        cmd = [plex_path, "-input-io", json_file_path, "-concurrency", str(concurrency)]

        if local:
            cmd.append("-local=true")

        if verbose:
            cmd.append("-verbose=true")

        if retry:
            cmd.append("-retry=true")

        with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, cwd=plex_work_dir) as p:
            for line in p.stdout:
                if "Initialized IO file at:" in line:
                    parts = line.split()
                    io_json_path = parts[-1]
                print(line, end='')
    return io_json_path

def print_io_graph_status(io_graph):
    state_count = {}

    # Iterate through the io_list and count the occurrences of each state
    for io in io_graph:
        state = io['state']
        if state in state_count:
            state_count[state] += 1
        else:
            state_count[state] = 1

    # Print the total number of IOs
    print(f"Total IOs: {len(io_graph)}")

    # Print the number of IOs in each state
    for state, count in state_count.items():
        print(f"IOs in {state} state: {count}")
