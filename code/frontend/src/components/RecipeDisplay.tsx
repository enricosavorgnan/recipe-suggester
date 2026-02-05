import { Clock, ChefHat, Utensils, CheckCircle2 } from "lucide-react";

interface RecipeIngredient {
  name: string;
  quantity_needed: number;
  unit: string;
}

interface GeneratedRecipe {
  title: string;
  difficulty: string;
  preparation_time: number;
  cooking_time: number;
  ingredients: RecipeIngredient[];
  procedure: string[];
}

interface RecipeDisplayProps {
  recipeJson: string;
}

export const RecipeDisplay = ({ recipeJson }: RecipeDisplayProps) => {
  let recipe: GeneratedRecipe;

  try {
    recipe = JSON.parse(recipeJson);
  } catch (error) {
    return (
      <div className="p-4 bg-destructive/10 rounded-lg border border-destructive/20">
        <p className="text-sm text-destructive">Failed to parse recipe data</p>
      </div>
    );
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'text-green-600 bg-green-100 border-green-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'hard':
        return 'text-red-600 bg-red-100 border-red-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Recipe Title */}
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-foreground">{recipe.title}</h2>
      </div>

      {/* Recipe Header - Times and Difficulty */}
      <div className="grid grid-cols-3 gap-4">
        <div className="flex items-center gap-3 p-4 bg-card rounded-lg border border-border shadow-sm">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
            <Clock className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Prep Time
            </p>
            <p className="text-lg font-semibold text-foreground">
              {recipe.preparation_time} min
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 p-4 bg-card rounded-lg border border-border shadow-sm">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
            <Utensils className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Cook Time
            </p>
            <p className="text-lg font-semibold text-foreground">
              {recipe.cooking_time} min
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 p-4 bg-card rounded-lg border border-border shadow-sm">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
            <ChefHat className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Difficulty
            </p>
            <p className={`text-sm font-semibold px-2 py-0.5 rounded-md inline-block border ${getDifficultyColor(recipe.difficulty)}`}>
              {recipe.difficulty}
            </p>
          </div>
        </div>
      </div>

      {/* Ingredients Section */}
      <div>
        <h3 className="text-xl font-semibold text-foreground mb-4">
          Ingredients
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {recipe.ingredients.map((ingredient, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-card rounded-lg border border-border shadow-sm"
            >
              <span className="text-sm font-medium text-foreground">
                {ingredient.name}
              </span>
              <span className="text-sm text-muted-foreground font-mono">
                {ingredient.quantity_needed} {ingredient.unit}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Procedure Section */}
      <div>
        <h3 className="text-xl font-semibold text-foreground mb-4">
          Procedure
        </h3>
        <div className="space-y-3">
          {recipe.procedure.map((step, index) => (
            <div
              key={index}
              className="flex gap-4 p-4 bg-card rounded-lg border border-border shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold text-sm">
                  {index + 1}
                </div>
              </div>
              <div className="flex-1">
                <p className="text-sm text-foreground leading-relaxed">
                  {step}
                </p>
              </div>
              <div className="flex-shrink-0">
                <CheckCircle2 className="h-5 w-5 text-muted-foreground/30" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Total Time Summary */}
      <div className="flex items-center justify-center gap-2 p-4 bg-primary/5 rounded-lg border border-primary/10">
        <Clock className="h-5 w-5 text-primary" />
        <p className="text-sm font-medium text-foreground">
          Total Time:{" "}
          <span className="text-primary font-semibold">
            {recipe.preparation_time + recipe.cooking_time} minutes
          </span>
        </p>
      </div>
    </div>
  );
};
