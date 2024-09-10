#!/bin/bash

# echo "- file(s): ["
for file in `ls *.v`
do
    echo "- file(s): [`pwd`/$file]"
    # echo "    `pwd`/$file,"
    # echo "    `pwd`/single_port_ram.v,"
    # echo "    `pwd`/dual_port_ram.v,"
    # echo "  ]"
    echo "  top: "`echo $file | tr -d '.v'`
    echo "  out_dir: /home/zli/Desktop/benchmarks/koios"
    echo
done

# echo "  ]"