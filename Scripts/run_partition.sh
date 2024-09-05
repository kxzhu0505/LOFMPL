python3 ./partition.py \
-opt_py ./opt_partition.py \
-benchs_info_file ../benchs_info/benchs_info_all.yaml \
-yosys_exe ../yosys-yosys-0.32/yosys \
-abc_exe ../abc-master/abc \
-abc_p_exe ../abc_p/abc \
-lsoracle_exe ../LSOracle/build/core/lsoracle \
-part_size 10000
