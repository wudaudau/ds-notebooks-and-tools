"""
Before committing
- [ ] Update this code. This seems not a mature version for our analysis. I will come back later once I have a better understanding of doing GSEA, ORA, and pathway analysis using g:Profiler. I might need to add more functions to this script to support different types of annotations and analyses based on our needs.
- [ ] Update the Title, Author, Date, Objective, License, and Description sections in the docstring below.
- [ ] Ensure no sensitive information (e.g., API keys, personal data, project name, cohort name, employee names, etc) is included in the code or comments.
- [ ] Remove this checklist and the instructions above from the final code.


Title:
Author: wudaudau (GitHub)
Date: YYYY-MM-DD
Objective:
License:

Copyright © YYYY wudaudau

AI Assistance:
    Tool: GitHub Copilot, ChatGPT
    Usage: Drafting and code suggestions
    Review: Human-verified

Description:
"""

from pathlib import Path
import logging

import pandas as pd
from gprofiler import GProfiler


def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

def annotate_uniprot_ids(uniprot_ids:list, logger:logging.Logger, organism='hsapiens') -> pd.DataFrame:
    """
    Annotate a list of UniProt IDs using g:Profiler API.

    Parameters:
    uniprot_ids (list): A list of UniProt IDs to annotate.
    output_file (Path): The path to save the annotated results.

    Returns:
    None
    """
    # Initialize g:Profiler
    gp = GProfiler(return_dataframe=True)

    # Query g:Profiler for annotations
    logger.info(f"Annotating {len(uniprot_ids)} UniProt IDs for organism '{organism}'...")


    # g:Profiler API has a limit on the number of queries per request, so we need to batch the queries if there are more than 100 UniProt IDs.
    batch_size = 100
    batch_results = []
    total_batches = ((len(uniprot_ids) - 1) // batch_size) + 1
    for i, batch in enumerate(chunked(uniprot_ids, batch_size), 1):
        logger.info(f"Processing batch {i} of {total_batches} with {len(batch)} UniProt IDs...")
        batch = {uniprot_id: [uniprot_id] for uniprot_id in batch} # g:Profiler API expects a dictionary of query lists, where each key is a query name and the value is a list of identifiers. Here we use the UniProt ID as both the key and the single item in the list to ensure that each UniProt ID is treated as a separate query. This allows us to get annotations for each individual UniProt ID rather than treating them as a single batch query.
        # TODO: I might need to add try-except block here to catch any potential errors from the g:Profiler API and log them without crashing the entire annotation process. 
        batch_result = gp.profile(query=batch, organism=organism, sources=['REAC', 'KEGG', 'GO:BP', 'GO:MF', 'GO:CC']) # Biological Process (BP), Molecular Function (MF), and Cellular Component (CC)
        batch_results.append(batch_result)

    res_df = pd.concat(batch_results, ignore_index=True)
    
    return res_df


def annotate_and_catch_raw(uniprot_ids:list, output_dir:Path, logger:logging.Logger, organism='hsapiens') -> pd.DataFrame:
    """
    Annotate a list of UniProt IDs using g:Profiler API and catch raw results in a parquet file.
    If the cache file already exists, it will load the cached annotations and only query missing UniProt IDs.
    
    Parameters:
    uniprot_ids (list): A list of UniProt IDs to annotate.
    output_dir (Path): The directory to save the annotated results.
    logger (logging.Logger): Logger for logging information and errors.
    organism (str): The organism to query in g:Profiler (default is 'hsapiens' for human).

    Returns:
    pd.DataFrame: A DataFrame containing the extracted annotations.
    """
    
    cache_path = output_dir / f"gprofiler_annotations_cache.parquet"
    # If cache exists, load and only query missing UniProts
    if cache_path.exists():
        logger.info(f"Loading cached annotations from {cache_path}...")
        cached_df = pd.read_parquet(cache_path)

        cached_uniprot_ids = set(cached_df['query'].unique())
        missing_uniprot_ids = [uniprot_id for uniprot_id in uniprot_ids if uniprot_id not in cached_uniprot_ids]

        if missing_uniprot_ids:
            logger.info(f"Annotating {len(missing_uniprot_ids)} missing UniProt IDs...")
            new_df = annotate_uniprot_ids(missing_uniprot_ids, logger, organism)
            annotations_df_raw = pd.concat([cached_df, new_df], ignore_index=True)
            annotations_df_raw.to_parquet(cache_path, index=False)
        else:
            logger.info("All UniProt IDs are already annotated in the cache.")
            annotations_df_raw = cached_df.copy()
    else:
        logger.info(f"No cache found. Annotating all {len(uniprot_ids)} UniProt IDs...")
        annotations_df_raw = annotate_uniprot_ids(uniprot_ids, logger, organism)
        annotations_df_raw.to_parquet(cache_path, index=False)
    return annotations_df_raw

def extract_annotations(annotations_raw:pd.DataFrame, source:str) -> pd.DataFrame:
    """
    Extract specific annotations from g:Profiler results based on the source.

    Parameters:
    annotations_raw (pd.DataFrame): The DataFrame containing the raw g:Profiler results (not yet filtered by source).
        It's the output of the annotate_uniprot_ids function.
        There are multiple sources in the results, including 'REAC', 'KEGG', 'GO:BP', 'GO:MF', and 'GO:CC'.
    source (str): The source of annotations to extract (e.g., 'REAC', 'KEGG', 'GO:BP', 'GO:MF', 'GO:CC').

    Returns:
    pd.DataFrame: A DataFrame containing the extracted annotations for the specified source.
    """
    extracted = annotations_raw[annotations_raw['source'] == source]

    # The most import columns for xxx are query, source, term_name, term_size
    # native and p_value are also important for filtering and ranking the annotations
    # TODO: Add organism column to the output for better traceability
    family_df = (
        extracted.sort_values(["query", "term_size"])   # smaller term_size ~ more specific
    .groupby("query", as_index=False)
    .first()[["query", "name", "native", "term_size", "p_value"]]
    .rename(columns={"query": "uniprot", "name": "family"}) # Renaming columns for clarity
    )
    
    return family_df



def main(uniprot_ids:list, output_dir:Path, output_type:str):
    """
    Main function to annotate UniProt IDs and save results.

    Parameters:
    uniprot_ids (list): A list of UniProt IDs to annotate.
    output_dir (Path): The directory to save the annotated results.
    output_type (str): The file format to save the results (e.g., 'tsv', 'csv', 'parquet').
    logger (logging.Logger): Logger for logging information and errors.

    Returns:
    None
    """
    if output_dir.exists():
        is_overwrite = input(f"Output directory {output_dir} already exists. Do you want to overwrite it? (y/n): ")
        if is_overwrite.lower() != 'y':
            logging.warning(f"Output directory {output_dir} already exists and user chose not to overwrite. Exiting the annotation process.")
            return
        else:
            logging.info(f"User chose to overwrite the existing output directory {output_dir}. Proceeding with annotation and overwriting existing files.")
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Set up logging
    logging.basicConfig(filename=output_dir / "gprofiler_fetch.log",
                        filemode='w',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()


    # Remove complexed UniProt IDs (e.g., "A6NEF3_A6NEM1_A6NI86") to ensure compatibility with g:Profiler
    excluded_uniprot_ids = [uniprot_id for uniprot_id in uniprot_ids if "_" in uniprot_id]
    if excluded_uniprot_ids:
        logger.warning(f"Excluding {len(excluded_uniprot_ids)} complexed UniProt IDs that contain underscores: {excluded_uniprot_ids}")


    # Filter out complexed UniProt IDs before annotation
    uniprot_ids = [uniprot_id for uniprot_id in uniprot_ids if "_" not in uniprot_id]

    
    logger.info(f"Annotating {len(uniprot_ids)} UniProt IDs after excluding complexed IDs.")
    entire_annotation_df = annotate_and_catch_raw(uniprot_ids, output_dir, logger)
    


    # Extract annotations for each source (family) and save to separate files
    for source in ['REAC', 'KEGG', 'GO:BP', 'GO:MF', 'GO:CC']:
        family_df = extract_annotations(entire_annotation_df, source)
        source_text = source.replace(":", "").lower()  # Remove colon and convert to lowercase for file naming


        # Save the extracted annotations to a file
        if output_type == "tsv":
            file_path = output_dir / f"{source_text}_annotations.tsv"
            family_df.to_csv(file_path, sep="\t", index=False) # uniprot will be the first column.
        elif output_type == "csv":
            file_path = output_dir / f"{source_text}_annotations.csv"
            family_df.to_csv(file_path, index=False) # uniprot will be the first column.
        elif output_type == "parquet":
            file_path = output_dir / f"{source_text}_annotations.parquet"
            family_df.to_parquet(file_path, index=False) # uniprot will be the first column.
        else:
            logger.error(f"Unsupported output type: {output_type}. Please choose 'tsv', 'csv', or 'parquet'.")
            

    logger.info("Annotation process completed successfully.")



if __name__ == "__main__":

    # ------ It's a demo script.

    # Set up output directory
    output_dir = Path("output/protein_annotations/gprofiler_fetch/")

    
    # Example list of UniProt IDs (replace with your actual list)
    uniprot_ids = [ # Replace with actual UniProt IDs
        "P05231", "P13725", "O43557",
        "P29459_P29460", # This is a complexed UniProt ID that should be excluded from annotation
        "O00585", "O00182", 
        ]  

    # Run the main function
    main(uniprot_ids, output_dir, output_type="tsv")