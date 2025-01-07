import pandas as pd


def filter_for_presnap(week, players_df):
    """
    Preprocesses the tracking data for each unique gameId and playId in the given dataframe.
    Filters for presnap frames and key offensive players.
    """
    tracking_data = pd.read_csv(f'../data/tracking_week_{week}.csv')
    
    total_rows_before = tracking_data.shape[0]
    print(f"INFO: Filtering {total_rows_before} rows of tracking data for pre-snap frames in week {week}...")
    
    all_processed_data = []

     # Filter once for BEFORE_SNAP and SNAP frames
    presnap_tracking_data = tracking_data[tracking_data['frameType'].isin(['BEFORE_SNAP', 'SNAP'])]
    
    # Group by gameId and playId, this is typically more efficient than using iterrows
    grouped_data = presnap_tracking_data.groupby(['gameId', 'playId'])
    
    # Extract the data from each group, if needed (could be expanded based on your analysis needs)
    all_processed_data = [group for _, group in grouped_data]
    
    # Combine all processed data into one DataFrame
    combined_data = pd.concat(all_processed_data, ignore_index=True)

    # Count the number of unique (gameId, playId) pairs
    unique_count = len(combined_data[['gameId', 'playId']].drop_duplicates())

    # Print the total number of rows after processing
    total_rows_after = combined_data.shape[0]
    print(f"INFO: Found {total_rows_after} pre-snap frames of tracking data in week {week}.")
    print(f"INFO: Found {unique_count} plays of tracking data in week {week}.")

    # Call the merge function to add player positions to the combined data
    combined_data_with_positions = merge_players_positions(combined_data, players_df)

    # Return the combined processed data
    return combined_data_with_positions

import pandas as pd

def merge_players_positions(tracking_df, players_df):
    """
    Merges the player position information from player_df into the tracking data (tracking_df).
    
    Args:
    - tracking_df (DataFrame): The tracking data containing player positions (nflId).
    - player_df (DataFrame): The players' data containing nflId and their respective positions.
    
    Returns:
    - DataFrame: The tracking data with an additional column 'position' that has player positions.
    """
    print(f"INFO: Merging player position data into tracking data...")
    
    # Merge the tracking data with the player data on 'nflId'
    merged_df = tracking_df.merge(players_df[['nflId', 'position']], on='nflId', how='left')
    
    # Check for any unmatched 'nflId' (i.e., players without position information)
    unmatched_players = merged_df[merged_df['position'].isna()]
    
    if not unmatched_players.empty:
        print(f"WARNING: Found {unmatched_players.shape[0]} players without position information.")
    
    print(f"INFO: Merged position data into tracking data. New shape: {merged_df.shape}")
    
    return merged_df
