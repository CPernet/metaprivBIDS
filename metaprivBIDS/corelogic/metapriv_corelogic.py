import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from itertools import combinations
import math
from piflib.pif_calculator import compute_cigs


import io
from rpy2 import robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

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
            value_counts = subset_data.value_counts(dropna=False)
            unique_rows = value_counts[value_counts == 1].index
            all_unique_count = len(unique_rows)
            temp_columns = [col for col in selected_columns if col != column]
            if temp_columns:
                subset_data_after_removal = data[temp_columns]
                value_counts_after_removal = subset_data_after_removal.value_counts(dropna=False)
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
        value_counts = data[selected_columns].value_counts(dropna=False)
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
        data_mod = data.copy()
        for col, history in self.combined_values_history.items():
            for values_to_combine, replacement_value in history:
                data_mod[col] = data_mod[col].replace(values_to_combine, replacement_value)
        data_mod[column_name] = data_mod[column_name].str.strip()
        print(f"Unique values in '{column_name}': {data_mod[column_name].unique()}")
        values_to_combine = input(f"Enter values to combine in '{column_name}' (comma-separated): ").split(",")
        values_to_combine = [v.strip().strip("'\"") for v in values_to_combine]
        replacement_value = input("Enter the replacement value: ").strip().strip("'\"")
        if column_name not in self.combined_values_history:
            self.combined_values_history[column_name] = []
        self.combined_values_history[column_name].append((values_to_combine, replacement_value))
        for col, history in self.combined_values_history.items():
            for values_to_combine, replacement_value in history:
                data_mod[col] = data_mod[col].replace(values_to_combine, replacement_value)
        return data_mod








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

        # Input mask value
        mask_value = input('Enter a mask value (or leave blank to skip):')
        if mask_value.strip().lower() == 'nan':  # Check if user inputs 'nan'
            mask_value = np.nan
            mask = df.isna()  # Create mask for NaN values
        elif mask_value != '':
            try:
                mask_value = float(mask_value)
                mask = df == mask_value  # Create mask for specific value
            except ValueError:
                raise ValueError("Invalid mask value. Please enter a number or 'nan'.")
        else:
            mask = None  # No masking applied

        # Compute CIGs
        cigs = pif.compute_cigs(df)
        cigs_df = pd.DataFrame(cigs)

        if mask is not None:
            cigs_df[mask] = 0  # Apply masking

        cigs_df['RIG'] = cigs_df.sum(axis=1)
        cigs_df_sorted = cigs_df.sort_values(by='RIG', ascending=False)

        # Input percentile
        try:
            percentile = int(input('Enter percentile (0-100): '))
        except ValueError:
            raise ValueError("Invalid input for percentile. Please enter a number between 0 and 100.")

        if percentile < 0 or percentile > 100:
            raise ValueError("Percentile must be between 0 and 100.")

        pif_value = np.percentile(cigs_df_sorted['RIG'], percentile)
        return pif_value, cigs_df_sorted







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




    
    def compute_suda2(self, data, selected_columns, sample_fraction=0.2, missing_value=None):
        """
        Compute SUDA2 on selected columns of the dataset.

        Parameters:
            data (pd.DataFrame): The input data.
            selected_columns (list): List of columns to include in the computation.
            sample_fraction (float): Fraction of the sample to use for SUDA2.
            missing_value: Value to treat as missing. Can be any value, including np.nan.

        Returns:
            dict: A dictionary containing the results of SUDA2 computation.
        """
        if not selected_columns:
            raise ValueError("No columns selected for SUDA2 computation.")

        # Copy selected columns without modifying missing values
        df = data[selected_columns].copy()

        # Handle categorical encoding
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype('category').cat.codes

        with localconverter(robjects.default_converter + pandas2ri.converter):
            r_df = robjects.conversion.py2rpy(df.astype(float))

        # Call the suda2 function
        suda_result = sdcMicro.suda2(
            r_df,
            missing=missing_value if missing_value is not None else None,
            DisFraction=sample_fraction
        )

        # Extract results
        dis_score = [round(x, 4) for x in list(suda_result.rx2('disScore'))]
        score = list(suda_result.rx2('score'))

        # Attribute contributions
        attribute_contributions = pd.DataFrame({
            'variable': list(suda_result.rx2('attribute_contributions').rx2('variable')),
            'contribution': [round(x, 2) for x in list(suda_result.rx2('attribute_contributions').rx2('contribution'))]
        }).sort_values(by='contribution', ascending=False)

        # Attribute level contributions
        attribute_level_contributions = pd.DataFrame({
            'variable': list(suda_result.rx2('attribute_level_contributions').rx2('variable')),
            'attribute': list(suda_result.rx2('attribute_level_contributions').rx2('attribute')),
            'contribution': [round(x, 2) for x in list(suda_result.rx2('attribute_level_contributions').rx2('contribution'))]
        }).sort_values(by=['variable', 'contribution'], ascending=[True, False])

        # Add scores to DataFrame
        df['dis-score'] = dis_score
        df['score'] = score

        # Return results
        return {
            "data_with_scores": df,
            "attribute_contributions": attribute_contributions,
            "attribute_level_contributions": attribute_level_contributions
        }




    def save_boxplot(self, df, column_name, k=2.2414):
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the DataFrame.")
        
        column_data = df[column_name].dropna()  # Extract the column data and drop missing values

        if len(column_data) < 5:
            print("Not enough data to generate a boxplot.")
            return

        # Calculate median and MAD
        median = np.nanmedian(column_data)
        mad = np.nanmedian(np.abs(column_data - median))

        if mad == 0:
            print("MAD is zero, recalculating without zero entries.")
            non_zero_data = column_data[column_data != 0]  # Exclude zero entries
            if len(non_zero_data) < 5:
                print("Not enough non-zero data to generate a boxplot.")
                return
            median = np.nanmedian(non_zero_data)
            mad = np.nanmedian(np.abs(non_zero_data - median))
            column_data = non_zero_data  # Update column_data to non_zero_data for plotting

        if mad == 0:
            print("MAD remains zero after excluding zeros.")
            return

        madn = mad / 0.6745  # Adjust MAD to robust standard deviation

        # Calculate Z-scores
        z_scores = (column_data - median) / madn

        # Identify outliers above the threshold k
        outlier_mask = z_scores > k
        outliers = column_data[outlier_mask]
        outlier_indices = outliers.index.tolist()  # Get indices of outliers

        # Print outlier indices and values
        if len(outliers) > 0:
            print(f"Outliers detected in column '{column_name}' above threshold {k}:")
            for idx in outlier_indices:
                print(f"Index: {idx}, Value: {df.loc[idx, column_name]}, Z-Score: {z_scores[idx]}")
        else:
            print(f"No outliers detected in column '{column_name}' above threshold {k}.")

        # Create the box plot
        fig, ax = plt.subplots(figsize=(8, 5))
        boxplot = ax.boxplot(
            z_scores,
            vert=False,
            patch_artist=True,
            boxprops=dict(facecolor='lightblue', color='blue'),
            medianprops=dict(color='orange'),
            flierprops=dict(marker='o', color='red', alpha=0.6)
        )

        # Adjust whiskers manually to limit them to -k and +k
        for line in boxplot['whiskers']:
            xdata = line.get_xdata()
            capped_xdata = np.clip(xdata, -k, k)  # Cap whisker ends to -k and +k
            line.set_xdata(capped_xdata)

        for cap in boxplot['caps']:
            xdata = cap.get_xdata()
            capped_xdata = np.clip(xdata, -k, k)  # Cap caps to -k and +k
            cap.set_xdata(capped_xdata)

        # Add threshold line for +k
        ax.axvline(x=k, color='red', linestyle='--', label=f'Threshold (+{k})')

        # Plot customization
        ax.set_title(f'Boxplot of Z-Scores with MAD-based Outlier Threshold (k={k})')
        ax.set_xlabel('Z-Score')
        ax.legend(loc='upper left')

        # Display the plot
        plt.show()

