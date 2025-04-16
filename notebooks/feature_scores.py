import numpy as np
from datetime import datetime

def calculate_weather_score(temp, precipitation, season):
    # Handle None or NaN values
    if temp is None:
        temp = 18  # Default comfortable temperature
    if precipitation is None: 
        precipitation = 0  # Assume no rain if missing
    if season is None: 
        season = "Summer"  # Default to summer if missing

    # Normalize temperature: best range is 15-22°C
    temp_score = max(0, min(1, 1 - abs(temp - 18) / 10))

    # Precipitation penalty
    precipitation_score = max(0, 1 - precipitation / 100)

    # Season effect (summer/fall is better than winter)
    season_bonus = {"Spring": 0.8, "Summer": 1.0, "Fall": 0.9, "Winter": 0.6}
    
    score = (temp_score * 0.5 + precipitation_score * 0.3 + season_bonus.get(season, 0.7) * 0.2)
    return round(score, 2)


def calculate_competition_score(competition, stage=None):
    base_scores = {
        "Bundesliga": 0.4,
        "Conference League": 0.4,
        "DFB Pokal": 0.5,
        "Europa League": 0.6,
        "Champions League": 0.7
    }
    stage_multiplier = {
        "Quarterfinal": 1.2,
        "Semifinal": 1.3,
        "Final": 1.4
    }
    base = base_scores.get(competition, 0.5)  # default to Bundesliga if unknown
    multiplier = stage_multiplier.get(stage, 1.0) if stage else 1.0
    score = base * multiplier
    return round(min(score, 1.0), 2)  # cap at 1.0 for normalization

low_comp = calculate_competition_score("Bundesliga")
high_comp = calculate_competition_score("Champions League", "Semifinal")

print(low_comp,high_comp)


def calculate_date_score(date_str, time_str, is_holiday=False, competing_event=False, matchday=14):
    """
    date_input: '2022-08-05' or pandas Timestamp
    time_str: '20:30:00.0000000'
    """
    # Handle Timestamp or string
   
    date_obj = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")

    day_name = date_obj.strftime("%A")  # e.g., 'Friday', 'Saturday'
    time_formatted = time_str[:5]

    score_map = {
        ("Saturday", "15:30"): 1.0,
        ("Saturday", "18:30"): 0.95,
        ("Friday", "20:30"): 0.9,
        ("Sunday", "15:30"): 0.8,
        ("Sunday", "17:30"): 0.7,
        ("Sunday", "19:30"): 0.6
    }
    base_score = score_map.get((day_name, time_formatted), 0.75)

    if is_holiday:
        base_score = min(base_score + 0.1, 1.1)
    if competing_event:
        base_score = max(base_score - 0.1, 0.0)
    if matchday <= 5 or matchday >= 30:
        base_score += 0.05

    return round(base_score, 3)

def calculate_team_score(members, form_string, home_pos, opponent_pos, is_derby=False):
    score = (
        club_member_score(members) * 0.5 +
        form_score(form_string) * 0.25 +
        table_score(home_pos, opponent_pos) * 0.25
    )
    if is_derby:
        score*= 1.2
    return score

def club_member_score(members):
    # Normalize between 0 and 1 (assume min 10k, max 150k members in Bundesliga)
    return min(max((members - 10000) / (400000 - 1000), 0), 1)

def form_score(form_string):
    base_points = {'W': 3, 'D': 1, 'L': 0}
    weights = [1, 1.5, 2, 2.5, 3]  # Adjusted weights
    score = 0
    max_score = sum([3 * w for w in weights])  # Max possible for normalization
    
    for i, result in enumerate(form_string):
        score += base_points[result] * weights[i]
    
    return score / max_score  # Normalized between 0 and 1

def table_score(home_pos, opponent_pos):
    # Define score ranges based on position groups
    position_score = {
        (1, 5): 1.0,   
        (6, 10): 0.75,  
        (11, 15): 0.5,  
        (16, 18): 0.25  
    }

    # Check the ranges for both home and opponent positions
    home_score = get_position_score(home_pos, position_score)
    opponent_score = get_position_score(opponent_pos, position_score)

    # Return average of home and opponent scores
    return (home_score + opponent_score) / 2

def get_position_score(position, position_score):
    # Find the score range for the given position
    for range_tuple, score in position_score.items():
        if range_tuple[0] <= position <= range_tuple[1]:
            return score
    return 0  # If position is out of bounds, return 0



# Example: Weighted sum + random noise
def generate_clicks(row):
    base_clicks = 1000
    weighted_sum = (
        row["DateScore"] * 0.2 +
        row["OpponentScore"] * 0.3 +
        row["HomeTeamScore"] * 0.2 +
        row["WeatherScore"] * 0.2 +
        row["CompetitionScore"] * 0.1
    )
    noise = np.random.normal(0, 200)  # Add randomness
    return int(base_clicks + weighted_sum * 4000 + noise)

