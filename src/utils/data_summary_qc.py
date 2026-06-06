"""
Title: Data Summary and Quality Control for Clinical Data
Author: wudaudau (GitHub)
Date: 2026-02-21


Description:
    This script is designed to perform data summary and quality control (QC) for the clinical data. It includes functions to analyze:
        - N per category group (cat1)
        - N per cat2 within each cat1 group
        - Proportion per cat2 within each cat1 group
        - Numerical variable summary (mean/SD or median/IQR) by cat1 group
        - Missingness analysis
"""

import pandas as pd


######
# General column summary function
######


def summarize_columns(df: pd.DataFrame, max_example_values=5):
    """
    df: pd.DataFrame
        DataFrame containing clinical variables to summarize.
    max_example_values: int
        Maximum number of example unique values to show per column.

    Summarize each column in the DataFrame with basic statistics (sorted by missing rate).
    The output columns include:
    - variable: column name
    - dtype: data type of the column
    - guessed_type: guessed variable type (numeric, categorical, binary, etc.)
    - n: number of rows
    - n_missing: number of missing values
    - missing_rate: proportion of missing values
    - n_unique: number of unique values
    - example_values: a few example unique values from the column
    """
    
    summary = []

    df = df.copy()  # work on a copy to avoid modifying the original DataFrame
    n_rows = len(df)

    for col in df.columns:
        s = df[col]
        n_missing = s.isna().sum()
        missing_rate = n_missing / n_rows
        
        # basic type
        dtype = s.dtype
        
        # unique values (careful with high cardinality)
        n_unique = s.nunique(dropna=True)
        example_values = s.dropna().unique()[:max_example_values]
        
        # simple type guess
        if pd.api.types.is_numeric_dtype(s):
            var_type = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(s):
            var_type = "datetime"
        elif n_unique == 2:
            var_type = "binary (2-level)"
        elif n_unique < 15:
            var_type = "categorical (low-card)"
        elif n_unique < n_rows * 0.5:
            var_type = "categorical (high-card)"
        else:
            var_type = "id-like / free-text?"

        summary.append({
            "variable": col,
            "dtype": str(dtype),
            "guessed_type": var_type,
            "n": n_rows,
            "n_missing": n_missing,
            "missing_rate": round(missing_rate, 3),
            "n_unique": int(n_unique),
            "example_values": example_values
        })

    return pd.DataFrame(summary).sort_values("missing_rate", ascending=True)

######
# Categorical variables analysis functions
######

def analyze_count_per_cat_group(df:pd.DataFrame, group_col:str, dropna:bool=True) -> pd.Series:
    """
    Analyze count per category group.

    Args:
        df: Input DataFrame.
        group_col: The column name of the categorical variable to analyze.
        dropna: Whether to exclude NaN values from the count. Default is True.

    Returns:
        A Series with counts per category group.
    """
    count_per_cat_group = df[group_col].value_counts(dropna=dropna).sort_index() # Sort by category for better readability
    return count_per_cat_group

def analyze_count_per_cat2_within_cat1(df:pd.DataFrame, cat1_col:str, cat2_col:str, dropna:bool=True) -> pd.DataFrame:
    """
    Analyze count per cat2 within each cat1 group.

    Args:
        df: Input DataFrame.
        cat1_col: The column name of the first categorical variable (e.g., t1_group).
        cat2_col: The column name of the second categorical variable (e.g., t1_adhd_cat_parent).

    Returns:
        A DataFrame with counts of cat2 categories within each cat1 group.
        Index will be cat1 categories, columns will be cat2 categories, and values will be counts.
    """
    count_per_cat2_within_cat1 = df.groupby(cat1_col)[cat2_col].value_counts(dropna=dropna).unstack(fill_value=0)
    return count_per_cat2_within_cat1

def analyze_proportion_per_cat2_within_cat1(df:pd.DataFrame, cat1_col:str, cat2_col:str, dropna:bool=True) -> pd.DataFrame:
    """
    Analyze proportion per cat2 within each cat1 group.

    Args:
        df: Input DataFrame.
        cat1_col: The column name of the first categorical variable (e.g., t1_group).
        cat2_col: The column name of the second categorical variable (e.g., t1_adhd_cat_parent).

    Returns:
        A DataFrame with proportions of cat2 categories within each cat1 group.
        Index will be cat1 categories, columns will be cat2 categories, and values will be proportions.
    """
    proportion_per_cat2_within_cat1 = df.groupby(cat1_col)[cat2_col].value_counts(normalize=True, dropna=dropna).unstack(fill_value=0)
    return proportion_per_cat2_within_cat1



######
# Numerical variables analysis functions
######




def analyze_numeric_mean_std_median_iqr_by_cat_group(df:pd.DataFrame, numeric_col:str, group_col:str) -> pd.DataFrame:
    """
    Analyze mean/SD or median/IQR of a numeric variable by categorical group.

    Args:
        df: Input DataFrame.
        numeric_col: The column name of the numeric variable to analyze (e.g., age).
        group_col: The column name of the categorical variable to group by (e.g., t1_group).
    Returns:
        A DataFrame with mean, SD, median, and IQR of the numeric variable for each category group.
    """
    stats = df.groupby(group_col)[numeric_col].agg(
        mean='mean',
        std='std',
        median='median',
        iqr=lambda x: x.quantile(0.75) - x.quantile(0.25)
    )
    return stats



######
# Missingness analysis functions
######

def analyze_individual_missingness(df:pd.DataFrame, sort_on:str=None) -> pd.DataFrame:
    """
    Analyze missingness for each individual (row) in the DataFrame.

    Args:
        df: Input DataFrame.
            Each row represents an individual, and each column represents a variable. 
        sort_by_rate: Whether to sort the output DataFrame by missingness rate in descending order. Default is False.
             If sort_by_rate is False, the output DataFrame will be in the same order as the rows in the input DataFrame.
             If sort_by_rate is True, the output DataFrame will be sorted by missingness rate in descending order, which can help identify individuals with the highest missingness.
    Returns:
        A DataFrame with the count and rate of missing values for each individual (row) in the input DataFrame.
    """
    return analyze_variable_missingness(df.T, sort_on=sort_on)


def analyze_variable_missingness(df:pd.DataFrame, sort_on:str=None) -> pd.DataFrame:
    """
    Analyze missingness for each variable (column) in the DataFrame.

    Args:
        df: Input DataFrame.
        sort_by_rate: Whether to sort the output DataFrame by missingness rate in descending order. Default is False.
            If sort_by_rate is False, the output DataFrame will be in the same order as the columns in the input DataFrame.
            If sort_by_rate is True, the output DataFrame will be sorted by missingness rate in descending order, which can help identify variables with the highest missingness.
    Returns:
        A DataFrame with the count and rate of missing values for each variable (column) in the input DataFrame.
    """
    total_count = len(df)
    missing_count = df.isnull().sum()
    missing_rate = df.isnull().mean()
    df_res = pd.DataFrame({
        'total_count': total_count,
        'missing_count': missing_count,
        'missing_rate': missing_rate
    })
    if sort_on == None:
        return df_res
    elif sort_on == "name":
        return df_res.sort_index()
    elif sort_on == "rate":
        return df_res.sort_values('missing_rate', ascending=True)
    else:
        raise ValueError(f"Invalid sort_on value: {sort_on}. Expected None, 'name', or 'rate'.")


def eligible_columns_by_missingness_threshold(df:pd.DataFrame, thresholds:list) -> pd.DataFrame:
    """
    Get eligible columns by missingness threshold.

    Args:
        df: Input DataFrame.
        thresholds: A list of thresholds (in rate) to determine eligibility based on missingness (e.g., [0.05, 0.1, 0.3, 0.5] for 5%, 10%, 30%, 50% missingness thresholds).
    Returns:
        A DataFrame with the count of columns that have missingness rate less than or equal to each threshold, and the list of those columns.
    """
    # validate thresholds
    is_valid_thresholds = all(isinstance(threshold, (int, float)) and 0 <= threshold <= 1 for threshold in thresholds)
    if not is_valid_thresholds:
        raise ValueError("Thresholds should be a list of numbers between 0 and 1.")

    missingness = analyze_variable_missingness(df)['missing_rate']

    results = []
    for threshold in sorted(thresholds):    
        label = f'<= {threshold*100:.0f}% missing'  # e.g., '<= 5%'    
        count = (missingness <= threshold).sum()
        total_columns = len(missingness)
        propotion = (missingness <= threshold).mean()
        item = missingness[missingness <= threshold].index.tolist()
        results.append({'threshold': label, 'count': count, 'total_count':total_columns, 'propotion_by_total': propotion, 'item': item}) # TODO: Find a good name for propotion column and add it to the results. 'propotion_by_total'?
    
    results_df = pd.DataFrame(results)
    return results_df





def analyze_missingness_by_group(df:pd.DataFrame, group_col:str) -> pd.DataFrame:
    """
    Analyze missingness rate by group.
    The group_col itself is not included in the result.
    Args:
        df: Input DataFrame.
        group_col: The column name of the categorical variable to group by (e.g., site).
    Returns:
        A DataFrame with the rate of missing values for each column in the input DataFrame, summarized by the specified group. 
    """
    # If group_col is all NaN, then we cannot analyze the missingness pattern by group. 
    if df[group_col].isna().all():
        raise ValueError(f"{group_col} is all NaN, cannot analyze missingness pattern by group for {group_col}")


    output_idx = df.columns.drop(group_col)
    missingness_count_by_group = df.pivot_table(index=group_col, aggfunc=lambda x: x.isnull().sum())
    total_count_by_group = df.groupby(group_col).size()
    missingness_rate_by_group = missingness_count_by_group.div(total_count_by_group, axis=0).T
    missingness_rate_by_group.columns.name = None
    return missingness_rate_by_group.reindex(output_idx)
    


# The following two functions are also for missingness analysis
# TODO: Refactor to harmonize the missingness analysis functions. Only keep the ones that are most useful and generalizable to use in the future.

def column_missingness(df:pd.DataFrame, sort_on:str=None) -> pd.Series:
    """
    Calculate the missingness rate for each column in the dataframe.
    We can also use it to evaluate the missingness of index, just transpose the dataframe and treat the index as a column.
    """
    # TODO: Count is also important. Add it to the result. See the functions above for refactoring.
    s = df.isna().mean() # Do not use percentage here
    s.name = "missingness"
    if sort_on == None:
        return s
    elif sort_on == "name":
        return s.sort_index()
    elif sort_on == "missingness":
        return s.sort_values(ascending=True) # We often focus on the least missing columns, so sort in ascending order
    else:
        raise ValueError(f"Invalid sort_on value: {sort_on}. Expected None, 'name', or 'missingness'.")
    
def column_missingness_by_group(df:pd.DataFrame, group_col:str, sort_on:str="missingness_all") -> pd.DataFrame:
    """
    Calculate the missingness rate for each column in the dataframe, grouped by a specified column.
    The result is a dataframe where the index is the group and the columns are the original columns with missingness rates as values.
    """
    missingness_by_group = df.groupby(group_col).apply(lambda x: x.isna().mean()).T

    # Rename columns as "missingness_gr_{group_value}_missingness"
    missingness_by_group.columns = [f"missingness_gr_{col}" for col in missingness_by_group.columns]

    # Add column missingness (overall) for reference
    missingness_by_group.insert(0, "missingness_all", column_missingness(df))

    if sort_on == "missingness_all":
        missingness_by_group = missingness_by_group.sort_values(by="missingness_all", ascending=True)
    elif sort_on == "no_sort":
        pass
    else:
        is_in_group_col = sort_on in df[group_col].unique()
        if not is_in_group_col:
            raise ValueError(f"Invalid sort_on value: {sort_on}. Expected 'missingness_all', 'no_sort', or a valid group value in '{group_col}'.")
        missingness_by_group = missingness_by_group.sort_values(by=f"missingness_gr_{sort_on}", ascending=True)
    return missingness_by_group
