import { ChefHat } from "lucide-react";
import { Recipe } from "@/api/recipes";

interface RecipeDetailProps {
  recipe: Recipe | null;
}

export const RecipeDetail = ({ recipe }: RecipeDetailProps) => {
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

  return (
    <div className="h-full flex flex-col">
      <h2 className="text-3xl font-bold text-foreground mb-6">
        {recipe.title}
      </h2>
      <div className="space-y-6">
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
        {/* Placeholder for more content to test scrolling */}
        <div className="space-y-4">
          <p className="text-muted-foreground">
            More recipe details will appear here...
          </p>
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} className="p-4 bg-accent/50 rounded-lg">
              <p className="text-foreground">Content section {i + 1}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
