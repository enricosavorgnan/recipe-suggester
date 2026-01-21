# External imports
import unittest

# Internal imports
from my_project import RecipeRecommender


class TestRecipeEngine(unittest.TestCase):
"""
This class tests performances of recipes retrieval model.
"""


    @classmethod
    def setUpClass(cls):
        """
        Load the retrieval system only one time.
        """
        
        # Load the retrieval system
        print("--- Recommender System Initialization ---")
        cls.recommender = RecipeRecommender()


    def test_recipe_coverage(self):
        """
        Tests th performance of the recipes retrieval system.
        Checks if the retrieved recipes contains the detected ingridients.
        """

        # Define the ingridients and call the retrieval system procedure
        input_ingredients = ["tomato", "eggs", "cheese"]
        suggested_recipes = self.recommender.get_recipes(input_ingredients)
        self.assertIsInstance(suggested_recipes, list)
        self.assertGreater(len(suggested_recipes), 0, "Nessuna ricetta trovata")

        # Merge all the ingridients retrieved from the suggested recipes
        all_recipe_ingredients = set()
        for recipe in suggested_recipes:
            all_recipe_ingredients.update(recipe['ingredients_list'])
        
        # Check if all input ingridients appear into the suggested-ingridients list
        input_set = set(input_ingredients)
        missing_ingredients = []
        for inp_ingridient in input_set:
            if inp_ingridient not in all_recipe_ingredients:
                missing_ingredients.append(inp_ingridient)
        self.assertEqual(len(missing_ingredients), 0, 
                         f"Recipes not found for ingridients: {missing_ingredients}.")


    def test_no_hallucination_check(self):
        """
        Test the consistency of the suggested recipes.
        E.g. if 'chicken' is passed as input ingridient, system should not suggest 'chocolate cake'.
        """

        # Define the ingridient to retrieve into recipes
        input_ingredients = ["chicken_breast"]
        recipes = self.recommender.get_recipes(input_ingredients)

        # All recipes should contain the ingridient above
        for recipe in recipes:
            has_chicken = all("chicken" in ingr.lower() for ingr in recipe['ingredients_list'])


if __name__ == '__main__':
    unittest.main()