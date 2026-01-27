import json
from openai import OpenAI
from app.config.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_recipe_from_ingredients(ingredients: list[str]) -> dict:
    """
    Generate a recipe using OpenAI GPT based on a list of ingredients.

    Args:
        ingredients: List of ingredient names (e.g., ["Tomato", "Pasta", "Garlic"])

    Returns:
        dict: Recipe with structure containing difficulty, times, ingredients with quantities, and procedure
    """

    # Create the prompt
    ingredients_str = ", ".join(ingredients)

    prompt = f"""You are a professional chef assistant. Given the following ingredients, create a delicious and feasible recipe.

Ingredients available: {ingredients_str}

Create a recipe using these ingredients. You can suggest additional common pantry items if needed (like salt, pepper, olive oil, water).

Return ONLY a valid JSON object with this exact structure:
{{
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
- Include ALL ingredients from the list above in your recipe
- Include realistic quantities and appropriate units
- Provide clear, numbered step-by-step instructions
- preparation_time is for prep work (cutting, mixing, etc.)
- cooking_time is for actual cooking/baking time
- Make the recipe practical and delicious
- Return ONLY the JSON, no additional text"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional chef assistant that creates recipes in JSON format. Always return valid JSON only, with no additional text or markdown formatting."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        recipe_json = response.choices[0].message.content
        recipe_dict = json.loads(recipe_json)

        # Validate the response has the required fields
        required_fields = ["difficulty", "preparation_time", "cooking_time", "ingredients", "procedure"]
        for field in required_fields:
            if field not in recipe_dict:
                raise ValueError(f"Missing required field: {field}")

        return recipe_dict

    except Exception as e:
        print(f"Error generating recipe with LLM: {e}")
        # Return an error message
        raise e
