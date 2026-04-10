from flask import Flask, render_template
import pandas as pd
import random
import os

# -------- PATH SETUP --------
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, "templates")

app = Flask(__name__, template_folder=template_dir)

# -------- LOAD DATA --------
courses = pd.read_csv("../data/courses.csv")
rooms = pd.read_csv("../data/rooms.csv")

course_list = courses.to_dict(orient="records")
room_list = rooms.to_dict(orient="records")

time_slots = [
    f"{day}{p}"
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri"]
    for p in range(1, 9)
]

# ================= GA FUNCTION =================
def run_genetic_algorithm():

    def fitness(timetable):
        score = 0
        used_slots = set()

        for i in range(len(timetable)):
            slot = timetable[i]["slot"]
            faculty = timetable[i]["faculty"]
            room = timetable[i]["room"]

            score += 5

            if slot in used_slots:
                score -= 20
            else:
                used_slots.add(slot)

            for j in range(i + 1, len(timetable)):
                if timetable[i]["slot"] == timetable[j]["slot"]:

                    if faculty == timetable[j]["faculty"]:
                        score -= 30

                    if room == timetable[j]["room"]:
                        score -= 30

        return score

    def generate_random():
        timetable = []
        used_slots = set()

        for course in course_list:
            slot = random.choice(time_slots)

            while slot in used_slots or slot.endswith("4"):
                slot = random.choice(time_slots)

            used_slots.add(slot)

            room = random.choice(room_list)

            timetable.append({
                "course": course["course_name"],
                "faculty": course["faculty"],
                "slot": slot,
                "room": room["room_name"],
                "type": course["type"]
            })

        return timetable

    def selection(pop):
        return sorted(pop, key=fitness, reverse=True)[:10]

    def crossover(p1, p2):
        return [random.choice([p1[i], p2[i]]).copy() for i in range(len(p1))]

    def mutate(t):
        for _ in range(2):
            x = random.choice(t)
            x["slot"] = random.choice(time_slots)
        return t

    # population
    population = [generate_random() for _ in range(30)]

    scores = []

    for _ in range(50):
        selected = selection(population)
        new_pop = selected.copy()

        while len(new_pop) < 30:
            child = crossover(random.choice(selected), random.choice(selected))

            if random.random() < 0.5:
                child = mutate(child)

            new_pop.append(child)

        population = new_pop

        best_score = max([fitness(p) for p in population])
        scores.append(best_score)

    best = max(population, key=fitness)

    # GRID
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    periods = [str(i) for i in range(1, 9)]

    grid = {d: {p: "Free" for p in periods} for d in days}

    for d in days:
        grid[d]["4"] = "LUNCH BREAK 🍱"

    for t in best:
        day = t["slot"][:3]
        period = t["slot"][3:]

        if period == "4":
            continue

        grid[day][period] = f"{t['course']} ({t['room']})"

    # ✅ FINAL RETURN (DO NOT CHANGE THIS)
    return [grid], scores
@app.route("/")
def home():
    timetables, scores = run_genetic_algorithm()

    return render_template(
        "index.html",
        timetables=timetables,
        scores=scores
    )
if __name__ == "__main__":
    app.run(debug=True)