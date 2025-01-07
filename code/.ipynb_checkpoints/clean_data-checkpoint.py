import pandas as pd
import numpy as np

from constants import RUN_PASS_DICT, MOTION_CAT_DICT, OFFENSIVE_FORMATION_DICT

def rotate_direction_and_orientation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rotate the direction and orientation angles so that 0° points from left to right on the field, and increasing angle goes counterclockwise
    This should be done BEFORE the call to make_plays_left_to_right, because that function with compensate for the flipped angles.

    :param df: the aggregate dataframe created using the aggregate_data() method

    :return df: the aggregate dataframe with orientation and direction angles rotated 90° clockwise
    """
    print(
        "INFO: Transforming orientation and direction angles so that 0° points from left to right, and increasing angle goes counterclockwise..."
    )
    df["o_clean"] = (-(df["o"] - 90)) % 360
    df["dir_clean"] = (-(df["dir"] - 90)) % 360
    return df


def make_plays_left_to_right(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flip tracking data so that all plays run from left to right. The new x, y, s, a, dis, o, and dir data
    will be stored in new columns with the suffix "_clean" even if the variables do not change from their original value.

    :param df: the aggregate dataframe created using the aggregate_data() method

    :return df: the aggregate dataframe with the new columns such that all plays run left to right
    """
    print("INFO: Flipping plays so that they all run from left to right...")
    df["x_clean"] = np.where(
        df["playDirection"] == "left",
        120 - df["x"],
        df[
            "x"
        ],  # 120 because the endzones (10 yds each) are included in the ["x"] values
    )
    df["y_clean"] = df["y"]
    df["s_clean"] = df["s"]
    df["a_clean"] = df["a"]
    df["dis_clean"] = df["dis"]
    df["o_clean"] = np.where(
        df["playDirection"] == "left", 180 - df["o_clean"], df["o_clean"]
    )
    df["o_clean"] = (df["o_clean"] + 360) % 360  # remove negative angles
    df["dir_clean"] = np.where(
        df["playDirection"] == "left", 180 - df["dir_clean"], df["dir_clean"]
    )
    df["dir_clean"] = (df["dir_clean"] + 360) % 360  # remove negative angles
    return df

def convert_geometry_to_int(df: pd.DataFrame):
    """
    Convert the x_clean, y_clean, dir_clean, o_clean, s_clean, a_clean columns to int to reduce dataframe size.
    We do this by multiplying the position, speed, acceleration vectors by 100, and the angle vectors by 10, and
    rounding to the nearest integer. This effectively reduces the precision of position, speed, and acceleration
    to the hundredths decimal, and the angle to the tenth decimal.

    :param df: the aggregate dataframe created using the aggregate_data() method

    :return df: the aggregate dataframe with the geometry column converted to a tuple of ints
    """
    state_cols = ["x_clean", "y_clean", "s_clean", "a_clean"]
    angle_cols = ["dir_clean", "o_clean"]

    # Fill NaN values with 0 (or another value if needed) before applying the transformation
    df[state_cols + angle_cols] = df[state_cols + angle_cols].fillna(0)

    print("INFO: Converting geometry variables from floats to int...")
    before = df.memory_usage(deep=True).sum()
    # For state_cols
    for col in state_cols:
        df[col] = (df[col] * 100).apply(round)  # Use df[col] instead of df.loc[:, col]
        assert (
            df[col].abs().max() < 32767
        ), f"ERROR: The max value of column {col} is too large for int 16"

    # For angle_cols
    for col in angle_cols:
        df[col] = (df[col] * 10).apply(round)  # Use df[col] instead of df.loc[:, col]
        assert (df[col] >= 0).all(), "Angles should be greater than 0"
        assert (
            df[col].max() < 32767
        ), f"ERROR: The max value of column {col} is too large for int 16"

    df = df.astype(
        {col: "int16" for col in state_cols + angle_cols}
    )  # int16 needed to cover all values
    after = df.memory_usage(deep=True).sum()
    print(f"INFO: Memory usage reduced from {before} to {after}")

    return df

def downcast_ints_and_floats(df: pd.DataFrame) -> pd.DataFrame:
    print("INFO: Downcasting integers and floats...")
    before = df.memory_usage(deep=True).sum()
    int_columns = df.select_dtypes(include="integer").columns
    float_columns = df.select_dtypes(include="float").columns

    # Downcast integer columns
    for col in int_columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")

    # Downcast float columns
    for col in float_columns:
        df[col] = pd.to_numeric(df[col], downcast="float")

    after = df.memory_usage(deep=True).sum()
    print("INFO: Memory usage reduced from {} to {}".format(before, after))

    return df

def optimize_memory_usage(df):
    """
    Optimize the memory usage by performing the following numerical operations:

    1) Converts the speed and position to ints by multiplying by 100 and then converting to int
    2) Converts angles to ints by multiplying by 10 and then converting to int
    3) Downcast all ints and floats to the most compact representation without corrupting the value
    """

    df = convert_geometry_to_int(df)
    df = downcast_ints_and_floats(df)

    return df


def clean_data(opt_df: pd.DataFrame) -> pd.DataFrame:
    opt_df = rotate_direction_and_orientation(opt_df)
    opt_df = make_plays_left_to_right(opt_df)
    opt_df = optimize_memory_usage(opt_df)
    
    return opt_df

def convert_to_DICT(df, RUN_PASS_DICT, MOTION_CAT_DICT, OFFENSIVE_FORMATION_DICT):
    """
    Converts the 'RUN_PASS_DICT', 'MOTION_CAT_DICT', and 'OFFENSIVE_FORMATION_DICT' columns in the DataFrame to integers 
    using the provided dictionaries.
    
    Args:
    - df (DataFrame): The DataFrame containing the columns to be converted.
    - run_pass_dict (dict): Dictionary to convert 'run'/'pass' to integers.
    - motion_cat_dict (dict): Dictionary to convert motion categories to integers.
    
    Returns:
    - df (DataFrame): The modified DataFrame with the columns converted to integers.
    """
    # Convert 'play_type' column using RUN_PASS_DICT
    if 'play_type' in df.columns:
        df['play_type'] = df['play_type'].map(RUN_PASS_DICT)
    
    # Convert 'motion_category' column using MOTION_CAT_DICT
    if 'motion_type' in df.columns:
        df['motion_type'] = df['motion_type'].map(MOTION_CAT_DICT)
    
    # Convert 'offenseFormation' column using OFFENSIVE_FORMATION_DICT
    if 'offenseFormation' in df.columns:
        df['offenseFormation'] = df['offenseFormation'].map(OFFENSIVE_FORMATION_DICT)
    
    # Convert boolean columns to integers (False -> 0, True -> 1)
    if 'inMotionAtBallSnap' in df.columns:
        df['inMotionAtBallSnap'] = df['inMotionAtBallSnap'].astype(int)
    if 'isDropback' in df.columns:
        df['isDropback'] = df['isDropback'].astype(int)

    return df


# from sklearn.preprocessing import StandardScaler, MinMaxScaler

# def scale_features(df):
#     # List of numerical features to be scaled
#     numerical_features = ['gameClockSeconds', 'yardsToGo', 'yardsGained', 'expectedPoints', 
#                           'scoreDifferential', 'pre_snap_time_duration', 'gameQuarterWeight', 
#                           'field_position_weight', 'possessionTeamWinProbability']
    
#     # Standardization (Z-score normalization)
#     scaler = StandardScaler()
#     df[numerical_features] = scaler.fit_transform(df[numerical_features])
    
#     # Alternatively, if you want to Min-Max scale (scale between 0 and 1):
#     # scaler = MinMaxScaler()
#     # df[numerical_features] = scaler.fit_transform(df[numerical_features])
    
#     return df