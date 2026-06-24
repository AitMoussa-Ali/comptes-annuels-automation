import pandas as pd

async def parse_balance(x1):

    # ✅ Find the sheet name regardless of trailing/leading spaces
    print("parsing")
    sheet_name = next(
        (s for s in x1.sheet_names if s.strip().lower() == "balance"),
        None
    )

    if sheet_name is None:
        raise ValueError(f"No 'Balance' sheet found. Available sheets: {x1.sheet_names}")

    balance_df = x1.parse(sheet_name=sheet_name, header=None)
    balance_df = balance_df.where(pd.notnull(balance_df), None)

    balance_df = balance_df.dropna().reset_index(drop=True)

    balance_df.columns = balance_df.iloc[0]
    balance_df = balance_df.iloc[1:].reset_index(drop=True)
    balance_df = balance_df.where(pd.notnull(balance_df), None)
    print("Parsed Balance !!!")
    return balance_df.to_dict(orient="records")
