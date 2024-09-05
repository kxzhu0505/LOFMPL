export PYTHONPATH=/home/wllpro/llwang04/zli/logic_synthesis/orig_dc
python3 ./top.py\
-opt_py ./opt.py\
-benchs_info_file ../benchs_info/benchs_info_all.yaml\
-yosys_exe../yosys-yosys-0.32/yosys\
-abc_exe ../abc-master/abc\
-abc_netlist_plugin ../abc_netlist/abc_netlist.so\
-synopsys_dc_setup_file ../orig_dc/.synopsys_dc.setup\
-gen_top_py ./gen_top.py\
-rl_P_opt_py ./rl_P_opt.py\
-outputs_dir_monitor ./outputs\
-outputs_dir_noop ./outputs'
