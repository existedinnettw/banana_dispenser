import pandas as pd


def check_id_as_index(df: pd.DataFrame) -> pd.DataFrame:
    if "id" in df.columns:
        df = df.set_index("id")
    else:
        df.index.name = "id"
    print(df)
    return df


# def check_order( users:pd.Data):
#     pass
