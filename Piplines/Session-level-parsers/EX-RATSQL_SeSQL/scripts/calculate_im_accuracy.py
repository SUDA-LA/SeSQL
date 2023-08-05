import json
def calculate_im_accuracy(input_file):
    im_dict={}
    eval_result=json.load(open(input_file))["per_item"]
    for i in eval_result:
        exact=i["exact"]
        interaction_id=i["interaction_id"]
        if(interaction_id not in im_dict):
            im_dict[interaction_id]={"all":1,"right":0}
        else:
            im_dict[interaction_id]["all"]+=1
        if(exact==True):
             im_dict[interaction_id]["right"]+=1
    im_right_accont=0
    im_all_account=0
    for key in im_dict:
        item=im_dict[key]
        im_all_account+=1
        temp_all=item["all"]
        temp_right=item["right"]
        if(temp_all==temp_right):
            im_right_accont+=1
    return im_right_accont,im_all_account,im_right_accont/im_all_account

print(calculate_im_accuracy("/data3/shhuang/DuoratChar-SeSQL/logdir/duorat-sesql-bert-wwm-follow-dependency-expand-max-length/my_inference_test_best_output.eval.json"))