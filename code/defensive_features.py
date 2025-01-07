import time
import pandas as pd

def get_defenders_position(df, defensive_positions):
    """
    Returns the positions (x_clean, y_clean) of the defensive players.
    
    Args:
    - df (DataFrame): DataFrame containing tracking data for a specific play.
    - defensive_positions (list): List of defensive positions.
    
    Returns:
    - defenders_df (DataFrame): DataFrame with x_clean and y_clean coordinates of defensive players.
    """
    defenders_df = df[df['position'].isin(defensive_positions)][['gameId', 'playId', 'x_clean', 'y_clean', 'position']]
    return defenders_df


def get_box_dimensions(ball_x, ball_y, box_depth=7, box_width=14):
    """
    Defines a box region starting at the ball's x_clean position and extending upfield (along x-axis_clean)
    and as wide as the ball's y_clean position + box_width/2 and - box_width/2 (along y-axis_clean).
    
    Args:
    - ball_x (float): The x_clean coordinate (upfield) of the ball at SNAP.
    - ball_y (float): The y_clean coordinate (sideways) of the ball at SNAP.
    - box_depth (float): Depth of the box (how far upfield), default is 7 yards.
    - box_width (float): Width of the box (side-to-side from the ball), default is 14 yards (7 to left and right).
    
    Returns:
    - tuple: (box_left, box_right, box_top, box_bottom)
    """
    box_depth *= 100  # Scale depth by 100
    box_width *= 100  # Scale width by 100

    box_left = ball_y - (box_width / 2)   # For the y_clean axis (left-right)
    box_right = ball_y + (box_width / 2)  # For the y_clean axis (left-right)
    box_top = ball_x                      # For the x_clean axis (up-down), box starts at ball's x_clean position
    box_bottom = ball_x + box_depth       # Box extends upfield (depth)
    
    return box_left, box_right, box_top, box_bottom


def check_defenders_in_box(defenders_df, box_left, box_right, box_top, box_bottom):
    """
    Check which defensive players are inside the defined box.
    
    Args:
    - defenders_df (DataFrame): DataFrame containing the positions (x_clean, y_clean) of the defensive players.
    - box_left (float): The left boundary of the box (y_clean axis).
    - box_right (float): The right boundary of the box (y_clean axis).
    - box_top (float): The top boundary of the box (x_clean axis).
    - box_bottom (float): The bottom boundary of the box (x_clean axis).
    
    Returns:
    - defenders_in_box (DataFrame): A filtered DataFrame with only the defenders inside the box.
    """
    defenders_in_box = defenders_df[
        (defenders_df['x_clean'] >= box_top) & (defenders_df['x_clean'] <= box_bottom) &  # x_clean axis check (upfield)
        (defenders_df['y_clean'] >= box_left) & (defenders_df['y_clean'] <= box_right)  # y_clean axis check (side-to-side)
    ]
    
    return defenders_in_box


def get_defensive_mismatches(df):
    """
    Identifies defensive mismatches by mapping player names and positions,
    checks for mismatches between defenders and their assigned coverage matchups,
    and returns a new DataFrame with a count of mismatches for each gameId/playId.
    
    Args:
    - df (DataFrame): The play-level DataFrame containing tracking and play data.
    - players_df (DataFrame): The players DataFrame containing player information like name and position.
    - player_play_df (DataFrame): The player-play DataFrame containing information on the defensive coverage matchups.
    
    Returns:
    - df (DataFrame): The input DataFrame with additional columns: 'isMismatch' (individual mismatch flag) and 'mismatchFound' (count of mismatches).
    """
    print(f"INFO: Identifying defensive mismatches...")
    
    # Step 2: Identify mismatches based on defender position and their primary coverage matchup
    mismatch_positions = {
        'CB': ['TE', 'RB'],    # CBs usually struggle against TEs and RBs
        'DB': ['TE', 'RB'],    # General DBs (CBs and Safeties) may struggle against TEs, RBs
        'ILB': ['WR', 'RB'],   # ILBs may struggle with WRs, TEs, and RBs in passing routes
        'OLB': ['WR', 'RB'],   # OLBs may struggle with WRs, TEs, and RBs in passing routes
        'MLB': ['WR', 'RB'],   # MLBs (Middle LBs) also may struggle with WRs, TEs, and RBs
        'LB': ['WR', 'RB'],    # General LB struggles with WRs, TEs, and RBs
        'FS': ['TE', 'RB'],    # FS (Free Safeties) may struggle with WRs and fast RBs
        'SS': ['TE', 'RB']     # SS (Strong Safeties) may struggle with WRs, TEs, and RBs
    }
    
    # Step 3: Apply the mismatch logic
    df['isMismatch'] = df.apply(
        lambda row: 1 if row['primaryCoverageMatchupPosition'] in mismatch_positions.get(row['playerPosition'], []) else 0,
        axis=1
    )
    
        # Group by gameId and playId and calculate the sum of mismatches for each play
    mismatch_counts = df.groupby(['gameId', 'playId'])['isMismatch'].sum().reset_index()
    mismatch_counts.rename(columns={'isMismatch': 'mismatchFound'}, inplace=True)
    
    return mismatch_counts


def extract_defenders_with_matchups(df):
    """
    Identifies defensive mismatches by mapping player names and positions,
    checks for mismatches between defenders and their assigned coverage matchups,
    and returns a new DataFrame with a count of mismatches for each gameId/playId.
    
    Args:
    - df (DataFrame): The play-level DataFrame containing tracking and play data.
    - players_df (DataFrame): The players DataFrame containing player information like name and position.
    - player_play_df (DataFrame): The player-play DataFrame containing information on the defensive coverage matchups.
    
    Returns:
    - df (DataFrame): The input DataFrame with additional columns: 'isMismatch' (individual mismatch flag) and 'mismatchFound' (count of mismatches).
    """
    print(f"INFO: Extracting defenders with primary matchups...")

    # Filter out only defensive players with a primary matchup
    defenders = df[df['pff_primaryDefensiveCoverageMatchupNflId'].notna()]
    
    # Add the necessary columns to the DataFrame
    df['defenderName'] = defenders['playerName']
    df['defenderPosition'] = defenders['playerPosition']
    df['primaryCoverageMatchupName'] = defenders['primaryCoverageMatchupName']
    df['primaryCoverageMatchupPosition'] = defenders['primaryCoverageMatchupPosition']
    
    return df

def merge_player_play_data(df, player_play_df):
    """Merges the filtered player_play_df with the main df to get nflId and matchup information."""
    df_filtered = player_play_df[(player_play_df['gameId'].isin(df['gameId'])) & 
                                 (player_play_df['playId'].isin(df['playId']))].copy()
    
    return df.merge(df_filtered[['gameId', 'playId', 'nflId', 'pff_primaryDefensiveCoverageMatchupNflId', 'pff_secondaryDefensiveCoverageMatchupNflId']],
                    on=['gameId', 'playId'], how='left')

def map_player_names_positions(df, players_df):
    """Maps player names and positions to the DataFrame."""
    nflId_to_displayName = players_df.set_index('nflId')['displayName'].to_dict()
    nflId_to_position = players_df.set_index('nflId')['position'].to_dict()

    df['playerName'] = df['nflId'].map(nflId_to_displayName)
    df['playerPosition'] = df['nflId'].map(nflId_to_position)

    # Map coverage matchups
    df['primaryCoverageMatchupName'] = df['pff_primaryDefensiveCoverageMatchupNflId'].map(nflId_to_displayName)
    df['primaryCoverageMatchupPosition'] = df['pff_primaryDefensiveCoverageMatchupNflId'].map(nflId_to_position)
    df['secondaryCoverageMatchupName'] = df['pff_secondaryDefensiveCoverageMatchupNflId'].map(nflId_to_displayName)
    df['secondaryCoverageMatchupPosition'] = df['pff_secondaryDefensiveCoverageMatchupNflId'].map(nflId_to_position)

    return df





def get_defensive_features(df_clean, agg_df, players_df, player_play_df):
    """
    Returns a DataFrame with gameId, playId, players_in_box_count, and mismatchFound for each play.
    
    Args:
    - df (DataFrame): The DataFrame containing tracking data at the SNAP.
    - players_df (DataFrame): DataFrame containing player information (names, positions).
    - player_play_df (DataFrame): DataFrame containing player-play data with defensive coverage matchups.
    
    Returns:
    - result_df (DataFrame): DataFrame containing `gameId`, `playId`, `players_in_box_count`, and `mismatchFound`.
    """
    print(f"INFO: Processing defensive features...")
    start_time = time.time()

    # Define the defensive positions
    defensive_positions = ['DE', 'NT', 'DT', 'ILB', 'OLB', 'MLB', 'LB', 'DB', 'CB', 'FS', 'SS']
    
    # Group by gameId and playId to process each unique play
    grouped = df_clean[df_clean['frameType'] == 'SNAP'].groupby(['gameId', 'playId'])
    
    box_results = []  # To store box-related data
    mismatch_results = []  # To store mismatch-related data
    
    print(f"INFO: Idenitfying a count of defensive players in the box pre-snap...")

    # Process each group (gameId, playId)
    for (gameId, playId), group in grouped:
        # Get the football position (displayName == 'football')
        football_row = group[group['displayName'] == 'football']
        if football_row.empty:
            continue  # Skip if no football data
        
        # Get ball position using x_clean and y_clean
        ball_x, ball_y = football_row[['x_clean', 'y_clean']].values[0]
        
        # Get the defenders' positions using x_clean and y_clean
        defenders_df = get_defenders_position(group, defensive_positions)
        
        # Define the box dimensions around the football using x_clean and y_clean
        box_left, box_right, box_top, box_bottom = get_box_dimensions(ball_x, ball_y)
        
        # Check if defenders are inside the box using x_clean and y_clean
        defenders_in_box = check_defenders_in_box(defenders_df, box_left, box_right, box_top, box_bottom)
        
        # Append the result for this gameId, playId
        box_results.append({
            'gameId': gameId,
            'playId': playId,
            'players_in_box_count': len(defenders_in_box)
        })
    
    # Convert box results to a DataFrame
    box_result_df = pd.DataFrame(box_results)
    
    # Add mismatch-related features
    df_merge = merge_player_play_data(agg_df, player_play_df)
    df_map = map_player_names_positions(df_merge, players_df)
    df_dMatchups = extract_defenders_with_matchups(df_map)
    mismatch_counts = get_defensive_mismatches(df_dMatchups)
    
    # Merge mismatch counts into the final box results
    result_df = box_result_df.merge(
        mismatch_counts[['gameId', 'playId', 'mismatchFound']],
        on=['gameId', 'playId'],
        how='left'
    )

    end_time = time.time()
    duration = end_time - start_time
    print(f"INFO: Defensive Feature functions ran in {duration:.4f} seconds")

    return result_df




