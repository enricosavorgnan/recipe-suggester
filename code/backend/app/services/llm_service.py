import json
from openai import OpenAI, AsyncOpenAI
from app.config.settings import settings
from app.config.prompts import get_recipe_generation_prompt, RECIPE_SYSTEM_PROMPT

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def generate_recipe_from_ingredients(ingredients: list[str]) -> dict:
    """
    Generate a recipe using OpenAI GPT based on a list of ingredients.

    Args:
        ingredients: List of ingredient names (e.g., ["Tomato", "Pasta", "Garlic"])

    Returns:
        dict: Recipe with structure containing difficulty, times, ingredients with quantities, and procedure

    Raises:
        Exception: If LLM call fails (API error, rate limit, invalid response, etc.)
    """
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": RECIPE_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": get_recipe_generation_prompt(ingredients)
                }
            ],
            temperature=0.5,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        recipe_json = response.choices[0].message.content
        recipe_dict = json.loads(recipe_json)

        # Validate the response has the required fields
        required_fields = ["title", "difficulty", "preparation_time", "cooking_time", "ingredients", "procedure"]
        for field in required_fields:
            if field not in recipe_dict:
                raise ValueError(f"Missing required field: {field}")

        return recipe_dict

    except Exception as e:
        print(f"Error generating recipe with LLM: {e}")
        raise e
