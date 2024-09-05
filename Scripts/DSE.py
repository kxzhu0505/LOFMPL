import argparse
import subprocess
import yaml
from os.path import abspath, expanduser
import shutil
from pathlib import Path
import os
import math
import time

def get_args():
    default = '(default: %(default)s)'
    parser = argparse.ArgumentParser()
    parser.add_argument("-benchs_info_file", type=str, required=True, help=f"benchmarks infomation file, YAML format")
    parser.add_argument("-rl_logic_synthesis_dir", type=str, required=True, help=f"rl_logic_synthesis directory")
    parser.add_argument("-outputs_dir_all_parts", type=str, required=True, help=f"outputs directory conatinging all partitions")
    parser.add_argument("-abc_exe", type=str, required=True, help=f"abc executable file")
    parser.add_argument("-process", type=int, default=1, required=False, help=f"parallel number, {default}")
    parser.add_argument("-rl_run_time", type=int, default=120, required=False, help=f"rl run time in minutes, {default}")
    parser.add_argument("-rl_run_memory", type=int, default=10000, required=False, help=f"rl run memory in MB, {default}")
    return parser.parse_args()

def get_design_dir(outputs_dir_all_parts, bench_info):
    outputs_parent_dir = str(Path(outputs_dir_all_parts).parent)
    design_dir = os.path.join(outputs_parent_dir, bench_info['out_dir'], bench_info['top'])
    return design_dir

if __name__ == '__main__':

    args = get_args()
    with open(args.benchs_info_file, 'r') as benchs_info_f:
        benchs_info = yaml.safe_load(benchs_info_f)
    rl_logic_synthesis_dir = abspath(expanduser(args.rl_logic_synthesis_dir))
    outputs_dir_all_parts = abspath(expanduser(args.outputs_dir_all_parts))
    abc_exe = abspath(expanduser(args.abc_exe))
    process = args.process
    rl_run_time = args.rl_run_time
    rl_run_memory = args.rl_run_memory

    for bench_info in benchs_info:
        if 'comment' not in bench_info:
            work_dir = abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top']
            subprocess.run(['mkdir', '-p', work_dir])
            
            design_dir = get_design_dir(outputs_dir_all_parts, bench_info)
            for file in os.listdir(design_dir + '/src'):
                if file.endswith('.v') and file != 'top.v' and ( 'part_additional' not in file ):
                    print(design_dir + ' ' + file)
                    params_dict = {}
                    params_dict['abc_exe'] = abc_exe
                    params_dict['init_bench'] = os.path.join(design_dir, 'src', file)
                    params_dict['step_bench'] = os.path.join(work_dir, file)
                    params_dict['actions'] = ['rewrite', 'rewrite -z', 'rewrite -l', 'rewrite -z -l', 'refactor', 'refactor -z', 'refactor -l', 'refactor -z -l', 'resub', 'resub -z', 'resub -l', 'resub -z -l', 'balance', 'fraig', '&get -n; &dsdb; &put', 'dc2']
                    params_dict['optimize'] = 'mix'
                    params_dict['baseline'] = 'balance; rewrite; refactor; balance; rewrite; rewrite -z; balance; refactor -z; rewrite -z; balance'
                    params_dict['max_seq_len'] = 20
                    params_dict['seq_end'] = 'Not_Time'
                    
                    with open(work_dir + '/' + file.replace('.v', '') + '.yml', 'w') as f:
                        yaml.dump(params_dict, f, default_flow_style=None, sort_keys=False, width=2147483647)
                    
                    print('== run_time: ', rl_run_time)
                    print('== run_memory: ', rl_run_memory / 1000, 'GB')

                    cmd = 'PYTHONPATH=' + rl_logic_synthesis_dir + ' python ' + rl_logic_synthesis_dir + '/rl-baselines3-zoo/train.py --env abc-exe-opt-v0 --gym-packages gym_eda --algo ppo --log-folder ' + work_dir + '/' + file.replace('.v', '') + ' --env-kwargs \'options_yaml_file:"' + work_dir + '/' + file.replace('.v', '') + '.yml"\''

                    while True:
                        num_jobs = len( subprocess.check_output(['bjobs']).splitlines() ) - 1
                        print('== process : ', process)
                        print('== run jobs: ', num_jobs)
                        if num_jobs < process:
                            subprocess.run(['bsub', '-o', work_dir + '/' + file.replace('.v', '') + '.log', '-W',  str(rl_run_time), '-R', 'rusage[mem=' + str(rl_run_memory) + ']', cmd], stdout=subprocess.DEVNULL, cwd=rl_logic_synthesis_dir)
                            time.sleep(8)
                            break
                        else:
                            print('Waiting ....... ')
                            time.sleep(1)