from flask import Flask, render_template, request, redirect, url_for, flash, session
import datetime
from database import initialize_db, add_workout, get_all_workouts, get_users, add_user
from openai_integration import query_openai
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key for production

def markdown_bold(text):
    """
    Convert markdown-style bold (i.e., **text**) into HTML <strong> tags.
    """
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

# Register the custom filter with Jinja
app.jinja_env.filters['markdown_bold'] = markdown_bold

# Initialize the database when the app starts
initialize_db()

# ------------------------------
# Index Route & User Selection
# ------------------------------
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_user = request.form.get("user_select")
        new_user = request.form.get("new_user")
        if selected_user and selected_user != "new":
            # Convert the selected user id to an integer and store in session.
            session["user_id"] = int(selected_user)
            # Look up the username from the users list.
            users = get_users()  # This returns a list of dictionaries, e.g., [{"id": 1, "username": "Alice"}, ...]
            for user in users:
                if user["id"] == int(selected_user):
                    session["user_name"] = user["username"]
                    break
        elif new_user:
            user_id = add_user(new_user)
            session["user_id"] = user_id
            session["user_name"] = new_user
        else:
            flash("Please select an existing user or enter a new username.")
            return redirect(url_for('index'))
        return redirect(url_for('index'))
    else:
        users = get_users()  # Returns list of users as dictionaries
        return render_template("index_v2.html", users=users, current_user=session.get("user_id"))

# ------------------------------
# Gym Workout Routes
# ------------------------------
@app.route('/record', methods=['GET', 'POST'])
def record_workout():
    if request.method == 'POST':
        date_input = request.form.get('date')
        if not date_input:
            date_input = datetime.date.today().isoformat()
        # Gym workout form fields:
        muscle_group = request.form.get('muscle_group')
        exercise = request.form.get('exercise')
        weight = request.form.get('weight')
        sets = request.form.get('sets')
        reps = request.form.get('reps')
        if muscle_group and exercise and weight and sets and reps:
            details = {
                "muscle_group": muscle_group,
                "exercise": exercise,
                "weight": weight,
                "sets": sets,
                "reps": reps
            }
            # Associate this workout with the current user
            add_workout(date_input, session["user_id"], "gym", details)
            flash('Gym workout recorded successfully.')
        else:
            flash('Missing fields for gym workout.')
        return redirect(url_for('index'))
    return render_template('record.html')

@app.route('/history')
def history():
    workouts = get_all_workouts()
    # (You might later choose to filter history by user for a combined history.)
    return render_template('history.html', workouts=workouts)

@app.route('/suggest')
def suggest():
    # Gym workout suggestions (filter by current user)
    workouts = get_all_workouts()
    workouts = [w for w in workouts if w["user_id"] == session["user_id"]]
    gym_workouts = [w for w in workouts if w["workout_type"] == "gym"]
    recent_workouts = gym_workouts[:5]
    history_text = "\n".join([
        f"Date: {w['date']}, Muscle Group: {w['details'].get('muscle_group','')}, "
        f"Exercise: {w['details'].get('exercise','')}, Weight: {w['details'].get('weight','')}, "
        f"Sets: {w['details'].get('sets','')}, Reps: {w['details'].get('reps','')}"
        for w in recent_workouts
    ])
    if gym_workouts:
        max_date = max(w["date"] for w in gym_workouts)
        last_workouts = [w for w in gym_workouts if w["date"] == max_date]
        records = []
        for w in last_workouts:
            records.append({
                "muscle_group": w["details"].get("muscle_group", ""),
                "exercise": w["details"].get("exercise", ""),
                "weight": w["details"].get("weight", ""),
                "sets": w["details"].get("sets", ""),
                "reps": w["details"].get("reps", "")
            })
        last_session = {"date": max_date, "records": records}
    else:
        last_session = None

    prompt = (
        "Based on my recent gym workout history focusing on strength training.\n"
        "Please suggest a gym workout plan for today, including warm-up and main exercises. "
        "Here is my gym workout history:\n"
        f"{history_text}\n\n"
        "Now, based on the above, please provide today's gym workout program."
    )
    suggestion = query_openai(prompt)
    return render_template('suggest.html', suggestion=suggestion, last_session=last_session)

@app.route('/record_actual', methods=['POST'])
def record_actual():
    today = datetime.date.today().isoformat()
    for i in range(5):
        muscle_group = request.form.get(f'body_part_{i}')
        exercise_name = request.form.get(f'exercise_{i}')
        weight = request.form.get(f'max_weight_{i}')
        sets = request.form.get(f'sets_{i}')
        reps = request.form.get(f'reps_{i}')
        if muscle_group and exercise_name and weight and sets and reps:
            details = {
                "muscle_group": muscle_group,
                "exercise": exercise_name,
                "weight": weight,
                "sets": sets,
                "reps": reps
            }
            add_workout(today, session["user_id"], "gym", details)
    flash("Gym workout recorded successfully.")
    return redirect(url_for('index'))

@app.route('/gym_suggest')
def gym_suggest():
    workouts = get_all_workouts()
    workouts = [w for w in workouts if w["user_id"] == session["user_id"]]
    gym_workouts = [w for w in workouts if w["workout_type"] == "gym"]
    recent_workouts = gym_workouts[:5]
    history_text = "\n".join([
        f"Date: {w['date']}, Muscle Group: {w['details'].get('muscle_group','')}, "
        f"Exercise: {w['details'].get('exercise','')}, Weight: {w['details'].get('weight','')}, "
        f"Sets: {w['details'].get('sets','')}, Reps: {w['details'].get('reps','')}"
        for w in recent_workouts
    ])
    if gym_workouts:
        max_date = max(w["date"] for w in gym_workouts)
        last_workouts = [w for w in gym_workouts if w["date"] == max_date]
        records = []
        for w in last_workouts:
            records.append({
                "muscle_group": w["details"].get("muscle_group", ""),
                "exercise": w["details"].get("exercise", ""),
                "weight": w["details"].get("weight", ""),
                "sets": w["details"].get("sets", ""),
                "reps": w["details"].get("reps", "")
            })
        last_session = {"date": max_date, "records": records}
    else:
        last_session = None

    prompt = (
         "Based on my recent gym workout history focusing on strength training.\n"
        "Please suggest a workout plan for today, starting with warm-up and following with the main exercises. "
        "Keep in mind a high-intensity level. "
        "Suggest 5 min warm-up & stretching exercises relevant to the main exercises. "
        "Include exactly 5 types of exercises in the main exercises, "
        "Each exercise can be from 3 to 5 sets. "
        "The exercises must be limited to 2 body parts per session, for example - chest and back, or shoulders and legs. "
        "Do not suggest the same body parts that were trained in the most recent history (see the dates). Suggest those that I haven't trained in a while. "
        "When choosing weight for the exercise - take the weight I have done with this exercise in the last historic session and add 1-3 kg. "
        "Give me suggestion in the following format where every set starts from the new line. "
        "In the beginning, tell me briefly and without too much details what I trained last time, and where the focus of today's training should be. "
        "Then give me warm-up exercises. The title saying Warm-up & Stretching must be in bold font."
        "Keep one blank line between warm-up and main exercises. "
        "The title saying Main Exercises must be in bold font. "
        "Then give me today’s program. Indicate which part of the body it works, max number of sets, max number of repetitions and max weight. "
        "List main exercises as single line for each out of 5. For example: Chest - Bench press: ramp to 80kg, 6 reps, 5 sets\n\n"
        "Here is my workout history:\n"
        f"{history_text}\n\n"
        "Now, based on the above, please provide today's workout program."
    )
    suggestion = query_openai(prompt)
    return render_template('gym_suggest.html', suggestion=suggestion, last_session=last_session)

@app.route('/gym_history')
def gym_history():
    if "user_id" not in session:
        flash("Please select a user first.")
        return redirect(url_for('index'))
    workouts = get_all_workouts()
    gym_workouts = [w for w in workouts if w["workout_type"] == "gym" and w["user_id"] == session["user_id"]]
    return render_template('gym_history.html', workouts=gym_workouts)

# ------------------------------
# WOD (CrossFit) Routes
# ------------------------------
@app.route('/wod_suggest')
def wod_suggest():
    if "user_id" not in session:
        flash("Please select a user first.")
        return redirect(url_for('index'))
    workouts = get_all_workouts()
    wod_workouts = [w for w in workouts if w["workout_type"] == "wod" and w["user_id"] == session["user_id"]]
    
    # Get the last (most recent) saved WOD by sorting by id (descending)
    if wod_workouts:
        sorted_wods = sorted(wod_workouts, key=lambda w: w["id"], reverse=True)
        last_wod = sorted_wods[0]
    else:
        last_wod = None

    if last_wod:
        history_text = (
            f"Date: {last_wod['date']}, "
            f"Block: {last_wod['details'].get('block', '')}, "
            f"Exercises: {last_wod['details'].get('exercises', '')}, "
            f"Time: {last_wod['details'].get('time', '')}, "
            f"Feedback: {last_wod['details'].get('feedback', '')}"
        )
    else:
        history_text = "No recorded WOD session."

    prompt = (
        "You are a professional CrossFit coach, and I am an athlete with 2 years of experience in CrossFit. "
        "Give me a WOD exercise program following the typical structure of a WOD. Include Rx weights and time for exercises where appropriate. "
        "Please provide today's WOD program in exactly 4 complete blocks. Each block should start with 'Block X:' where X is the block number. "
        "Each block must include the following details: Block title, Exercises, Time. The first block is always the warm-up. "
        "The suggestion must take into account my last saved WOD workout below, targeting different muscle groups and considering previous difficulty feedback. "
        "To understand the difficulty feedback, look for one of the following keywords: too easy, easy, perfect, too difficult. "
        "Here is my last saved WOD workout:\n"
        f"{history_text}\n\n"
        "Now, based on the above, please provide today's complete WOD program."
    )
    
    suggestion = query_openai(prompt)
    pattern = r'(Block\s+\d+:[\s\S]*?)(?=Block\s+\d+:|$)'
    suggestion_blocks = re.findall(pattern, suggestion)
    if len(suggestion_blocks) < 4:
        flash("Warning: Expected 4 blocks but received fewer. The GPT response may be truncated.")
    saved_wod = "\n".join(suggestion_blocks)
    
    return render_template('wod_suggest.html', 
                           suggestion_blocks=suggestion_blocks, 
                           last_wod=last_wod,
                           saved_wod=saved_wod)

@app.route('/wod_history')
def wod_history():
    if "user_id" not in session:
        flash("Please select a user first.")
        return redirect(url_for('index'))
    workouts = get_all_workouts()
    wod_workouts = [w for w in workouts if w["workout_type"] == "wod" and w["user_id"] == session["user_id"]]
    return render_template('wod_history.html', workouts=wod_workouts)

@app.route('/record_wod_feedback', methods=['POST'])
def record_wod_feedback():
    if "user_id" not in session:
        flash("Please select a user first.")
        return redirect(url_for('index'))
    feedback = request.form.get('feedback')  # e.g., "easy"
    wod_workout = request.form.get('wod_workout')  # the full WOD workout suggestion
    today = datetime.date.today().isoformat()
    if wod_workout and feedback:
        details = {
            "block": "",         # Optionally, extract block info if needed.
            "exercises": wod_workout,  # Save the full workout suggestion here.
            "time": "",          # Update this if your suggestion includes time.
            "feedback": feedback
        }
        add_workout(today, session["user_id"], "wod", details)
        flash("WOD workout and feedback recorded successfully.")
    else:
        flash("Missing WOD workout data or feedback.")
    return redirect(url_for('index'))

@app.route('/record_wod', methods=['POST'])
def record_wod():
    if "user_id" not in session:
        flash("Please select a user first.")
        return redirect(url_for('index'))
    today = datetime.date.today().isoformat()
    wod_workout = request.form.get('wod_workout')
    if wod_workout:
        details = {
            "wod_workout": wod_workout
        }
        add_workout(today, session["user_id"], "wod", details)
        flash("WOD workout recorded successfully.")
    else:
        flash("No WOD workout data provided.")
    return redirect(url_for('wod_suggest'))

@app.route('/delete_wod/<int:record_id>', methods=['POST'])
def delete_wod(record_id):
    import sqlite3
    from database import DB_NAME
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM workout_logs WHERE id = ? AND workout_type = 'wod'", (record_id,))
    conn.commit()
    conn.close()
    flash("WOD record deleted successfully.")
    return redirect(url_for('wod_history'))

if __name__ == '__main__':
    app.run(debug=True)
