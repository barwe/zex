IMPORTED_PANDAS = None


class DisabledError(Exception):
    pass


def import_pandas():

    global IMPORTED_PANDAS

    if IMPORTED_PANDAS is None:
        import pandas as pd

        for k in dir(pd.DataFrame):
            if k.startswith("to_"):
                setattr(pd, k, None)

        IMPORTED_PANDAS = pd

    return IMPORTED_PANDAS


def pd_read_csv(*args, **kwargs):
    from pandas import DataFrame

    pd = import_pandas()
    if isinstance(args[0], str):
        raise DisabledError("Reading from filepath is not supported")
    df: DataFrame = pd.read_csv(*args, **kwargs)
    return df


def pd_to_csv(df, *args, **kwargs):
    pd = import_pandas()
    if isinstance(args[0], str):
        raise DisabledError("Writing to filepath is not supported")
    pd.DataFrame.to_csv(df, *args, **kwargs)
