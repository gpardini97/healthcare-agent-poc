"""
Module: SRAG Daily Data Processing

Provides functions to generate daily aggregated information
from raw SRAG (Severe Acute Respiratory Syndrome) case data.

Functions:
    generate_df_daily_info(df_srag: pd.DataFrame) -> pd.DataFrame
        Generate a daily summary DataFrame containing:
        - Number of cases
        - Number of deaths
        - Daily ICU admissions
        - Number of vaccinated cases

    filter_df_srag_for_vacc_label(df_srag: pd.DataFrame) -> pd.DataFrame
        Filter the last 30 days of SRAG cases for vaccination labeling.

    label_vaccination_status(df: pd.DataFrame) -> pd.DataFrame
        Label each SRAG case as vaccinated or not, based on influenza,
        COVID-19, or other/unspecified classifications.
"""

import pandas as pd

def generate_df_daily_info(
    df_srag: pd.DataFrame  
)-> pd.DataFrame:
    """
    Generate a daily summary DataFrame for SRAG cases.

    Aggregates daily:
        - Total cases ('NU_CASOS')
        - Deaths ('NU_OBITOS')
        - ICU admissions ('NU_UTI')
        - Vaccinated cases ('NU_VACINADOS')

    Args:
        df_srag (pd.DataFrame): Raw SRAG dataset containing at least
                                the columns 'DT_NOTIFIC', 'NU_NOTIFIC',
                                'EVOLUCAO', 'UTI', 'VACINA', 'VACINA_COV', 'CLASSI_FIN'.

    Returns:
        pd.DataFrame: Daily aggregated DataFrame 'df_daily_info'.
    """
    
    #Extracting daily quantity of cases
    df_srag["NU_CASOS"] = (
        df_srag.groupby("DT_NOTIFIC")["NU_NOTIFIC"]
        .transform(lambda x: x.count())
    )

    # Generating initial df_daily_info
    df_daily_info =(
        df_srag[["DT_NOTIFIC", "NU_CASOS"]].drop_duplicates()
        .reset_index(drop=True)
    )

    # Generating dataframe with daily deaths
    df_deaths_daily = (
        df_srag[df_srag["EVOLUCAO"] == 2]  
        .groupby("DT_NOTIFIC")["EVOLUCAO"]  
        .count()
        .reset_index()
        .rename(columns={"EVOLUCAO": "NU_OBITOS"})  
    )

    # Generating dataframe with daily UTI admission
    df_utis_daily = (
        df_srag[df_srag["UTI"] == 1]  
        .groupby("DT_NOTIFIC")["UTI"]  
        .count()
        .reset_index()
        .rename(columns={"UTI": "NU_UTI"})  
    )

    # Generating dataframe with daily vaccinations
    # Given that the vaccination label is a bit more
    # complex, to spare processing a filtered df_srag 
    # needs to be considered
    df_srag_filtered = filter_df_srag_for_vacc_label(
        df_srag
    )

    df_srag_filtered = label_vaccination_status(
        df_srag_filtered
    )
    
    df_vacinations_daily = (
        df_srag_filtered[df_srag_filtered["VACINADO"] == 1]  
        .groupby("DT_NOTIFIC")["VACINADO"]  
        .count()
        .reset_index()
        .rename(columns={"VACINADO": "NU_VACINADOS"})  
    )

    # Merging all dfs to df_daily_info 
    df_daily_info = df_daily_info.merge(
        df_deaths_daily, on="DT_NOTIFIC", how="left"
    )

    df_daily_info = df_daily_info.merge(
        df_utis_daily, on="DT_NOTIFIC", how="left"
    )

    df_daily_info = (
        df_daily_info.merge(
            df_vacinations_daily, on="DT_NOTIFIC", how="left"
        )
    )

    return df_daily_info


def filter_df_srag_for_vacc_label(
        df_srag:pd.DataFrame
    ):

    """
    Filter SRAG cases for the last 30 days to prepare for vaccination labeling.
    Vaccination labeling takes a lot of processing, so this filter is required. 
    When the periods will be user-editable, this function will have to be adapted. 

    Args:
        df_srag (pd.DataFrame): Full SRAG dataset.

    Returns:
        pd.DataFrame: Filtered dataset containing only the last 30 days.
    """

    max_period = 30 #Can be a variable if the solution evolves

    current_max_date = df_srag["DT_NOTIFIC"].max()

    filter_start_date = (
        current_max_date - pd.Timedelta(days=max_period - 1)
    )

    df_srag_filtered = df_srag[
        df_srag["DT_NOTIFIC"] >= filter_start_date
    ].copy()

    return df_srag_filtered

def label_vaccination_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Label vaccination status (Vaccinated / Not Vaccinated) for SRAG cases.

    Rules:
        1. SRAG due to influenza (CLASSI_FIN == 1):
            - Uses only `VACINA` (influenza vaccine).
        2. SRAG due to COVID-19 (CLASSI_FIN == 5):
            - Uses only `VACINA_COV` (COVID-19 vaccine).
        3. Other viruses / agents / unspecified / null classifications:
            - Labeled as vaccinated only if both `VACINA == 1` AND `VACINA_COV == 1`.
            - If either is "No" (2), the case is labeled as not vaccinated.
            - If information is missing/ignored (9 or NaN), label is set to None.

    Expected column values:
        - VACINA, VACINA_COV:
            1 = Yes, 2 = No, 9 = Ignored, NaN = Unknown
        - CLASSI_FIN:
            1 = Influenza
            2 = Other respiratory virus
            3 = Other etiological agent
            4 = Unspecified
            5 = COVID-19
            NaN = Unknown

    Args:
        df (pd.DataFrame): DataFrame containing the columns
                           'CLASSI_FIN', 'VACINA', and 'VACINA_COV'.

    Returns:
        pd.DataFrame: Copy of the input DataFrame with an additional column 'VACINADO':
                      - 1 = Vaccinated
                      - 0 = Not vaccinated
                      - None = Unknown / Ignored
    """

    df = df.copy()
    df["VACINADO"] = df.apply(classify_row, axis=1)

    return df

def classify_row(row):
    classification = row["CLASSI_FIN"]
    vacina = row["VACINA"]
    vacina_covid = row["VACINA_COV"]

    # Influenza
    if classification == 1:
        if vacina == 1:
            return 1
        else:
            return 0

    # COVID-19
    elif classification == 5:
        if vacina_covid == 1:
            return 1
        else:
            return 0

    # Other / Unspecified / Null
    else:
        if vacina == 1 and vacina_covid == 1:
            return 1
        else:
            return 0



    
    