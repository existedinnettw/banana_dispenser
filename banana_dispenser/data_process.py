import pandas as pd
from expression import Some, Nothing, Option, pipe, Ok
import pathlib
import traceback


def open_list_file(file_path: Option[str]) -> Option[pd.DataFrame]:
    def check_id_as_index(df_op: Option[pd.DataFrame]) -> Option[pd.DataFrame]:
        match df_op:
            case Option(tag="some"):
                df = df_op.value
                if "id" in df.columns:
                    df = df.set_index("id")
                else:
                    df.index.name = "id"
                # print(df)
                return Some(df)
            case _:
                return Nothing

    def read_csv(io: Option[str]) -> Option[pd.DataFrame]:
        try:
            return Some(
                pd.read_csv(
                    io.value,
                    skipinitialspace=True,
                    # parse_dates=["pickup_datetime"]
                )
            )
        except Exception:
            # traceback.print_exc()
            return Nothing

    def read_excel(io: Option[str]) -> Option[pd.DataFrame]:
        try:
            return Some(pd.read_excel(io.value))
        except Exception:
            # traceback.print_exc()
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


def people_df_validator(people_df_op: Option[pd.DataFrame]) -> Option[pd.DataFrame]:
    # pandas not well combine with pydantic yet

    # check if column exist
    match people_df_op:
        case Option(tag="some"):
            people_df = people_df_op.value

            required_columns = ["name"]
            if not all(column in people_df.columns for column in required_columns):
                return Nothing
            # print(people_df)

            # check assign datatype
            try:
                people_df = people_df.astype(
                    {
                        "name": str,
                    }
                )
                # print(people_df)
                return Some(people_df)
            except ValueError:
                # traceback.print_exc()
                return Nothing
        case _:
            return Nothing


def objects_df_validator(objects_df_op: Option[pd.DataFrame]) -> Option[pd.DataFrame]:
    # pandas not well combine with pydantic yet

    # check if column exist
    match objects_df_op:
        case Option(tag="some"):
            # check if columns exactly ["object", "people_id", "pickup_datatime", "name"]
            objects_df = objects_df_op.value
            # print(objects_df)

            required_columns = ["object", "people_id", "pickup_datetime"]
            if not all(column in objects_df.columns for column in required_columns):
                return Nothing
            # print(objects_df)

            # check assign datatype
            try:
                objects_df = objects_df.astype(
                    {
                        "object": str,
                        "people_id": pd.Int64Dtype(),
                    }
                )
                objects_df["pickup_datetime"] = pd.to_datetime(
                    objects_df["pickup_datetime"], format="%Y-%m-%dT%H:%M:%S%z"
                )
                # print(objects_df)
                return Some(objects_df)
            except ValueError:
                # traceback.print_exc()
                return Nothing
        case _:
            return Nothing


def combine_to_orders_table(
    people_df: Option[pd.DataFrame], objects_df: Option[pd.DataFrame]
) -> Option[pd.DataFrame]:
    try:
        combined_df = objects_df.value.merge(
            people_df.value,
            # how="outer",
            how="left",
            left_on="people_id",
            right_on="id",
            suffixes=(None, "_DROP"),
        ).filter(regex="^(?!.*DROP)")
        # print(combined_df)
        combined_df.set_axis(["object", "people_id", "pickup_datatime", "name"], axis=1)

        combined_df = combined_df.astype(
            {
                "people_id": pd.Int64Dtype(),
            }
        )
        # if any entry which is not match have no people_df --> they are wrong
        non_matched_combined_df = combined_df[combined_df["people_id"].isnull()]
        # print("non matched:\n", non_matched_combined_df, "\n")
        if not non_matched_combined_df.empty:
            print("[WARNING] following entry is not matched")
            print(non_matched_combined_df)
        # TODO may need to list people not yet order

        matched_combined_df = combined_df[~combined_df["people_id"].isnull()]
        # print("matched:\n", matched_combined_df, "\n")
        return Some(matched_combined_df)
    except Exception:
        # traceback.print_exc()
        return Nothing


# def check_order( users:pd.Data):
#     pass
