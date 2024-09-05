import argparse
import subprocess
import yaml
import multiprocessing
from os.path import abspath, expanduser
import time

def prepare(opt_py, bench_info, yosys_exe, abc_exe, abc_netlist_plugin, synopsys_dc_setup_file, gen_top_py, rl_yqian_P_opt_py, outputs_dir_monitor, outputs_dir_noop):
    if 'comment' not in bench_info:
        subprocess.run(['mkdir', '-p', abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + '/' + 'src'])
        subprocess.run(['mkdir', '-p', abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + '/' + 'scripts'])
        subprocess.run(['mkdir', '-p', abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + '/' + 'reports'])
        subprocess.run(['mkdir', '-p', abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + '/' + 'outputs'])
        subprocess.run(['cp', synopsys_dc_setup_file, abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top']])
        with open(abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + '/bench_info.yaml', 'w') as bench_info_f:
            yaml.dump(bench_info, bench_info_f, default_flow_style=None, sort_keys=False, width=2147483647)

        print('============= ' + bench_info['out_dir'] + ': ' + bench_info['top'] + ' =============', flush=True)
        cmd = 'python3 ' + opt_py + ' -work_dir ' +  abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + ' -yosys_exe ' + yosys_exe + ' -abc_exe ' + abc_exe + ' -abc_netlist_plugin ' + abc_netlist_plugin + ' -gen_top_py ' + gen_top_py + ' -rl_yqian_P_opt_py ' + rl_yqian_P_opt_py + ' -outputs_dir_monitor ' + outputs_dir_monitor + ' -outputs_dir_noop ' + outputs_dir_noop
        subprocess.run(['bsub', '-R', 'rusage[mem=200000]', cmd])
        time.sleep(1)


def get_args():
    default = '(default: %(default)s)'
    parser = argparse.ArgumentParser()
    parser.add_argument("-opt_py", type=str, required=True, help=f"opt python file")
    parser.add_argument("-benchs_info_file", type=str, required=True, help=f"benchmarks infomation file, YAML format")
    parser.add_argument("-yosys_exe", type=str, required=True, help=f"yosys executable file")
    parser.add_argument("-abc_exe", type=str, required=True, help=f"abc executable file")
    parser.add_argument("-abc_netlist_plugin", type=str, required=True, help=f"abc netlist plugin file for yosys")
    parser.add_argument("-synopsys_dc_setup_file", type=str, required=True, help=f".synopsys_dc.setup file")
    parser.add_argument("-gen_top_py", type=str, required=True, help=f"generate top module python file in lsoracle plugin")
    parser.add_argument("-process", type=int, default=1, required=False, help=f"parallel number, {default}")
    parser.add_argument("-rl_P_opt_py", type=str, required=True, help=f"rl_P_opt.py file")

    parser.add_argument("-outputs_dir_monitor", type=str, required=True, help=f"outputs directory with monitors")
    parser.add_argument("-outputs_dir_noop", type=str, required=True, help=f"outputs directory with noop partitions")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    opt_py = abspath(expanduser(args.opt_py))
    yosys_exe = abspath(expanduser(args.yosys_exe))
    abc_exe = abspath(expanduser(args.abc_exe))
    abc_netlist_plugin = abspath(expanduser(args.abc_netlist_plugin))
    synopsys_dc_setup_file = abspath(expanduser(args.synopsys_dc_setup_file))
    gen_top_py = abspath(expanduser(args.gen_top_py))
    rl_yqian_P_opt_py = abspath(expanduser(args.rl_yqian_P_opt_py))
    outputs_dir_monitor = abspath(expanduser(args.outputs_dir_monitor))
    outputs_dir_noop = abspath(expanduser(args.outputs_dir_noop))

    with open(args.benchs_info_file, 'r') as benchs_info_f:
        benchs_info = yaml.safe_load(benchs_info_f)

    p = multiprocessing.Pool(args.process)
    for bench_info in benchs_info:
        p.apply_async(func=prepare, args=(opt_py, bench_info, yosys_exe, abc_exe, abc_netlist_plugin, synopsys_dc_setup_file, gen_top_py,rl_yqian_P_opt_py,outputs_dir_monitor,outputs_dir_noop,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
    exit()
