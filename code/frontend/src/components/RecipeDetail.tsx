import { ChefHat, AlertCircle } from "lucide-react";
import { Recipe } from "@/api/recipes";
import { useQuery } from "@tanstack/react-query";
import jobsApi from "@/api/jobs";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface RecipeDetailProps {
  recipe: Recipe | null;
  token: string;
}

export const RecipeDetail = ({ recipe, token }: RecipeDetailProps) => {
  const { data: jobs, isLoading } = useQuery({
    queryKey: ["recipe-jobs", recipe?.id],
    queryFn: () => jobsApi.getJobsByRecipe(recipe!.id, token),
    enabled: !!recipe && !!token,
  });

  if (!recipe) {
    return (
      <div className="h-full flex flex-col items-center justify-center">
        <ChefHat className="h-24 w-24 text-muted-foreground mb-6" />
        <h2 className="text-3xl font-bold text-foreground mb-4">
          Welcome to Recipe Suggester
        </h2>
        <p className="text-muted-foreground text-lg">
          Select a recipe from the sidebar or create a new one
        </p>
      </div>
    );
  }

  const ingredientsJob = jobs?.ingredients_job;
  const hasImage = !!recipe.image;
  const hasIngredients = ingredientsJob?.status === 'completed' && ingredientsJob.ingredients_json;

  return (
    <div className="h-full flex flex-col">
      <h2 className="text-3xl font-bold text-foreground mb-6">
        {recipe.title}
      </h2>

      {isLoading ? (
        <div className="text-muted-foreground">Loading recipe details...</div>
      ) : (
        <div className="space-y-6">
          {/* Recipe Image */}
          {hasImage ? (
            <div className="flex justify-center">
              <img
                src={`${API_URL}/uploads/recipes/${recipe.image}`}
                alt={recipe.title}
                className="max-w-md rounded-lg shadow-lg"
              />
            </div>
          ) : (
            <div className="flex items-center gap-3 p-4 bg-muted/50 rounded-lg border border-border">
              <AlertCircle className="h-5 w-5 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                No image uploaded for this recipe
              </p>
            </div>
          )}

          {/* Ingredients */}
          <div>
            <h3 className="text-xl font-semibold text-foreground mb-4">
              Detected Ingredients
            </h3>
            {hasIngredients ? (
              <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm">
                {JSON.stringify(JSON.parse(ingredientsJob.ingredients_json!), null, 2)}
              </pre>
            ) : ingredientsJob?.status === 'running' ? (
              <div className="flex items-center gap-3 p-4 bg-muted/50 rounded-lg border border-border">
                <AlertCircle className="h-5 w-5 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Ingredients detection is still in progress...
                </p>
              </div>
            ) : ingredientsJob?.status === 'failed' ? (
              <div className="flex items-center gap-3 p-4 bg-destructive/10 rounded-lg border border-destructive/20">
                <AlertCircle className="h-5 w-5 text-destructive" />
                <p className="text-sm text-destructive">
                  Failed to detect ingredients. Please try again.
                </p>
              </div>
            ) : (
              <div className="flex items-center gap-3 p-4 bg-muted/50 rounded-lg border border-border">
                <AlertCircle className="h-5 w-5 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  No ingredients detected yet. Upload an image to start detection.
                </p>
              </div>
            )}
          </div>

          {/* Recipe Metadata */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-semibold text-muted-foreground">Recipe ID</p>
              <p className="text-lg text-foreground">{recipe.id}</p>
            </div>
            <div>
              <p className="text-sm font-semibold text-muted-foreground">Created At</p>
              <p className="text-lg text-foreground">
                {new Date(recipe.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
