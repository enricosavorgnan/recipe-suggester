"""
LLM prompts for recipe generation.
"""


def get_recipe_generation_prompt(ingredients: list[str]) -> str:
    """
    Generate the prompt for recipe creation from ingredients.

    Args:
        ingredients: List of ingredient names

    Returns:
        Complete prompt string for the LLM
    """
    ingredients_str = ", ".join(ingredients)

    return f'''You are a professional chef assistant. Given the following ingredients, create a delicious and feasible recipe.

Ingredients available: {ingredients_str}

Create a recipe using these ingredients. You can suggest additional common pantry items if needed (like salt, pepper, olive oil, water).

Return ONLY a valid JSON object with this exact structure:
{{
  "title": "Creative and appetizing recipe name",
  "difficulty": "Easy|Medium|Hard",
  "preparation_time": <minutes as integer>,
  "cooking_time": <minutes as integer>,
  "ingredients": [
    {{
      "name": "ingredient name",
      "quantity_needed": <number>,
      "unit": "gr|ml|pieces|tbsp|tsp|cups|etc"
    }}
  ],
  "procedure": [
    "Step 1 description",
    "Step 2 description",
    "Step 3 description"
  ]
}}

Important:
- Create an appealing and descriptive title for the recipe
- Include ALL ingredients from the list above in your recipe
- Include realistic quantities and appropriate units
- Provide clear, numbered step-by-step instructions
- preparation_time is for prep work (cutting, mixing, etc.)
- cooking_time is for actual cooking/baking time
- Make the recipe practical and delicious
- Return ONLY the JSON, no additional text'''


RECIPE_SYSTEM_PROMPT = """You are a professional chef assistant that creates recipes in JSON format. Always return valid JSON only, with no additional text or markdown formatting."""
