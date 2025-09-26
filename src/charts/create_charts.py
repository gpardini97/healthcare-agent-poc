# --- Standard Library ---
import os
from pathlib import Path

# --- Third-Party Libraries ---
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def generate_and_store_plots(
        df_daily_info: pd.DataFrame,
        daily_period: int = 30, 
        monthly_period: int = 12
    ):
    """
    Generate two plots using seaborn/matplotlib:
        1. Daily number of cases for the last `daily_period` days (line plot with filled area)
        2. Monthly number of cases for the last `monthly_period` months (bar plot with last month highlighted)
    
    Optionally, save the plots as PNG files.

    Args:
        df_daily_info (pd.DataFrame): DataFrame with daily case counts.
                           Must contain columns:
                           - 'DT_NOTIFIC' (datetime)
                           - 'NU_CASOS' (int/float)
        daily_period (int): Number of days for daily trend plot.
        monthly_period (int): Number of months for monthly trend plot.
        save_path (str, optional): Directory path to save plots. If None, plots are not saved.
    """
    # Setting the path to store images
    EXP_IMG_DIR = Path("../../images")

    # Make sure the folder exists
    os.makedirs(EXP_IMG_DIR, exist_ok=True)

    # Ensure datetime type
    df_daily_info["DT_NOTIFIC"] = pd.to_datetime(df_daily_info["DT_NOTIFIC"])

    # Set seaborn style
    sns.set_theme(style="white")

    last_date = df_daily_info["DT_NOTIFIC"].max()

    # -----------------------
    # Daily plot with filled area
    # -----------------------
    start_date = last_date - pd.Timedelta(days=daily_period-1)
    df_last = df_daily_info[df_daily_info["DT_NOTIFIC"] >= start_date]

    plt.figure(figsize=(12, 6))
    ax = sns.lineplot(
        data=df_last,
        x="DT_NOTIFIC",
        y="NU_CASOS",
        marker="o",
        markersize=7,
        linewidth=2.5,
        color="royalblue"
    )

    # Fill under the curve
    ax.fill_between(
        df_last["DT_NOTIFIC"], df_last["NU_CASOS"], color="royalblue", alpha=0.2
    )

    # Format x-axis as DD/MM and show all dates
    ax.xaxis.set_major_formatter(DateFormatter("%d/%m"))
    ax.set_xticks(df_last["DT_NOTIFIC"])
    ax.grid(axis='x', linestyle='--', alpha=0.5)  # vertical grid
    plt.title(f"Daily SRAG Cases - Last {daily_period} Days", fontsize=14, weight="bold")
    plt.xlabel("Date")
    plt.ylabel("Number of Cases")
    plt.xticks(rotation=45)
    plt.tight_layout()

    EXP_IMG_DIR = Path(__file__).parent.parent.parent / "images"
    os.makedirs(EXP_IMG_DIR, exist_ok=True)
    print(f"Saving plots to: {EXP_IMG_DIR.resolve()}")


    # Storing images
    plt.savefig(
        EXP_IMG_DIR / f"daily_cases_last_{daily_period}_days.png", 
        dpi=300
    )

    plt.close()
    # -----------------------
    # Monthly plot with last partial month highlighted
    # -----------------------
    start_month = last_date - pd.DateOffset(months=monthly_period)
    df_last_n_months = df_daily_info[df_daily_info["DT_NOTIFIC"] >= start_month]

    # Aggregate by month-end using ME
    df_monthly = (
        df_last_n_months
        .set_index("DT_NOTIFIC")
        .resample("ME")["NU_CASOS"]
        .sum()
        .reset_index()
    )

    # Format month as MM/YY
    df_monthly["month_label"] = df_monthly["DT_NOTIFIC"].dt.strftime("%m/%y")

    # Check if last month is partial
    is_last_partial = df_monthly["DT_NOTIFIC"].iloc[-1].month == last_date.month and \
                      df_monthly["DT_NOTIFIC"].iloc[-1].year == last_date.year
    if is_last_partial:
        df_monthly.loc[
            df_monthly.index[-1], "month_label"
        ] += f" (until {last_date.strftime('%d/%m')})"
        

    # Prepare colors: all bars royalblue, last one orange if partial
    colors = ["royalblue"] * len(df_monthly)
    if is_last_partial:
        colors[-1] = "orange"

    plt.figure(figsize=(12, 6))
    bars = plt.bar(
        df_monthly["month_label"], df_monthly["NU_CASOS"], color=colors
    )

    # Highlight last x-axis label (negrito)
    if is_last_partial:
        tick_labels = plt.gca().get_xticklabels()
        tick_labels[-1].set_fontweight("bold")
        tick_labels[-1].set_color("black")

    plt.title(
        f"Monthly SRAG Cases - Last {monthly_period} Months", 
        fontsize=14, weight="bold"
    )
    plt.xlabel("Month")
    plt.ylabel("Number of Cases")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Storing images
    plt.savefig(
        EXP_IMG_DIR / f"monthly_cases_last_{monthly_period}_months.png", 
        dpi=300
    )

    plt.close()
