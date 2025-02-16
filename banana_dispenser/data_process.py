import pandas as pd
from expression import Ok, Error, Result, pipe, Option, Some
import pathlib
from datetime import datetime
import os
from pathlib import Path


def open_list_file(file_path_op: Option[str]) -> Result[pd.DataFrame, str]:

    def check_id_as_index(
        df_res: Result[pd.DataFrame, str]
    ) -> Result[pd.DataFrame, str]:
        match df_res:
            case Result(tag="ok", ok=df):
                if "id" in df.columns:
                    df = df.set_index("id")
                else:
                    df.index.name = "id"
                return Ok(df)
            case _:
                return df_res

    def rst_read_csv(io: Result[str, str]) -> Result[pd.DataFrame, str]:
        match io:
            case Result(tag="ok", ok=value):
                try:
                    return Ok(pd.read_csv(value, skipinitialspace=True))
                except Exception as e:
                    return Error(f"Error reading CSV: {str(e)}")
            case _:
                return io

    def rst_read_excel(io: Result[str, str]) -> Result[pd.DataFrame, str]:
        match io:
            case Result(tag="ok", ok=value):
                try:
                    return Ok(pd.read_excel(value))
                except Exception as e:
                    return Error(f"Error reading Excel: {str(e)}")
            case _:
                return io

    extension = pathlib.Path(file_path_op.value).suffix  # e.g. `.csv`

    match extension:
        case ".csv":
            return Ok(file_path_op.value).pipe(rst_read_csv).pipe(check_id_as_index)
        case ".xls" | ".xlsx":
            return Ok(file_path_op.value).pipe(rst_read_excel).pipe(check_id_as_index)
        case _:
            return Error("Unsupported file format {}".format(extension))


def people_df_validator(
    people_df_res: Result[pd.DataFrame, str]
) -> Result[pd.DataFrame, str]:
    match people_df_res:
        case Result(tag="ok", ok=people_df):
            required_columns = ["name"]
            if not all(column in people_df.columns for column in required_columns):
                return Error("Missing required columns in people DataFrame")
            try:
                people_df = people_df.astype({"name": str})
                return Ok(people_df)
            except ValueError as e:
                return Error(
                    f"Error converting data types in people DataFrame: {str(e)}"
                )
        case _:
            return people_df_res


def objects_df_validator(
    objects_df_res: Result[pd.DataFrame, str]
) -> Result[pd.DataFrame, str]:
    match objects_df_res:
        case Result(tag="ok", ok=objects_df):
            required_columns = ["object", "people_id", "pickup_datetime"]
            if not all(column in objects_df.columns for column in required_columns):
                return Error("Missing required columns in objects DataFrame")
            try:
                # utc for datetime64[ns, UTC]
                objects_df["pickup_datetime"] = pd.to_datetime(
                    objects_df["pickup_datetime"], format="mixed", utc=True
                )
                objects_df = objects_df.astype(
                    {"object": str, "people_id": pd.Int64Dtype()}
                )
                objects_df["pickup_datetime"] = objects_df["pickup_datetime"]
                return Ok(objects_df)
            except ValueError as e:
                return Error(
                    f"Error converting data types in objects DataFrame: {str(e)}"
                )
        case _:
            return objects_df_res


def combine_to_orders_table(
    people_df_res: Result[pd.DataFrame, str], objects_df_res: Result[pd.DataFrame, str]
) -> Result[pd.DataFrame, str]:
    match (people_df_res, objects_df_res):
        case (Result(tag="ok", ok=people_df), Result(tag="ok", ok=objects_df)):
            try:
                # https://stackoverflow.com/a/37654295
                combined_df = (
                    objects_df.reset_index()
                    .merge(
                        people_df,
                        how="left",
                        left_on="people_id",
                        right_on="id",
                        suffixes=(None, "_DROP"),
                    )
                    .filter(regex="^(?!.*DROP)")
                    .set_index("id")
                )
                combined_df.set_axis(
                    ["object", "people_id", "pickup_datetime", "name"], axis=1
                )

                combined_df = combined_df.astype({"people_id": pd.Int64Dtype()})
                non_matched_combined_df = combined_df[combined_df["people_id"].isnull()]
                if not non_matched_combined_df.empty:
                    print("[WARNING] following entry is not matched")
                    print(non_matched_combined_df)

                matched_combined_df = combined_df[~combined_df["people_id"].isnull()]
                return Ok(matched_combined_df)
            except Exception as e:
                return Error(f"Error combining DataFrames: {str(e)}")
        case (Result(tag="ok", ok=people_df), _):
            return objects_df_res  # error
        case (_, _):
            return people_df_res  # error


def insert_conflict_to_path(path: str):
    """
    Modifies the given file path by inserting 'conflict' before the file extension.

    Args:
        path (str): The original file path.

    Returns:
        str: The modified file path with 'conflict' inserted.

    Example:
        >>> insert_conflict_to_path("abc/xxx.csv")
        'abc/xxx.conflict.csv'
    """
    # Split the path into the base and extension
    base, ext = os.path.splitext(path)

    # Insert 'conflict' before the extension
    return f"{base}.conflict{ext}"


def export_df_list_file(
    df_op: Option[pd.DataFrame], file_path_op: Option[Path]
) -> Result[None, str]:
    """ """
    extension = file_path_op.value.suffix  # e.g. `.csv`

    if df_op.is_none():
        return Error("No dataframe passed in.")

    match extension:
        case ".csv":
            df_op.value.to_csv(str(file_path_op.value), index=True)
            return Ok(None)
        case ".xls" | ".xlsx":
            df_op.value.to_excel(str(file_path_op.value), index=True)
            return Ok(None)
        case _:
            return Error("Unsupported file format {}".format(extension))


def export_and_save_back_origin_path(
    df: pd.DataFrame, file_path: str, ori_touch_time: datetime
) -> None:
    """
    Save df back to original path, depend on touch time
    """
    assert isinstance(file_path, str), "file_path is type {}".format(type(file_path))
    assert isinstance(ori_touch_time, datetime)

    q = Path(file_path)

    # Create parent directories if they don't exist
    q.parent.mkdir(parents=True, exist_ok=True)

    df_op = Some(df)
    q_op = Some(q)

    if not q.exists():
        # df.to_csv(str(q), index=True)
        export_df_list_file(df_op, q_op)

    # exists
    if not q.is_file():
        target_path = insert_conflict_to_path(str(q))
        export_df_list_file(df_op, pipe(target_path, Path, Some))

    if ori_touch_time != datetime.fromtimestamp(os.path.getmtime(str(q))):
        target_path = insert_conflict_to_path(str(q))
        export_df_list_file(df_op, pipe(target_path, Path, Some))

    export_df_list_file(df_op, q_op)
