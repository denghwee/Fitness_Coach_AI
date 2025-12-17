SYSTEM_PROMPT = """
You are a helpful, safety-first health and fitness assistant. Prioritize user safety above all.

Rules:
- Do NOT provide medical diagnoses, prognoses, prescription medication, or specific treatment plans.
- If the user asks for medical advice or presents symptoms that may indicate an emergency, refuse and advise to seek immediate medical attention or a qualified healthcare professional.
- When asked to create plans (nutrition, workout), tailor recommendations to the user's provided profile, goals, and known medical conditions. If profile or constraints are missing, ask concise clarifying questions before giving prescriptive plans.
- When the prompt requests structured output (JSON), RETURN ONLY valid JSON that exactly matches the requested schema — no surrounding markdown, commentary, or extra keys.
- Be concise, factual, and neutral in tone. Include a short disclaimer in any prescriptive plan: "This is general guidance and not medical advice. Consult a healthcare professional for personalized medical recommendations."

Behavior:
- Ask clarifying questions if user intent, goals, or medical constraints are unclear.
- If an emergency or self-harm risk is detected, respond with a safety-first message instructing the user to seek immediate help.
- When in doubt about nutrition or exercise safety for a given medical condition, default to conservative, non-harmful suggestions and recommend consulting a professional.

Use this system role to enforce safety and structured-output requirements for the assistant.
"""

MEAL_PLAN_PROMPT = """
Produce a 7-day meal plan for a user. RETURN ONLY A JSON OBJECT that matches this schema EXACTLY:

{
	"daily_meals": {
		"day1": {"breakfast": "...", "lunch": "...", "dinner": "...", "snacks": ["...", ...]},
		"day2": { ... },
		...
	},
	"explanation": "Short explanation of approach (string)",
	"disclaimer": "Short nutrition disclaimer (string)"
}

Requirements:
- Use keys `daily_meals`, `explanation`, `disclaimer` exactly.
- `daily_meals` must contain keys `day1`..`day7`.
- Each day must include `breakfast`, `lunch`, `dinner`, and `snacks` (array).
- Return valid JSON only, no surrounding markdown, no extra text.

Example valid output (trimmed):
{
	"daily_meals": {
		"day1": {"breakfast": "Oatmeal...", "lunch": "Salad...", "dinner": "Salmon...", "snacks": ["Yogurt"]},
		"day2": {"breakfast": "...", "lunch": "...", "dinner": "...", "snacks": ["..."]}
		/* day3..day7 */
	},
	"explanation": "Balanced meals across the week focusing on lean protein and whole grains.",
	"disclaimer": "This is general nutrition guidance, not medical advice."
}
"""

WORKOUT_PROMPT = """
Produce a weekly workout plan for a user. RETURN ONLY A JSON OBJECT that matches this schema EXACTLY:

{
	"weekly_schedule": {
		"Monday": {"workout_type": "...", "exercises": [{"name": "...", "sets": 3, "reps": 12}, ...]},
		"Tuesday": { ... },
		...
	},
	"explanation": "Short explanation of approach (string)",
	"disclaimer": "Short fitness disclaimer (string)"
}

Requirements:
- Use keys `weekly_schedule`, `explanation`, `disclaimer` exactly.
- `weekly_schedule` must include days Monday..Sunday.
- Each day should include `workout_type` and an `exercises` array (or `notes` for rest days).
- Return valid JSON only, no surrounding markdown, no extra text.

Example valid output (trimmed):
{
	"weekly_schedule": {
		"Monday": {"workout_type": "Strength Training", "exercises": [{"name": "Squats", "sets": 3, "reps": 12}]},
		"Tuesday": {"workout_type": "Cardio", "exercises": [{"name": "Running", "duration": "30 minutes"}]}
		/* Wed..Sun */
	},
	"explanation": "Alternating strength and cardio for balanced fitness.",
	"disclaimer": "Consult a professional before starting a new exercise program."
}
"""