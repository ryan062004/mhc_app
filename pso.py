import numpy as np
from pyswarm import pso
import database
import random

# Define activities
activities = ["Meditation", "Journaling", "Breathing Exercise", "Music", "Walking"]

# Default scores
default_scores = {activity: 5 for activity in activities}

# Load mood feedback and track removed activities
mood_feedback = database.get_mood_feedback()
removed_activities = database.get_removed_activities()

# Ensure feedback is stored as a list
for activity in mood_feedback:
    if not isinstance(mood_feedback[activity], list):
        mood_feedback[activity] = [mood_feedback[activity]]

# Initialize scores
base_scores = default_scores.copy()

# Track activities for removal
bad_activities = set()

def adjust_scores(activity, feedback):
    """Adjust activity scores based on recent mood feedback."""
    recent_feedback = feedback[-3:]  # Focus on last 3 ratings
    avg_mood = sum(recent_feedback) / len(recent_feedback)

    # **Ensure score stays in range**
    avg_mood = max(1, min(10, avg_mood))

    # **Stronger Removal Condition**
    if sum(1 for x in recent_feedback if x <= 2) >= 2:  # Reduce threshold to 2 bad ratings
        bad_activities.add(activity)
        removed_activities[activity] = 7  # Increase cooldown to 7 runs
        return None  # Remove from selection

    # **Apply a Stronger Score Penalty**
    if avg_mood <= 3:
        return max(-10, base_scores[activity] - 15)  # Stronger penalty for low ratings
    elif avg_mood >= 8:
        return base_scores[activity] + 5  # Boost highly-rated activities
    else:
        return base_scores[activity] + (avg_mood - 5) * 0.5  # Moderate scaling


# Adjust scores based on feedback
for activity in activities:
    if activity in mood_feedback and mood_feedback[activity]:
        new_score = adjust_scores(activity, mood_feedback[activity])
        if new_score is not None:
            base_scores[activity] = new_score

# Update cooldown for removed activities
for activity in list(removed_activities.keys()):
    removed_activities[activity] -= 1
    if removed_activities[activity] <= 0:
        del removed_activities[activity]
        base_scores[activity] = 5  # Restore default score

# Remove bad activities from selection
activities = [act for act in activities if act not in bad_activities and act not in removed_activities]
activity_scores = [base_scores[activity] for activity in activities]

# Define PSO bounds
lb = [0] * len(activities)
ub = [1] * len(activities)

def calculate_penalty(activity, feedback):
    """Returns penalty based on average feedback."""
    avg_feedback = sum(feedback) / len(feedback) if feedback else 5
    penalty = max(0, 10 - avg_feedback)  

    # **Extra penalty for activities that were recently removed**
    if activity in removed_activities:
        penalty += 5  

    return penalty


def fitness_function(x):
    last_activities = database.get_last_recommendations()
    total_score = 0

    for i, activity in enumerate(activities):
        feedback = mood_feedback.get(activity, [])
        penalty = calculate_penalty(activity, feedback)
        total_score += x[i] * (-activity_scores[i] - penalty)

    # Ensure at least 2 activities
    selected_count = sum(round(x[i]) for i in range(len(activities)))
    if selected_count < 2:
        return -99999  # Strong penalty
    if selected_count > 3:
        return -5000  # Mild penalty

    # Stronger penalty for repeating activities
    for i in range(len(activities)):
        if activities[i] in last_activities and round(x[i]) == 1:
            total_score -= 10

    return total_score

# Run PSO with optimized parameters
best_solution, _ = pso(fitness_function, lb, ub, swarmsize=50, maxiter=200)

# Convert PSO output to selected activities
best_solution = [round(x) for x in best_solution]
selected_activities = [activities[i] for i in range(len(best_solution)) if best_solution[i] == 1]

# **Ensure at least 2 activities are selected**
if len(selected_activities) < 2:
    sorted_activities = sorted(activities, key=lambda act: -activity_scores[activities.index(act)])
    selected_activities = sorted_activities[:2]

# Save recommendations and updates
database.save_recommendations(selected_activities)
database.save_removed_activities(removed_activities)

print("Recommended Activities:", selected_activities)

# Save mood feedback function
def save_mood_feedback(activity, mood_score):
    """Save mood feedback for a given activity."""
    mood_feedback.setdefault(activity, []).append(mood_score)
    database.save_mood_feedback(activity, mood_score)
    print(f"Feedback for {activity} saved.")
