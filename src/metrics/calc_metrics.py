import pandas as pd

def calc_case_var_rate_by_period(
        df_daily_info: pd.DataFrame, 
        period_days: int
) -> float:
    """
    Calculate the percentage variation of confirmed or suspected SRAG cases over a specific period.

    This function compares the total number of cases in the most recent `period_days` 
    with the total number of cases in the preceding `period_days`. The percentage change
    is calculated as:

        rate = (current_period_cases - previous_period_cases) / previous_period_cases * 100

    Args:
        df_daily_info (pd.DataFrame): DataFrame containing daily information regarding case count. 
            Expected columns:
                - 'DT_NOTIFIC' (datetime): date of notification
                - 'NU_CASOS' (int/float): number of cases reported that day
        period_days (int): Number of days to define the period for rate calculation.
            The function will use the last `period_days` as the current period 
            and the `period_days` immediately before that as the previous period.

    Returns:
        float: Percentage change of cases between the current and previous period, rounded to 2 decimals.
               Returns `inf` or raises an error if the previous period has zero cases.

    Notes:
        - Only the last 2 * period_days are considered to avoid unnecessary computation.
        - Ensure that 'DT_NOTIFIC' is of datetime type.
        - This function assumes the DataFrame is not empty and contains sufficient data
          for the specified period.
    """

    last_date = df_daily_info["DT_NOTIFIC"].max()

    # Start of the window covering the previous and current period
    window_start_date = last_date - pd.Timedelta(days=period_days*2 - 1)

    # Filter DataFrame to keep only relevant period
    df_window = df_daily_info[df_daily_info["DT_NOTIFIC"] >= window_start_date].copy()

    # Previous period: first `period_days` in the window
    df_prev_period = df_window[df_window["DT_NOTIFIC"] <= window_start_date + pd.Timedelta(days=period_days-1)]
    total_prev_cases = df_prev_period["NU_CASOS"].sum()

    # Current period: last `period_days` in the window
    df_curr_period = df_window[df_window["DT_NOTIFIC"] > window_start_date + pd.Timedelta(days=period_days-1)]
    total_curr_cases = df_curr_period["NU_CASOS"].sum()

    # Calculate percentage change
    rate = (total_curr_cases - total_prev_cases) / total_prev_cases * 100
    rate = round(rate, 2)

    return rate

def calc_rate_by_period(
        df_daily_info: pd.DataFrame, 
        numerator_col: str, 
        denominator_col: str, 
        period_days: int
) -> float:
    """
    Calculate the rate (%) of a given numerator over a denominator 
    within a specified recent period of days.

    The function computes the rate as:

        rate (%) = (sum(numerator_col) / sum(denominator_col)) * 100

    considering only rows within the last `period_days` from the most 
    recent date in the dataset.

    Args:
        df_daily_info (pd.DataFrame): DataFrame containing daily information.
            Must contain at least:
                - 'DT_NOTIFIC' (datetime): date of notification
                - `numerator_col` (int/float): column for numerator values
                - `denominator_col` (int/float): column for denominator values
        numerator_col (str): Column name to be used as the numerator.
        denominator_col (str): Column name to be used as the denominator.
        period_days (int): Number of most recent days to consider.

    Returns:
        float: Rate (%) over the specified period, rounded to 2 decimals.
               Returns `None` if denominator sum is zero.

    Notes:
        - Only the last `period_days` from the latest date in the DataFrame are considered.
        - Ensure 'DT_NOTIFIC' is datetime type.
        - This function is intended for descriptive reporting, not epidemiological modeling.
    """

    # Identify the last date in the dataset
    last_date = df_daily_info["DT_NOTIFIC"].max()

    # Define the start of the window for the period
    start_date = last_date - pd.Timedelta(days=period_days - 1)

    # Filter DataFrame to only include rows in the period
    df_period = df_daily_info[df_daily_info["DT_NOTIFIC"] >= start_date].copy()

    # Sum numerator and denominator
    numerator = df_period[numerator_col].sum()
    denominator = df_period[denominator_col].sum()

    # Avoid division by zero
    if denominator == 0:
        return None

    # Calculate rate as percentage
    rate = (numerator / denominator) * 100
    rate = round(rate, 2)

    return rate

