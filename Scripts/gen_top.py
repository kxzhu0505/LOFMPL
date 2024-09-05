import os
import argparse
from os.path import abspath, expanduser

def get_args():
    default = '(default: %(default)s)'
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", type=str, required=True, help=f"working directory")
    parser.add_argument("-module_name", type=str, required=True, help=f"module name")
    return parser.parse_args()


if __name__ == '__main__':

    args = get_args()
    dir = abspath(expanduser(args.dir))
    module_name = args.module_name

    with open(dir + '/top.inputs', 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        top_inputs = lines[0].split()
    # print(top_inputs)

    with open(dir + '/top.outputs', 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        top_outputs = lines[0].split()
    # print(top_outputs)

    top_ports = top_inputs + top_outputs

    with open(dir + '/' + module_name + '.v', 'w') as f:
        print('module ' + module_name + ' (', file=f)
        print('  ' + ', '.join(top_ports), file=f)
        print(');', file=f)
        for top_input in top_inputs:
            print('  input ' + top_input + ' ;', file=f)
            print('  wire ' + top_input + ' ;', file=f)
        for top_output in top_outputs:
            print('  output ' + top_output + ' ;', file=f)
            print('  wire ' + top_output + ' ;', file=f)
        print(file=f)

        wires = set()
        for file_name in os.listdir(dir):
            if file_name.endswith(".v") and ('network_' in file_name or 'part_' in file_name):
                part_name = file_name.rstrip('.v')

                with open(dir + '/' + part_name + '.ports', 'r') as f_part_ports:
                    lines = [line.strip() for line in f_part_ports.readlines()]
                    part_ports = lines[0].split()

                for port in part_ports:
                    if ( port not in top_ports ) and ( port not in wires ):
                        print('  wire ' + port + ' ;', file=f)
                        wires.add(port)

                print('  ' + part_name + ' ' + part_name + '_inst ( ', file=f, end='')
                print('.' + part_ports[0] + '(' + part_ports[0] + ')', file=f, end='')
                for port in part_ports[1:]:
                    print(', .' + port + '(' + port + ')', file=f, end='')
                print(' );', file=f)
                print(file=f)

        print('endmodule', file=f)