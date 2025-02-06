from flask import Flask, render_template, request, redirect, url_for, flash
import datetime
from database import initialize_db, add_workout, get_all_workouts
from llama_integration import query_llama

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key for production

# Initialize the database when the app starts
initialize_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record', methods=['GET', 'POST'])
def record_workout():
    if request.method == 'POST':
        # Use today's date if none is provided
        date_input = request.form.get('date')
        if not date_input:
            date_input = datetime.date.today().isoformat()
        exercise = request.form.get('exercise')
        details = request.form.get('details')
        add_workout(date_input, exercise, details)
        flash('Workout recorded successfully.')
        return redirect(url_for('index'))
    return render_template('record.html')

@app.route('/history')
def history():
    workouts = get_all_workouts()
    return render_template('history.html', workouts=workouts)

@app.route('/suggest')
def suggest():
    # Retrieve all workouts (or just the recent ones)
    workouts = get_all_workouts()
    
    # Optionally, limit to the most recent 5 sessions to keep the prompt concise
    recent_workouts = workouts[:5]
    
    # Format the workout history into a readable string.
    history_text = "\n".join(
        [f"Date: {w[1]}, Exercise: {w[2]}, Details: {w[3]}" for w in recent_workouts]
    )
    
    # Build a prompt that incorporates both your workout history and detailed instructions.
    prompt = (
        "Based on my recent workout history focusing on strength training.\n"
        "Please suggest a workout plan for today, starting with warm-up and following with the main exercises. "
        "Keep in mind a high-intensity level. "
        "Include exactly 5 types of exercises in the main exercises, "
        "Each exercise can be from 3 to 5 sets."
        "The exercises must be limited to 2 body parts per session, for example - chest and back, or shoulders and legs."
        "Do not suggest the same body parts that were trained in the most recent history (see the dates). Suggest those that I haven't trained in a while."
        "When choosing weight for the exercise - take the weight I have done with this exercise in the last historic session and add 1-3 kg."
        "Give me suggestion in the following format where every set starts from the new line."
        "In the beginning, give me the list of the exercises from the previous workout session."
        "Then give me today’s program. Indicate which part of the body it works, number of sets, number of repetitions and weight."
        "For example: Chest - Bench press: ramp to 80kg, 6 reps, 5 sets\n\n"
        "Here is my workout history:\n"
        f"{history_text}\n\n"
        "Now, based on the above history, please provide today's workout program."
    )
    
    # Call the model with the combined prompt.
    suggestion = query_llama(prompt)
    
    return render_template('suggest.html', suggestion=suggestion)

@app.route('/record_actual', methods=['POST'])
def record_actual():
    today = datetime.date.today().isoformat()
    # Process the 5 rows from the form
    for i in range(5):
        body_part = request.form.get(f'body_part_{i}')
        exercise_name = request.form.get(f'exercise_{i}')
        max_weight = request.form.get(f'max_weight_{i}')
        sets = request.form.get(f'sets_{i}')
        reps = request.form.get(f'reps_{i}')
        
        # Only record the row if all required fields are provided.
        if body_part and exercise_name and max_weight and sets and reps:
            # Combine Body Part and Exercise Name for a concise record.
            full_exercise = f"{body_part} - {exercise_name}"
            # Store additional details in a formatted string.
            details = f"Max Weight: {max_weight}, Sets: {sets}, Reps: {reps}"
            add_workout(today, full_exercise, details)
    
    flash("Workout recorded successfully.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
