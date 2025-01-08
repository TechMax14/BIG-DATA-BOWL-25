import pandas as pd

def get_pass_plays(plays_df):
    """
    Returns a DataFrame with gameId, playId, and play_type ('pass') for pass plays 
    in the specified week.
    """
    df = plays_df
    # Filter for pass plays based on passResult column (complete, incomplete, intercepted)
    pass_plays = df[df['passResult'].isin(['C', 'I', 'IN'])]
    
    # Extract unique gameId and playId combinations and add play_type column
    pass_plays = pass_plays[['gameId', 'playId']].drop_duplicates()
    pass_plays['play_type'] = 'pass'
    
    # INFO statement about the number of unique pass plays
    print(f"INFO: Found {pass_plays.shape[0]} unique PASS plays...")
    
    return pass_plays


def get_run_plays(player_plays_df):
    """
    Returns a DataFrame with gameId, playId, and play_type ('run') for run plays 
    (hadRushAttempt = 1) in the specified week.
    """

    # Filter for the specified week
    df = player_plays_df
    
    # Filter for run plays based on hadRushAttempt = 1
    run_plays = df[df['hadRushAttempt'] == 1]
    
    # Extract unique gameId and playId combinations and add play_type column
    run_plays = run_plays[['gameId', 'playId']].drop_duplicates()
    run_plays['play_type'] = 'run'
    
    # INFO statement about the number of unique run plays
    print(f"INFO: Found {run_plays.shape[0]} unique RUN plays...")
    
    return run_plays


def aggregate_play_types(plays_df, player_play_df, games_df):
    """
    Combines pass and run plays into a single DataFrame with gameId, playId, play_type, and week.

    Args:
        plays_df (DataFrame): DataFrame containing play information, including passResult.
        player_plays_df (DataFrame): DataFrame containing player-level play information, including hadRushAttempt.
        games_df (DataFrame): DataFrame containing game-level information, including week.

    Returns:
        DataFrame: A combined DataFrame with gameId, playId, play_type, and week.
    """
    print(f"INFO: [ START OF DATA LOADING]")
    print(f"INFO: Filtering for run and pass plays...")

    # Get pass plays
    pass_plays = get_pass_plays(plays_df)
    
    # Get run plays
    run_plays = get_run_plays(player_play_df)
    
    # Combine pass and run plays into a single DataFrame
    all_plays = pd.concat([pass_plays, run_plays], ignore_index=True)
    
    # Merge with games_df to include the week column
    all_plays = all_plays.merge(games_df[['gameId', 'week']], on='gameId', how='left')
    
    print(f"INFO: Combining run-pass dataframes...")

    # INFO statement about the total number of unique plays
    print(f"INFO: Combined DataFrame contains {all_plays.shape[0]} unique plays (pass and run), with week column added.")
    
    return all_plays


def aggregate_play_level_features(df, fps_df, plays_df):
    """
    Merges play-level features from fps_df into the aggregated play types DataFrame.

    Args:
        df (DataFrame): The DataFrame containing gameId, playId, play_type, and week.
        fps_df (DataFrame): The DataFrame containing play-level features to merge.

    Returns:
        DataFrame: The merged DataFrame with additional play-level features.
    """
    print(f"INFO: Merging FPS df for play level features.")

    fps_columns = [
        'gameId', 'playId', 'quarter', 'gameClockSeconds', 'gameQuarterWeight',
        'down', 'yardsToGo', 'yardsGained', 'expectedPoints', 'expectedPointsAdded',
        'absoluteYardlineNumber', 'offenseFormation', 'inMotionAtBallSnap', 'isDropback', 
        'field_position_weight', 'scoreDifferential', 'playSuccessWeight', 'possessionTeamWinProbability',
        'possessionTeamImpact', 'opponentTeamImpact'    
    ]


    # Merge fps_df with the main df on gameId and playId
    merged_df = df.merge(fps_df[fps_columns], on=['gameId', 'playId'], how='left')

    merged_df = merged_df.merge(plays_df[['gameId', 'playId', 'receiverAlignment']], on=['gameId', 'playId'], how='left')

    # INFO statement about the resulting DataFrame size
    print(f"INFO: Merged DataFrame contains {merged_df.shape[0]} rows and {merged_df.shape[1]} columns.\n")
    
    return merged_df


def final_merge(agg_df, def_features_data, off_features_data):
    """
    Merges three DataFrames (agg_df, def_features, off_features) on gameId and playId.

    Args:
    - agg_df (DataFrame): Aggregated data frame containing play-level or game-level features.
    - def_features (DataFrame): Data frame containing defensive features.
    - off_features (DataFrame): Data frame containing offensive features.

    Returns:
    - merged_df (DataFrame): Data frame with all features from agg_df, def_features, and off_features merged.
    """
    # Merge agg_df and def_features on gameId and playId
    merged_df = pd.merge(agg_df, def_features_data, on=['gameId', 'playId'], how='left')
    
    # Merge the result with off_features on gameId and playId
    merged_df = pd.merge(merged_df, off_features_data, on=['gameId', 'playId'], how='left')
    
    return merged_df