#!/bin/bash
task=evaluation
read_model_path=./exp/task_LGESQL_SeSQL_BERT__model_lgesql_view_mmc_gp_0.15/plm_bert-base-chinese__gnn_512_x_8__head_8__share__dp_0.2__dpa_0.0__dpc_0.2__bs_16__lr_0.0001_ld_0.8__l2_0.1__wp_0.1__sd_linear__me_250__mn_5.0__bm_5__seed_100
batch_size=16
beam_size=5
device=4

python scripts/text2sql.py --task $task --testing --read_model_path $read_model_path \
    --batch_size $batch_size --beam_size $beam_size --device $device
