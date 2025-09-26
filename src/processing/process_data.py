import pandas as pd 

from src.preprocessing.generate_aux_df import generate_df_daily_info
from src.metrics.calc_metrics import (
    calc_rate_by_period, calc_case_var_rate_by_period
)
from src.charts.create_charts import generate_and_store_plots

def generate_metrics_prompt_and_plots(
    qty_of_cases_var_period_1: int, 
    qty_of_cases_var_period_2: int, 
    death_rate_period:int, 
    uti_occup_rate_period: int,
    vacc_rate_period: int,
    df_srag: pd.DataFrame
) -> str:
    """
    Generate a summary of SRAG metrics as a string prompt and create/store corresponding plots.

    Args:
        qty_of_cases_var_period_1 (int): Number of days for the first case variation calculation.
        qty_of_cases_var_period_2 (int): Number of days for the second case variation calculation.
        death_rate_period (int): Number of days to calculate the mortality rate.
        uti_occup_rate_period (int): Number of days to calculate ICU occupancy rate.
        vacc_rate_period (int): Number of days to calculate vaccination rate.
        df_srag (pd.DataFrame): Raw SRAG dataset.

    Returns:
        str: Metrics summary formatted as a string to be used in the final report prompt.
    """
    # Generate auxiliary DataFrame with daily information
    df_daily_info = generate_df_daily_info(df_srag)

    # Calculate metrics in % 
    case_var_period_1 = calc_case_var_rate_by_period(
        df_daily_info, qty_of_cases_var_period_1
    )

    case_var_period_2 = calc_case_var_rate_by_period(
        df_daily_info, qty_of_cases_var_period_2
    )

    death_rate = calc_rate_by_period(
        df_daily_info, "NU_OBITOS", "NU_CASOS",
        death_rate_period
    )

    uti_occup_rate = calc_rate_by_period(
        df_daily_info, "NU_UTI", "NU_CASOS",
        uti_occup_rate_period
    )

    vacc_rate = calc_rate_by_period(
        df_daily_info, "NU_VACINADOS", "NU_CASOS",
        vacc_rate_period
    )

    # Storing metrics on a string to serve as a prompt later 
    # This will facilitate the construction of the final prompt
    metrics_prompt = (
        f"Segue o resumo das métricas mais recentes relacionadas às SRAGs:\n"
        f"- Taxa de variação de casos nos últimos {qty_of_cases_var_period_1} dias: {case_var_period_1}%\n"
        f"- Taxa de variação de casos nos últimos {qty_of_cases_var_period_2} dias: {case_var_period_2}%\n"
        f"- Taxa de ocupação de UTI nos últimos {uti_occup_rate_period} dias: {uti_occup_rate}%\n"
        f"- Taxa de vacinação nos últimos {vacc_rate_period} dias: {vacc_rate}%\n"
        f"- Taxa de mortalidade nos últimos {death_rate_period} dias: {death_rate}%\n"
    )

    # Generate and store plots
    generate_and_store_plots(df_daily_info)

    return (
        metrics_prompt
    )






    
    
