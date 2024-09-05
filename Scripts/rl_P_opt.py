import argparse
import subprocess
import yaml
from os.path import abspath, expanduser
import os
from pathlib import Path
import pandas as pd

def get_args():
    default = '(default: %(default)s)'
    parser = argparse.ArgumentParser()
    parser.add_argument("-abc_exe", type=str, required=True, help=f"abc executable file")
    parser.add_argument("-outputs_dir_monitor", type=str, required=True, help=f"outputs directory with monitors")
    parser.add_argument("-outputs_dir_noop", type=str, required=True, help=f"outputs directory with noop partitions")
    return parser.parse_args()

def get_best_seq_reward(monitor_csv_file):
    monitor_df = pd.read_csv(monitor_csv_file, comment='#')
    sorted_df = monitor_df.sort_values(by='r', ascending=False)
    return sorted_df.iloc[0][5], sorted_df.iloc[0][0]


if __name__ == '__main__':
    args = get_args()
    abc_exe = abspath(expanduser(args.abc_exe))
    outputs_dir_monitor = abspath(expanduser(args.outputs_dir_monitor))
    outputs_dir_noop = abspath(expanduser(args.outputs_dir_noop))

    with open('bench_info.yaml', 'r') as f:
        bench_info = yaml.safe_load(f)

    monitor_outputs_parent_dir = str(Path(outputs_dir_monitor).parent)
    noop_outputs_parent_dir = str(Path(outputs_dir_noop).parent)
    src_dir = os.path.join(noop_outputs_parent_dir, bench_info['out_dir'], bench_info['top'], 'src')

    for item in os.listdir(src_dir):

        if item.endswith('.v'):
            monitor_csv_file = os.path.join(monitor_outputs_parent_dir, bench_info['out_dir'], bench_info['top'], os.path.basename(item).split('.')[0], 'ppo', 'abc-exe-opt-v0_1', '0.monitor.csv')
            if os.path.isfile(monitor_csv_file): # if exists
                best_seq, reward = get_best_seq_reward(monitor_csv_file)
                print(best_seq, reward)
                cmd = 'read_verilog ' + os.path.join(src_dir, item) + '; '
                cmd += 'strash; '
                cmd += ( best_seq + '; ')
                cmd += ( 'write_verilog src/' + item )
                subprocess.run([abc_exe, '-q', cmd])
            else:
                subprocess.run(['cp', os.path.join(src_dir, item), 'src/'])

        if item.endswith('.ports'):
            subprocess.run(['cp', os.path.join(src_dir, item), 'src/'])
        
        if item in ['top.inputs', 'top.outputs']:
            subprocess.run(['cp', os.path.join(src_dir, item), 'src/'])

