import argparse
import subprocess
import yaml
import multiprocessing
from os.path import abspath, expanduser

def prepare(opt_py, bench_info, yosys_exe, abc_exe, abc_p_exe, lsoracle_exe, part_size):
    if 'comment' not in bench_info:
        subprocess.run(['mkdir', '-p', abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + '/' + 'src'])
        subprocess.run(['mkdir', '-p', abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + '/' + 'scripts'])
        subprocess.run(['mkdir', '-p', abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + '/' + 'reports'])
        subprocess.run(['mkdir', '-p', abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + '/' + 'outputs'])
       
        with open(abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + '/bench_info.yaml', 'w') as bench_info_f:
            yaml.dump(bench_info, bench_info_f, default_flow_style=None, sort_keys=False, width=2147483647)

        print('============= ' + bench_info['out_dir'] + ': ' + bench_info['top'] + ' =============', flush=True)
        cmd = 'python3 ' + opt_py + ' -work_dir ' +  abspath(expanduser(bench_info['out_dir'])) + '/' + bench_info['top'] + ' -yosys_exe ' + yosys_exe + ' -abc_exe ' + abc_exe + ' -abc_p_exe ' + abc_p_exe + ' -lsoracle_exe ' + lsoracle_exe + ' -part_size ' + str(part_size)
        subprocess.run(['bsub', '-R', 'rusage[mem=200000]', cmd])


def get_args():
    default = '(default: %(default)s)'
    parser = argparse.ArgumentParser()
    parser.add_argument("-opt_py", type=str, required=True, help=f"opt python file")
    parser.add_argument("-benchs_info_file", type=str, required=True, help=f"benchmarks infomation file, YAML format")
    parser.add_argument("-yosys_exe", type=str, required=True, help=f"yosys executable file")
    parser.add_argument("-abc_exe", type=str, required=True, help=f"abc executable file")
    parser.add_argument("-abc_p_exe", type=str, required=True, help=f"abc_p executable file")
    parser.add_argument("-lsoracle_exe", type=str, required=True, help=f"lsoracle executable file")
    parser.add_argument("-part_size", type=int, default=10000, required=False, help=f"partition size, {default}")
    parser.add_argument("-process", type=int, default=1, required=False, help=f"parallel number, {default}")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    opt_py = abspath(expanduser(args.opt_py))
    yosys_exe = abspath(expanduser(args.yosys_exe))
    abc_exe = abspath(expanduser(args.abc_exe))
    abc_p_exe = abspath(expanduser(args.abc_p_exe))
    lsoracle_exe = abspath(expanduser(args.lsoracle_exe))
    part_size = args.part_size

    with open(args.benchs_info_file, 'r') as benchs_info_f:
        benchs_info = yaml.safe_load(benchs_info_f)

    p = multiprocessing.Pool(args.process)
    for bench_info in benchs_info:
        p.apply_async(func=prepare, args=(opt_py, bench_info, yosys_exe, abc_exe, abc_p_exe, lsoracle_exe, part_size,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
    exit()
