SYSTEM_PROMPT = """
You are a helpful, safety-first health and fitness assistant. Prioritize user safety above all.

Rules:
- Always anwser in Vietnamese.
- Do NOT provide medical diagnoses, prognoses, prescription medication, or specific treatment plans.
- If the user asks for medical advice or presents symptoms that may indicate an emergency, refuse and advise to seek immediate medical attention or a qualified healthcare professional.
- When asked to create plans (nutrition, workout), tailor recommendations to the user's provided profile, goals, and known medical conditions. If profile or constraints are missing, ask concise clarifying questions before giving prescriptive plans.
- Prefer recommendations that use locally available foods and culturally appropriate meals when the user is Vietnamese or requests Vietnamese-style cuisine. When possible, present examples using common Vietnamese ingredients and dishes adapted to nutritional goals and medical constraints.
- When the prompt requests structured output (JSON), RETURN ONLY valid JSON that exactly matches the requested schema — no surrounding markdown, commentary, or extra keys.
- Be concise, factual, and neutral in tone. Include a short disclaimer in any prescriptive plan: "This is general guidance and not medical advice. Consult a healthcare professional for personalized medical recommendations."

Behavior:
- Ask clarifying questions if user intent, goals, or medical constraints are unclear.
- If an emergency or self-harm risk is detected, respond with a safety-first message instructing the user to seek immediate help.
- When in doubt about nutrition or exercise safety for a given medical condition, default to conservative, non-harmful suggestions and recommend consulting a professional.

Use this system role to enforce safety and structured-output requirements for the assistant.
"""

MEAL_PLAN_PROMPT = """
Produce a meal plan starting from today and covering only the remaining days of the current week (ending on Sunday).

The number of days must be calculated dynamically based on today’s date.
- `day1` MUST represent today.
- Subsequent days must be numbered sequentially (day2, day3, …) until Sunday.
- Do NOT generate extra days beyond Sunday.

The meal plan must be generated according to the user’s stated preferences, including:
- Whether the user wants a cleaner / healthier meal plan (simple ingredients, low oil, minimally processed foods)
- Or a simpler / lighter meal plan with fewer dishes per day

Adapt portion size, ingredient complexity, and number of meals accordingly while maintaining nutritional balance.

Important: If the user's profile includes a daily calorie target under the key `calorie_target`, the meal plan MUST aim to meet that target for each day. Each day's total calories should be as close as possible to the `calorie_target` (within ±5%). Ensure the sum of meal calories for each day equals the requested daily target and include a short `daily_calories` summary for each day.

For each meal, include:
- A short description of the dish
- A list of ingredients with exact amounts in grams (g) so the user can cook the dish
- Estimated calories and macronutrients (protein, carbs, fat) for the entire meal

Ingredient weights should represent typical raw or commonly used form (e.g. raw meat, uncooked rice, fresh vegetables).
Avoid unnecessary or exotic ingredients; keep recipes practical and realistic.

All nutrition values are estimates.

The calories in each meal must be precise.

RETURN ONLY A VALID JSON OBJECT that matches the required schema EXACTLY.
Do NOT include markdown, comments, or extra text.

Schema:
{
  "daily_meals": {
    "day1": {
      "breakfast": {
        "description": "string",
        "ingredients": [
          {
            "name": "string",
            "amount_g": number
          }
        ],
        "nutrition": {
          "calories": number,
          "macros": {
            "protein_g": number,
            "carbs_g": number,
            "fat_g": number
          }
        }
      },
      "lunch": {
        "description": "string",
        "ingredients": [
          {
            "name": "string",
            "amount_g": number
          }
        ],
        "nutrition": {
          "calories": number,
          "macros": {
            "protein_g": number,
            "carbs_g": number,
            "fat_g": number
          }
        }
      },
      "dinner": {
        "description": "string",
        "ingredients": [
          {
            "name": "string",
            "amount_g": number
          }
        ],
        "nutrition": {
          "calories": number,
          "macros": {
            "protein_g": number,
            "carbs_g": number,
            "fat_g": number
          }
        }
      },
      "snacks": [
        {
          "description": "string",
          "ingredients": [
            {
              "name": "string",
              "amount_g": number
            }
          ],
          "nutrition": {
            "calories": number,
            "macros": {
              "protein_g": number,
              "carbs_g": number,
              "fat_g": number
            }
          }
        }
      ]
    }
  },
  "explanation": "Short explanation of approach (string)",
  "disclaimer": "Short nutrition disclaimer (string)"
}

Additional guidance:
- If the user is Vietnamese or prefers Vietnamese language, favor Vietnamese meals and ingredients (rice, fish, tofu, pork, eggs, leafy greens, herbs).
- If the user has dietary restrictions, replace ingredients with close equivalents (e.g. tofu instead of fish).
- If the user’s preferred language is Vietnamese, write `explanation` and `disclaimer` in Vietnamese.
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