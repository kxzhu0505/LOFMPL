import yaml
import argparse
import subprocess
from os.path import abspath, expanduser
import os
import re
# from funcs import create_script, get_PDA

def gen_verilog_ports(verilog_file):

    with open(verilog_file, 'r') as verilog_f:
        verilog_content = verilog_f.read()

    pattern = r'[(]([\s\S]*?)[)]'
    ports = re.search(pattern, verilog_content)[1].replace("\n", " ").replace(",", " ").split()

    with open(verilog_file.replace('.v', '.ports'), 'w') as ports_f:
        for port in ports:
            print(port, end = ' ', file=ports_f)

def rename_parts(work_dir, network_name):
    for file in os.listdir(os.path.join(work_dir, network_name)):
        if file.endswith('.v'):
            subprocess.run(['sed', '-i', '1s/'+file.replace('.v','')+'/'+network_name+'_'+file.replace('.v','')+'/', os.path.join(network_name, file)], cwd=work_dir)
            os.rename(os.path.join(work_dir, network_name, file), os.path.join(work_dir, 'src', network_name+'_'+file))
            os.rename(os.path.join(work_dir, network_name, file.replace('.v', '.ports')), os.path.join(work_dir, 'src', network_name+'_'+file.replace('.v', '.ports')))

def get_args():
    default = '(default: %(default)s)'
    parser = argparse.ArgumentParser()
    parser.add_argument("-work_dir", type=str, required=True, help=f"working directory")
    parser.add_argument("-yosys_exe", type=str, required=True, help=f"yosys executable file")
    parser.add_argument("-abc_exe", type=str, required=True, help=f"abc executable file")
    parser.add_argument("-abc_p_exe", type=str, required=True, help=f"abc_p executable file")
    parser.add_argument("-lsoracle_exe", type=str, required=True, help=f"lsoracle executable file")
    parser.add_argument("-part_size", type=int, default=10000, required=False, help=f"partition size, {default}")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    work_dir = abspath(expanduser(args.work_dir))
    yosys_exe = abspath(expanduser(args.yosys_exe))
    abc_exe = abspath(expanduser(args.abc_exe))
    abc_p_exe = abspath(expanduser(args.abc_p_exe))
    lsoracle_exe = abspath(expanduser(args.lsoracle_exe))
    part_size = args.part_size

    with open(work_dir + '/bench_info.yaml', 'r') as f:
        bench_info = yaml.safe_load(f)

    if 'comment' not in bench_info:
        cmds = ''
        if 'include_dir' in bench_info:
            cmds += 'verilog_defaults -add -I' + abspath(expanduser(bench_info['include_dir'])) + '; '
        for file in bench_info['file(s)']:
            cmds += 'read_verilog -nolatches ' + abspath(expanduser(file)) + '; '
        cmds += 'hierarchy -check -top ' + bench_info['top'] + '; '
        cmds += 'flatten; proc; opt -purge; memory; opt -purge; fsm; opt -purge; stat; techmap; opt -purge; stat; '
        cmds += 'abc -nocleanup -script "+strash; write_aiger -s abc.aig; quit";'
        subprocess.run([yosys_exe, '-Q', '-T', '-l', 'yosys.log', '-p', cmds], check=False, stdout=subprocess.DEVNULL, cwd=work_dir)

        cmds = 'read_aiger abc.aig; pif -s ' + str(part_size) + ' -d ./src; quit'
        subprocess.run([abc_p_exe, '-c', cmds], check=False, stdout=subprocess.DEVNULL, cwd=work_dir)

        src_dir = os.path.join(work_dir, 'src')
        for verilog_file in os.listdir(src_dir):
            cmds = 'read_verilog ' + os.path.join(src_dir, verilog_file) + '; strash; write_aiger -s '+ os.path.join(src_dir, verilog_file.replace('.v', '.aig')) + '; print_stats; quit'
            subp_log = subprocess.run([abc_exe, '-c', cmds], check=True, stdout=subprocess.PIPE, text=True, cwd=work_dir)
            abc_log = subp_log.stdout.replace('\x1b[1;37m', '').replace('\x1b[0m', '')
            for line in abc_log.split('\n'):
                if 'i/o' in line:
                    nodes = (re.search('and *= *(\d+) *', line))[1]
                    if int(nodes) > 1.5*part_size:
                        subprocess.run(['mkdir', '-p', os.path.join(work_dir, verilog_file.split('.')[0])])
                        cmds = 'read_aig ' + os.path.join(src_dir, verilog_file.replace('.v', '.aig')) + '; ps -a; oracle --p_strategy mffc_kahypar --size ' + str(part_size) + ' --noop_dir ' + os.path.join(work_dir, verilog_file.split('.')[0]) + '; quit'
                        lso_log = subprocess.run([lsoracle_exe, '-c', cmds], check=True, stdout=subprocess.PIPE, text=True, cwd=work_dir)

                        subprocess.run(["sed -i  's/node/" + verilog_file.split('.')[0] + "_node/g' *.v"], shell=True, stdout=subprocess.DEVNULL, cwd=os.path.join(work_dir, verilog_file.split('.')[0]))
                        for file in os.listdir(os.path.join(work_dir, verilog_file.split('.')[0])):
                            gen_verilog_ports(os.path.join(work_dir, verilog_file.split('.')[0], file))

                        with open(os.path.join(work_dir, verilog_file.split('.')[0], 'lso.log'), 'w') as f:
                            print(lso_log.stdout, file=f)
                        subprocess.run(['rm', os.path.join(src_dir, verilog_file)])
                        rename_parts(work_dir, verilog_file.split('.')[0])
                    else:
                        gen_verilog_ports(os.path.join(src_dir, verilog_file))
                    subprocess.run(['rm', os.path.join(src_dir, verilog_file.replace('.v', '.aig'))])
        
        for item in os.listdir(work_dir):
            if item.startswith('_tmp_'):
                subprocess.run(['sed -n 2p ' + os.path.join(item, 'input.blif') + " | tr -d '\n' | sed 's/.inputs //' > src/top.inputs"], shell=True, stdout=subprocess.DEVNULL, cwd=work_dir)
                subprocess.run(['sed -n 3p ' + os.path.join(item, 'input.blif') + " | tr -d '\n' | sed 's/.outputs //' > src/top.outputs"], shell=True, stdout=subprocess.DEVNULL, cwd=work_dir)