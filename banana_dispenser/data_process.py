import pandas as pd
from expression import Some, Nothing, Option, pipe, Ok
import pathlib


def open_list_file(file_path: Option[str]) -> Option[pd.DataFrame]:
    def check_id_as_index(df_op: Option[pd.DataFrame]) -> Option[pd.DataFrame]:
        if df_op.is_some():
            df = df_op.value
            if "id" in df.columns:
                df = df.set_index("id")
            else:
                df.index.name = "id"
            # print(df)
            return Some(df)
        return Nothing

    def read_csv(io: Option[str]) -> Option[pd.DataFrame]:
        try:
            return Some(pd.read_csv(io.value, skipinitialspace=True))
        except Exception as e:
            print("[ERROR]:", e)
            return Nothing

    def read_excel(io: Option[str]) -> Option[pd.DataFrame]:
        try:
            return Some(pd.read_excel(io.value))
        except Exception as e:
            print("[ERROR]:", e)
            return Nothing

    extension = pathlib.Path(file_path.value).suffix  #'.csv'

    match extension:
        case ".csv":
            return file_path.pipe(read_csv, check_id_as_index)
        case ".xls" | ".xlsx":
            return file_path.pipe(read_excel, check_id_as_index)
        case _:
            # unsupport format
            return Nothing


def combine_to_orders_table(
    people_df: Option[pd.DataFrame], objects_df: Option[pd.DataFrame]
) -> Option[pd.DataFrame]:
    try:
        combined_df = objects_df.value.merge(
            people_df.value,
            how="outer",
            # how="inner",
            left_on="people_id",
            right_on="id",
            suffixes=(None, "_DROP"),
        ).filter(regex="^(?!.*DROP)")
        # print(combined_df)
        combined_df.set_axis(["object", "people_id", "pickup_datatime", "name"], axis=1)
        return Some(combined_df)
    except Exception as e:
        print("[ERROR]:", e)
        return Nothing


# def check_order( users:pd.Data):
#     pass
