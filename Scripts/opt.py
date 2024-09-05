import yaml
import argparse
import subprocess
from os.path import abspath, expanduser
from funcs import create_script, get_PDA


def get_args():
    default = '(default: %(default)s)'
    parser = argparse.ArgumentParser()
    parser.add_argument("-work_dir", type=str, required=True, help=f"working directory")
    parser.add_argument("-yosys_exe", type=str, required=True, help=f"yosys executable file")
    parser.add_argument("-abc_exe", type=str, required=True, help=f"abc executable file")
    parser.add_argument("-abc_netlist_plugin", type=str, required=True, help=f"abc netlist plugin file for yosys")
    parser.add_argument("-gen_top_py", type=str, required=True, help=f"generate top module python file in lsoracle plugin")
    parser.add_argument("-rl_P_opt_py", type=str, required=True, help=f"rl_P_opt.py file")
    parser.add_argument("-outputs_dir_monitor", type=str, required=True, help=f"outputs directory with monitors")
    parser.add_argument("-outputs_dir_noop", type=str, required=True, help=f"outputs directory with noop partitions")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    work_dir = abspath(expanduser(args.work_dir))
    yosys_exe = abspath(expanduser(args.yosys_exe))
    abc_exe = abspath(expanduser(args.abc_exe))
    abc_netlist_plugin = abspath(expanduser(args.abc_netlist_plugin))
    # lsoracle_exe = abspath(expanduser(args.lsoracle_exe))
    # lsoracle_plugin = abspath(expanduser(args.lsoracle_plugin))
    gen_top_py = abspath(expanduser(args.gen_top_py))
    rl_yqian_P_opt_py = abspath(expanduser(args.rl_yqian_P_opt_py))
    outputs_dir_monitor = abspath(expanduser(args.outputs_dir_monitor))
    outputs_dir_noop = abspath(expanduser(args.outputs_dir_noop))

    with open(work_dir + '/bench_info.yaml', 'r') as f:
        bench_info = yaml.safe_load(f)

    subprocess.run(['python3', rl_yqian_P_opt_py, '-abc_exe', abc_exe, '-outputs_dir_monitor', outputs_dir_monitor, '-outputs_dir_noop', outputs_dir_noop], cwd=work_dir)
    subprocess.run(['python3', gen_top_py, '-dir', 'src', '-module_name', 'netlist'], cwd=work_dir)

    cmds = 'read_verilog src/*.v; hierarchy -top netlist; flatten; techmap; opt -purge; write_verilog -noattr netlist.v'
    subprocess.run([yosys_exe, '-Q', '-T', '-p', cmds], check=True, stdout=subprocess.DEVNULL, cwd=work_dir)
    subprocess.run(['mv src/* outputs/'], shell=True, check=True, stdout=subprocess.DEVNULL, cwd=work_dir)


    cmds = ''
    if 'include_dir' in bench_info:
        cmds += 'verilog_defaults -add -I' + abspath(expanduser(bench_info['include_dir'])) + '; '
    for file in bench_info['file(s)']:
        cmds += 'read_verilog -nolatches ' + abspath(expanduser(file)) + '; '
    cmds += 'hierarchy -check -top ' + bench_info['top'] + '; '
    cmds += 'flatten; proc; opt -purge; memory; opt -purge; fsm; opt -purge; stat; techmap; opt -purge; stat; '
    cmds += 'abc_netlist -netlist netlist.v ' + ' -script "+cec netlist.v; quit"; '
    cmds += 'opt -purge; write_verilog -noattr src/output.v; '

    subprocess.run([yosys_exe, '-Q', '-l', 'yosys.log', '-T', '-m', abc_netlist_plugin, '-p', cmds], check=True, stdout=subprocess.DEVNULL, cwd=work_dir)

    create_script(work_dir + '/' + 'scripts', bench_info, 'compile -map_effort high', 0)
    subprocess.run(['dc_shell', '-f', 'scripts/top.tcl', '-output_log_file', 'log'], check=True, stdout=subprocess.DEVNULL, cwd=work_dir)
    
    # opt1_area, opt1_delay, opt1_slack, opt1_power = get_PDA(bench_info['top'], work_dir + '/reports/')
    # create_script(work_dir + '/' + 'scripts', bench_info, 'compile -map_effort high', -opt1_slack)
<<<<<<< HEAD
    # subprocess.run(['dc_shell', '-f', 'scripts/top.tcl', '-output_log_file', 'log'], check=True, stdout=subprocess.DEVNULL, cwd=work_dir)
=======
    # subprocess.run(['dc_shell', '-f', 'scripts/top.tcl', '-output_log_file', 'log'], check=True, stdout=subprocess.DEVNULL, cwd=work_dir)
>>>>>>> d82afa379f16033b972e22152092d74d3565f675
