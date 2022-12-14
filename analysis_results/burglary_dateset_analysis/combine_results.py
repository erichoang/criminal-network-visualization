import os
import pandas as pd

# FP_DF_OUTPUT = 'df_israel_lea_inp_burglary_offender_id_network_undirected_betweenness_centrality_scores_mean.csv'
FP_DF_OUTPUT = 'df_israel_lea_inp_burglary_offender_id_network_removed_edges_5%_mean.csv'

def get_list_results_file(results_dir):
    list_file_name = list()
    for file_name in os.listdir(results_dir):
        if file_name.startswith('df_israel_lea_inp_burglary_offender') and file_name.endswith('.csv'):
            list_file_name.append(file_name)
    return list_file_name

def merge_jaccard_results(results_dir_path):
    list_results_file = get_list_results_file(results_dir_path)

    concat_df = pd.DataFrame()
    
    for results_file in list_results_file:
        results_file_path = os.path.join(results_dir_path, results_file)
        temp_df = pd.read_csv(results_file_path, index_col=False)
        concat_df= pd.concat([concat_df, temp_df], ignore_index=True)
    
    concat_df = concat_df.loc[:, ~concat_df.columns.str.contains('^Unnamed')]
    
    aggregation_functions = {'#_central_nodes': 'first', '#_removed_edges': 'first', 
                             'acc_top_1(%)': 'mean', 'acc_top_3(%)': 'mean', 'acc_top_5(%)': 'mean'}
    grouped_df = concat_df.groupby(by=['#_central_nodes', '#_removed_edges'])

    merged_df = pd.DataFrame(columns=['#_central_nodes', '#_removed_edges',
                                      'acc_top_1(%)', 'acc_top_3(%)', 'acc_top_5(%)'])
    for key, item in grouped_df:
        group = grouped_df.get_group(key)
        # print(group)
        avg_group = group.groupby(group['#_central_nodes']).aggregate(aggregation_functions)
        merged_df = pd.concat([merged_df, avg_group])
    
    merged_df = merged_df.reset_index(drop=True)
    print(merged_df)

    merged_df.to_csv(results_dir_path + '/' + FP_DF_OUTPUT)

def merge_removed_edges_results(results_dir_path):
    list_results_file = get_list_results_file(results_dir_path)

    concat_df = pd.DataFrame()
    
    for results_file in list_results_file:
        results_file_path = os.path.join(results_dir_path, results_file)
        temp_df = pd.read_csv(results_file_path, index_col=False)
        concat_df= pd.concat([concat_df, temp_df], ignore_index=True)
    
    concat_df = concat_df.loc[:, ~concat_df.columns.str.contains('^Unnamed')]
    
    aggregation_functions = {'#_removed_edges': 'first', 
                             'acc_top_1(%)': 'mean', 'acc_top_3(%)': 'mean', 'acc_top_5(%)': 'mean'}
    grouped_df = concat_df.groupby(by=['#_removed_edges'])


    merged_df = pd.DataFrame(columns=['#_removed_edges',
                                      'acc_top_1(%)', 'acc_top_3(%)', 'acc_top_5(%)'])
    for key, item in grouped_df:
        group = grouped_df.get_group(key)
        # print(group)
        avg_group = group.groupby(group['#_removed_edges']).aggregate(aggregation_functions)
        merged_df = pd.concat([merged_df, avg_group])
    
    merged_df = merged_df.reset_index(drop=True)
    print(merged_df)

    merged_df.to_csv(results_dir_path + '/' + FP_DF_OUTPUT)


if __name__ == "__main__":
    # results_dir_path = 'analyzer/examples/jaccard'
    # merge_jaccard_results(results_dir_path)

    results_dir_path = 'analyzer/examples/removed_edges_5%_new'
    merge_removed_edges_results(results_dir_path)
    
