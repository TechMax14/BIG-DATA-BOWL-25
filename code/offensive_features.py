import pandas as pd
import time
from joblib import Parallel, delayed
import pandas as pd
import time

def process_motion_frames(data, speed_minimum_for_motion=1.5, speed_threshold=0.5):
    """
    Detects frames corresponding to local minima, local maxima, and motion segments for a given players speed.
    Function: reads in tracking data for a player and returns motion frames if the players 's' meets criteria.

    Args:
    - data (DataFrame): Data containing speed ('s') and frame identifiers ('frameId') for a player.
    - speed_minimum_for_motion (float): Minimum speed to classify as motion (default=1.5).
    - speed_threshold (float): Speed threshold to end a motion segment (default=0.5).

    Returns:
    - dict: A dictionary with:
        - "local_maxima_frames": Frames corresponding to local maxima of speed.
        - "local_minima_frames": Frames corresponding to local minima of speed.
        - "motion_frames": Frames corresponding to motion segments between minima and maxima.
    """
    # Ensure speed is in float64 type and handle missing values (if any)
    if data['s'].dtype != 'float64':  # Convert if it's not the correct type
        data['s'] = data['s'].astype('float64')
    data['s'] = data['s'].fillna(0)  # Replace NaNs with 0 (or another suitable value)

    maxima_frames = []
    minima_frames = []
    motion_frames = []

    # Ensure the 's' and 'frameId' columns exist
    if 's' not in data.columns or 'frameId' not in data.columns:
        raise KeyError("'s' or 'frameId' column missing in data")
    # Using pandas built-in vectorized operations to calculate maxima/minima
    speed = data['s']
    frame_ids = data['frameId']
    
    # Create shifted series to detect local maxima and minima
    prev_speed = speed.shift(1)
    next_speed = speed.shift(-1)

    # Conditions for detecting minima and maxima
    is_local_minima = (speed == 0) & (speed.shift(1) > 0) & (speed.shift(-1) > 0)
    is_local_maxima = (speed >= prev_speed) & (speed >= next_speed) & (speed >= speed_minimum_for_motion)

    minima_frames = frame_ids[is_local_minima].tolist()
    maxima_frames = frame_ids[is_local_maxima].tolist()
    
    total_frames = len(data)

    # Special handling for last frame
    last_frame_idx = total_frames - 1
    last_frame_speed = data.iloc[last_frame_idx]['s']
    second_last_frame_speed = data.iloc[last_frame_idx - 1]['s']
    if last_frame_speed >= second_last_frame_speed and last_frame_speed >= speed_minimum_for_motion:
        maxima_frames.append(data.iloc[last_frame_idx]['frameId'])

    # Motion segments: From minima to maxima, then to below threshold or last frame
    minima_idx = 0
    maxima_idx = 0
    motion_segments = []

    while minima_idx < len(minima_frames) and maxima_idx < len(maxima_frames):
        minima_frame = minima_frames[minima_idx]
        maxima_frame = maxima_frames[maxima_idx]

        segment_frames = frame_ids[(frame_ids >= minima_frame) & (frame_ids <= maxima_frame)].tolist()

        # After maxima, detect frames with speed below threshold
        frames_after_maxima = data[data['frameId'] > maxima_frame]
        stop_frame = frames_after_maxima[frames_after_maxima['s'] < speed_threshold]
        
        stop_frame = stop_frame['frameId'].min() if not stop_frame.empty else frame_ids.iloc[-1]
        segment_frames += frame_ids[(frame_ids > maxima_frame) & (frame_ids <= stop_frame)].tolist()

        motion_segments.append(segment_frames)
        minima_idx += 1
        maxima_idx += 1

    motion_frames = sorted(set([frame for segment in motion_segments for frame in segment]))

    return {
        "local_maxima_frames": maxima_frames,
        "local_minima_frames": minima_frames,
        "motion_frames": motion_frames
    }


def classify_motion_type(player_motion_results, last_frame_in_data):
    """
    Classifies the type of motion based on the players' motion frames.
    
    'no motion': 0 players found in the play with motion frames           
    'single shift': a single player motions and stops before the ball is snapped
    'single motion': a single player is in motion when the ball is snapped (pre-snap motion)
    'single combined': a single player shifts, stops, then motions as the ball is snapped
    'multi shift': multiple players shift during pre-snap and stop before the ball is snapped
    'multi motion': multiple players in motion
    'multi combined': multiple players shift and a player motions at ball snap

    Args:
    - player_motion_results (dict): Dictionary mapping player IDs to lists of motion frames.
    - last_frame_in_data (int): The ID of the last frame in the play.

    Returns:
    - tuple: A tuple containing:
        - motion_type (str): The type of motion ('no motion', 'single shift', 'single motion', 'single combined', or 'multi motion').
        - players_with_motion (int): The count of players with motion.
        - players_motion_ends_at_last_frame (int): The count of players whose motion ends at the last frame.
    """
    motion_types = []
    players_with_motion = 0
    players_motion_ends_at_last_frame = 0
    player_last_frame_check = {}

    # Determine players with motion in a vectorized manner
    players_with_motion = {player: len(frames) > 0 for player, frames in player_motion_results.items()}
    players_motion_ends_at_last_frame = {
        player: frames[-1] == last_frame_in_data if frames else False for player, frames in player_motion_results.items()
    }

    motion_type = 'no motion'
    if sum(players_with_motion.values()) == 1:
        # Check motion type logic based on 1 player
        single_player = next(player for player, frames in player_motion_results.items() if len(frames) > 0)
        motion_frames = player_motion_results[single_player]
        gaps = [i for i in range(1, len(motion_frames)) if motion_frames[i] - motion_frames[i - 1] > 1]
        if gaps and motion_frames[-1] == last_frame_in_data:
            motion_type = "single combined"
        elif players_motion_ends_at_last_frame.get(single_player, False):
            motion_type = "single motion"
        else:
            motion_type = "single shift"
    elif sum(players_with_motion.values()) > 1:
        motion_type = 'multi motion'  # Simplified; you can adjust this logic

    return motion_type, sum(players_with_motion.values()), sum(players_motion_ends_at_last_frame.values())



def count_players_with_motion(player_motion_results, last_frame_in_data):
    """
    Counts the number of players with motion frames > 1 and those whose motion ends at the last frame.

    Args:
    - player_motion_results (dict): Dictionary mapping player IDs to lists of motion frames.
    - last_frame_in_data (int): The ID of the last frame in the play.

    Returns:
    - tuple: A tuple containing:
        - players_with_motion (int): The number of players with motion.
        - players_motion_ends_at_last_frame (int): The number of players whose motion ends at the last frame.
        - player_last_frame_check (dict): A dictionary mapping player IDs to whether their motion ends at the last frame.
    """
    players_with_motion = 0
    players_motion_ends_at_last_frame = 0
    player_last_frame_check = {}

    for player, motion_frames in player_motion_results.items():
        if motion_frames:
            players_with_motion += 1
            motion_ends_at_last_frame = motion_frames[-1] == last_frame_in_data
            if motion_ends_at_last_frame:
                players_motion_ends_at_last_frame += 1
            player_last_frame_check[player] = motion_ends_at_last_frame
        else:
            player_last_frame_check[player] = False

    return players_with_motion, players_motion_ends_at_last_frame, player_last_frame_check








def count_pre_snap_frames(group):
    """
    Counts the number of pre-snap frames for a given playId.
    """
    return len(group)


def get_time_to_snap(group):
    """
    Calculate the time difference (in seconds) from the first frame to the ball snap.
    If no BEFORE_SNAP frame exists, default time_to_snap to 0.1.
    """
    # Extract the 'time' values for the group
    before_snap_frames = group[group['frameType'] == 'BEFORE_SNAP']
    ball_snap_data = group[group['frameType'] == 'SNAP']  # Use frameType == 'SNAP'

    if not before_snap_frames.empty:
        # Get the first frame timestamp
        first_frame_time = pd.to_datetime(before_snap_frames['time'].min())
    else:
        # No BEFORE_SNAP frames; assign default first frame timestamp (arbitrary)
        first_frame_time = None

    if not ball_snap_data.empty:
        snap_time = pd.to_datetime(ball_snap_data['time'].iloc[0])  # Ball snap timestamp
        
        if first_frame_time is not None:
            # Calculate the time difference in seconds
            time_to_snap = (snap_time - first_frame_time).total_seconds()
        else:
            # No BEFORE_SNAP frame, set default value
            time_to_snap = 0.1
    else:
        # If no SNAP event exists, return default value
        time_to_snap = 0.1

    return time_to_snap







def get_offensive_features(opt_df_clean, player_play_df):
    start_time = time.time()
    
    # Initialize result storage
    game_ids = []
    play_ids = []
    motion_types = []
    motion_player_counts = []
    pre_snap_frame_counts = [] 
    pre_snap_time_durations = []

    print(f"INFO: Extracting offensive features: motion categorization and motion player count...")

    # Function to process each group (game-play pair)
    def process_group(group):
        """
        Process a single group (game-play pair) to extract motion features like motion type,
        motion player count, and pre-snap time duration.

        Args:
            group (pd.DataFrame): The group (subset of the original DataFrame) for a single game-play pair.

        Returns:
            dict: A dictionary containing the processed features for the current play.
        """
        # Use the 'gameId' and 'playId' directly from the group, since group is a DataFrame.
        game_id, play_id = group.iloc[0][['gameId', 'playId']] 

        # Now proceed with the rest of the function as usual...
        player_motion_results = {}
        for player_name, player_data in group.groupby('displayName'):
            results = process_motion_frames(player_data, speed_minimum_for_motion=1.5, speed_threshold=0.5)
            player_motion_results[player_name] = results['motion_frames']
        
        last_frame_in_data = group['frameId'].max()

        motion_type, players_with_motion, players_motion_ends_at_last_frame = classify_motion_type(player_motion_results, last_frame_in_data)

        pre_snap_time_duration = get_time_to_snap(group)

        return {
            'gameId': game_id,
            'playId': play_id,
            'motion_type': motion_type,
            'motion_player_count': players_with_motion,
            'pre_snap_time_duration': pre_snap_time_duration,
        }

    
    # Step 1: Parallelize the processing of each game-play group
    result_list = Parallel(n_jobs=-1)(delayed(process_group)(group) for _, group in opt_df_clean.groupby(['gameId', 'playId']))

    # Step 2: Convert the result list to a DataFrame
    result_df = pd.DataFrame(result_list)

    print(f"INFO: Calculating time from huddle break to snap...")

    # Step 3: Return the result DataFrame
    end_time = time.time()
    duration = end_time - start_time
    print(f"INFO: Offensive Feature functions ran in {duration:.4f} seconds")

    return result_df