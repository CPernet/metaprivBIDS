import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from itertools import combinations
import math
from piflib.pif_calculator import compute_cigs



from rpy2 import robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri


# Activate pandas <-> R DataFrame conversion
pandas2ri.activate()

# Import the sdcMicro package
sdcMicro = importr('sdcMicro')


class metaprivBIDS_core_logic:
    def __init__(self):
        self.original_columns = {}
        self.combined_values_history = {}

    def load_data(self, file_path):
        sep = '\t' if file_path.lower().endswith('.tsv') else ','
        data = pd.read_csv(file_path, sep=sep)
        data.columns = data.columns.str.strip()
        column_unique_counts = {col: data[col].nunique() for col in data.columns}
        column_types = [(col, count, "Continuous" if count > 45 else "Categorical") for col, count in column_unique_counts.items()]
        return {"data": data, "original_data": data.copy(), "column_unique_counts": column_unique_counts, "column_types": column_types}




    def find_lowest_unique_columns(self, data, selected_columns):
        results = {}
        for column in selected_columns:
            subset_data = data[selected_columns]
            value_counts = subset_data.value_counts()
            unique_rows = value_counts[value_counts == 1].index
            all_unique_count = len(unique_rows)
            temp_columns = [col for col in selected_columns if col != column]
            if temp_columns:
                subset_data_after_removal = data[temp_columns]
                value_counts_after_removal = subset_data_after_removal.value_counts()
                unique_rows_after_removal = value_counts_after_removal[value_counts_after_removal == 1].index
                unique_count_after_removal = len(unique_rows_after_removal)
                difference = all_unique_count - unique_count_after_removal
                unique_values_count = subset_data[column].nunique()
                normalized_difference = round(difference / unique_values_count, 1)
                results[column] = {
                    'unique_count_after_removal': unique_count_after_removal,
                    'difference': difference,
                    'normalized_difference': normalized_difference
                }
        return results




    def calculate_k_anonymity(self, data, selected_columns):
        grouped = data.groupby(selected_columns).size().reset_index(name='counts')
        return grouped['counts'].min()



    def calculate_l_diversity(self, data, selected_columns, sensitive_attr):
        grouped = data.groupby(selected_columns)
        return grouped[sensitive_attr].nunique().min()



    def calculate_unique_rows(self, data, selected_columns, sensitive_attr=None):
        value_counts = data[selected_columns].value_counts()
        num_unique_rows = len(value_counts[value_counts == 1])
        total_rows = len(data)
        total_columns = len(data.columns)
        num_selected_columns = len(selected_columns)
        k_anonymity = self.calculate_k_anonymity(data, selected_columns)
        l_diversity = self.calculate_l_diversity(data, selected_columns, sensitive_attr) if sensitive_attr else None
        return {
            "total_rows": total_rows,
            "total_columns": total_columns,
            "num_selected_columns": num_selected_columns,
            "num_unique_rows": num_unique_rows,
            "k_anonymity": k_anonymity,
            "l_diversity": l_diversity
        }



    def compute_combined_column_contribution(self, data, selected_columns, min_size=3, max_size=7):
        if data is None:
            raise ValueError("No data loaded. Please load a dataset first.")
        if not selected_columns:
            raise ValueError("Please select at least one column.")
        
        results = []
        total_unique_rows = None

        for r in range(min_size, max_size + 1):
            all_combinations = combinations(selected_columns, r)
            for comb in all_combinations:
                selected_cols = list(comb)
                value_counts = data[selected_cols].value_counts()
                num_unique_rows = len(value_counts[value_counts == 1])

                remaining_columns = [col for col in selected_columns if col not in selected_cols]
                if remaining_columns:
                    value_counts_excluded = data[remaining_columns].value_counts()
                    num_excluded_unique_rows = len(value_counts_excluded[value_counts_excluded == 1])
                else:
                    num_excluded_unique_rows = 0

                results.append({
                    'Combination': ', '.join(selected_cols),
                    'Unique Rows': num_unique_rows,
                    'Unique Rows Excluding Columns': num_excluded_unique_rows
                })

        all_combinations_df = pd.DataFrame(results)

        if total_unique_rows is None:
            total_value_counts = data[selected_columns].value_counts()
            total_unique_rows = len(total_value_counts[total_value_counts == 1])

        all_combinations_df['Score'] = (total_unique_rows - all_combinations_df['Unique Rows Excluding Columns']) / all_combinations_df['Unique Rows']

        return all_combinations_df



    def round_values(self, data, column_name, precision):

        try:
            factor = 10 ** precision 
            
            if column_name in data.columns:
               
                self.original_columns.setdefault(column_name, data[column_name].copy())
                
              
                data[column_name] = data[column_name].apply(lambda x: math.ceil(x / factor) * factor)
                
                return data  
            else:
                raise ValueError(f"Column {column_name} not found in data.")
        except Exception as e:
            raise ValueError(f"An error occurred while rounding: {e}")




    def revert_to_original(self, data, column_name):
        if column_name in self.original_columns:
            data[column_name] = self.original_columns[column_name]
            return data
        else:
            raise ValueError(f"No original data available for column {column_name}.")





    def show_preview(self, data):
        return data.head(10)





    def add_noise(self, data, column_name, noise_type):
        if column_name not in data.columns:
            raise ValueError(f"Column {column_name} not found in the data.")
        if column_name not in self.original_columns:
            self.original_columns[column_name] = data[column_name].copy()
        noise = np.random.laplace(loc=0.0, scale=1.0, size=len(data[column_name])) if noise_type == 'laplacian' else np.random.normal(loc=0.0, scale=1.0, size=len(data[column_name]))
        data[column_name] += noise
        return data





    def combine_values(self, data, column_name):
        if column_name not in data.columns:
            raise ValueError(f"Column {column_name} not found in the data.")
        print(f"Unique values in '{column_name}': {data[column_name].unique()}")
        values_to_combine = input(f"Enter values to combine in '{column_name}' (comma-separated): ").split(",")
        values_to_combine = [v.strip() for v in values_to_combine]
        replacement_value = input("Enter the replacement value: ").strip()
        if column_name not in self.combined_values_history:
            self.combined_values_history[column_name] = []
        self.combined_values_history[column_name].append((values_to_combine, replacement_value))
        data[column_name] = data[column_name].replace(values_to_combine, replacement_value)
        print(f"Replaced {values_to_combine} with '{replacement_value}' in '{column_name}'.")
        return self.combined_values_history





    def plot_tree_graph(self, data, column_name):
        G = nx.DiGraph()
        G.add_node(column_name)
        nodes_to_add = set()
        edges_to_add = set()
        if column_name in self.combined_values_history:
            for combined_values, replacement_value in self.combined_values_history[column_name]:
                nodes_to_add.add(replacement_value)
                edges_to_add.add((column_name, replacement_value))
                for value in combined_values:
                    nodes_to_add.add(value)
                    edges_to_add.add((replacement_value, value))
        unique_values = data[column_name].unique()
        for value in unique_values:
            if pd.notna(value):
                nodes_to_add.add(value)
                edges_to_add.add((column_name, value))
        G.add_nodes_from(nodes_to_add)
        G.add_edges_from(edges_to_add)
        pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_size=1000, node_color='white', font_size=6, font_weight='normal', edge_color='black')
        plt.title(f'Tree Graph of Values in Column "{column_name}"')
        plt.show()






    def compute_cig(self, data, selected_columns):
        import piflib.pif_calculator as pif
        df = data[selected_columns]
        if df.empty:
            raise ValueError("Data not available.")

        mask_value = input('Enter a mask value (or leave blank to skip):')
        if mask_value != '':
            try:
                mask_value = float(mask_value)
                mask = df == mask_value
            except ValueError:
                raise ValueError("Invalid mask value. Please enter a number.")
            cigs = pif.compute_cigs(df)
            cigs_df = pd.DataFrame(cigs)
            cigs_df[mask] = 0
        else:
            cigs = pif.compute_cigs(df)
            cigs_df = pd.DataFrame(cigs)

        cigs_df['RIG'] = cigs_df.sum(axis=1)
        cigs_df_sorted = cigs_df.sort_values(by='RIG', ascending=False)

        percentile = int(input('Enter percentile (0-100): '))
        if percentile < 0 or percentile > 100:
            raise ValueError("Percentile must be between 0 and 100.")

        pif_value = np.percentile(cigs_df_sorted['RIG'], percentile)
        return pif_value, cigs_df_sorted

    def describe_cig(self, cigs_df):
        if not cigs_df.empty:
            if 'RIG' in cigs_df.columns:
                cigs_df_for_description = cigs_df.drop(columns=['RIG'])
            else:
                cigs_df_for_description = cigs_df

            description = cigs_df_for_description.describe()
            return description.applymap(lambda x: f"{x:.2f}")
        else:
            raise ValueError("Please compute CIG before describing it.")






    def generate_heatmap(self, cigs_df):
        if not cigs_df.empty:
            if 'RIG' in cigs_df.columns:
                cigs_df_no_rig = cigs_df.drop(columns=['RIG'])
            else:
                cigs_df_no_rig = cigs_df

            color_map = mcolors.ListedColormap(sns.color_palette("RdYlGn", 256).as_hex()[::-1])

            plt.figure(figsize=(10, 8))
            sns.heatmap(cigs_df_no_rig, cmap=color_map, annot=False, fmt="g", cbar=True)
            plt.title("CIG Heatmap")
            plt.xticks(fontsize=10)  
            plt.yticks(rotation=90, fontsize=10)
            plt.show()
        else:
            raise ValueError("Please compute CIG before generating the heatmap.")


    def convert_to_numeric(df):
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype('category').cat.codes
        return df




    
def compute_suda2(self, data, selected_columns, sample_fraction=0.2, missing_value=-999):

    if not selected_columns:
        raise ValueError("No columns selected for SUDA2 computation.")

    df = data[selected_columns].copy()
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype('category').cat.codes

    r_df = robjects.DataFrame({name: robjects.FloatVector(df[name].astype(float)) for name in df.columns})
    suda_result = sdcMicro.suda2(r_df, missing=missing_value, DisFraction=sample_fraction)

    dis_score = [round(x, 4) for x in list(suda_result.rx2('disScore'))]
    score = list(suda_result.rx2('score'))
    attribute_contributions = pd.DataFrame({
        'variable': list(suda_result.rx2('attribute_contributions').rx2('variable')),
        'contribution': list(suda_result.rx2('attribute_contributions').rx2('contribution')).round(2)
    }).sort_values(by='contribution', ascending=False)

    attribute_level_contributions = pd.DataFrame({
        'variable': list(suda_result.rx2('attribute_level_contributions').rx2('variable')),
        'attribute': list(suda_result.rx2('attribute_level_contributions').rx2('attribute')),
        'contribution': list(suda_result.rx2('attribute_level_contributions').rx2('contribution')).round(2)
    }).sort_values(by=['variable', 'contribution'], ascending=[True, False])

    df['dis-score'] = dis_score
    df['score'] = score

    return {
        "data_with_scores": df,
        "attribute_contributions": attribute_contributions,
        "attribute_level_contributions": attribute_level_contributions
    }

