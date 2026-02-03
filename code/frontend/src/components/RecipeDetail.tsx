import { useState, useEffect } from "react";
import { ChefHat, AlertCircle, Plus, Loader2, Check } from "lucide-react";
import { Recipe } from "@/api/recipes";
import { useQuery } from "@tanstack/react-query";
import jobsApi from "@/api/jobs";
import { Button } from "@/components/ui/button";
import { IngredientItem } from "@/components/IngredientItem";
import {
  AddIngredientDialog,
  EditIngredientDialog,
  DeleteIngredientDialog,
} from "@/components/IngredientDialogs";
import { RecipeDisplay } from "@/components/RecipeDisplay";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Ingredient {
  name: string;
  confidence?: number;
}

interface RecipeDetailProps {
  recipe: Recipe | null;
  token: string;
}

export const RecipeDetail = ({ recipe, token }: RecipeDetailProps) => {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [ingredientName, setIngredientName] = useState("");
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [deletingIndex, setDeletingIndex] = useState<number | null>(null);
  const [isGeneratingRecipe, setIsGeneratingRecipe] = useState(false);
  const [recipeJobId, setRecipeJobId] = useState<number | null>(null);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);

  const recipeLoadingMessages = [
    "Mixing up your ingredients...",
    "Elaborating the recipe...",
  ];

  const { data: jobs, isLoading } = useQuery({
    queryKey: ["recipe-jobs", recipe?.id],
    queryFn: () => jobsApi.getJobsByRecipe(recipe!.id, token),
    enabled: !!recipe && !!token,
  });

  // Update ingredients when jobs data changes
  useEffect(() => {
    if (jobs?.ingredients_job?.ingredients_json) {
      try {
        const parsedData = JSON.parse(jobs.ingredients_job.ingredients_json);
        if (parsedData.ingredients && Array.isArray(parsedData.ingredients)) {
          setIngredients(parsedData.ingredients);
        }
      } catch (error) {
        console.error("Failed to parse ingredients JSON:", error);
      }
    }
  }, [jobs]);

  // Rotating loading messages for recipe generation
  useEffect(() => {
    if (!isGeneratingRecipe) return;

    const interval = setInterval(() => {
      setLoadingMessageIndex((prev) => (prev + 1) % recipeLoadingMessages.length);
    }, 2000);

    return () => clearInterval(interval);
  }, [isGeneratingRecipe, recipeLoadingMessages.length]);

  // Polling for recipe job status
  useEffect(() => {
    if (!recipeJobId || !isGeneratingRecipe) return;

    const pollInterval = setInterval(async () => {
      try {
        const job = await jobsApi.getRecipeJob(recipeJobId, token);

        if (job.status !== 'running') {
          setIsGeneratingRecipe(false);
          clearInterval(pollInterval);

          if (job.status === 'completed') {
            // Recipe generation completed - could show success message or navigate
            console.log("Recipe generated successfully:", job.recipe_json);
          } else if (job.status === 'failed') {
            console.error("Recipe generation failed");
          }
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 1000);

    return () => clearInterval(pollInterval);
  }, [recipeJobId, isGeneratingRecipe, token]);

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

  const handleAddIngredient = () => {
    if (ingredientName.trim()) {
      setIngredients([...ingredients, { name: ingredientName.trim() }]);
      setIngredientName("");
      setAddDialogOpen(false);
    }
  };

  const handleEditIngredient = (index: number) => {
    setEditingIndex(index);
    setIngredientName(ingredients[index].name);
    setEditDialogOpen(true);
  };

  const handleSaveEdit = () => {
    if (editingIndex !== null && ingredientName.trim()) {
      const updated = [...ingredients];
      updated[editingIndex] = { ...updated[editingIndex], name: ingredientName.trim() };
      setIngredients(updated);
      setIngredientName("");
      setEditingIndex(null);
      setEditDialogOpen(false);
    }
  };

  const handleDeleteIngredient = (index: number) => {
    setDeletingIndex(index);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (deletingIndex !== null) {
      setIngredients(ingredients.filter((_, i) => i !== deletingIndex));
      setDeletingIndex(null);
      setDeleteDialogOpen(false);
    }
  };

  const handleConfirmIngredients = async () => {
    if (!recipe) return;

    try {
      setIsGeneratingRecipe(true);
      // Create recipe job with current ingredients
      const job = await jobsApi.createRecipeJob(recipe.id, ingredients, token);
      setRecipeJobId(job.id);
    } catch (error) {
      console.error("Failed to create recipe job:", error);
      setIsGeneratingRecipe(false);
    }
  };

  return (
    <div className="h-full flex flex-col pb-8">
      <h2 className="text-3xl font-bold text-foreground mb-6">
        {recipe.title}
      </h2>

      {isLoading ? (
        <div className="text-muted-foreground mb-8">Loading recipe details...</div>
      ) : (
        <div className="space-y-6 pb-8">
          {/* Creation Date - Top Right */}
          <div className="flex justify-end">
            <div className="text-right">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">
                Created
              </p>
              <p className="text-sm text-foreground font-light">
                {new Date(recipe.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                })}
              </p>
              <p className="text-xs text-muted-foreground font-light">
                {new Date(recipe.created_at).toLocaleTimeString('en-US', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>

          {/* Image - Centered */}
          <div className="flex justify-center">
            {hasImage ? (
              <img
                src={`${API_URL}/uploads/recipes/${recipe.image}`}
                alt={recipe.title}
                className="w-64 h-64 object-cover rounded-lg shadow-lg"
              />
            ) : (
              <div className="w-64 h-64 flex items-center justify-center bg-muted/50 rounded-lg border border-border">
                <div className="text-center">
                  <AlertCircle className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-xs text-muted-foreground">No image</p>
                </div>
              </div>
            )}
          </div>

          {/* Ingredients Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-foreground">
                Detected Ingredients
              </h3>
              {hasIngredients && (
                <Button
                  onClick={() => setAddDialogOpen(true)}
                  size="sm"
                  variant="outline"
                  className="gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Add Ingredient
                </Button>
              )}
            </div>

            {hasIngredients ? (
              <>
                <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
                  {ingredients.map((ingredient, index) => (
                    <IngredientItem
                      key={index}
                      ingredient={ingredient}
                      onEdit={() => handleEditIngredient(index)}
                      onDelete={() => handleDeleteIngredient(index)}
                    />
                  ))}
                </div>

                {/* Confirm Button or Loading State */}
                {!jobs?.recipe_job || jobs.recipe_job.status === 'failed' || jobs.recipe_job.status === 'running' ? (
                  <div className="mt-6">
                    {isGeneratingRecipe ? (
                      <div className="flex flex-col items-center gap-6">
                        <div className="flex items-center gap-3">
                          <Loader2 className="h-6 w-6 animate-spin text-primary" />
                          <p className="text-lg font-medium text-foreground">
                            {recipeLoadingMessages[loadingMessageIndex]}
                          </p>
                        </div>
                      </div>
                    ) : jobs?.recipe_job?.status === 'failed' ? (
                      <div className="flex justify-center">
                        <div className="flex items-center gap-3 p-4 bg-destructive/10 rounded-lg border border-destructive/20">
                          <AlertCircle className="h-5 w-5 text-destructive" />
                          <p className="text-sm text-destructive">
                            Failed to generate recipe. Please try again.
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div className="flex justify-center">
                        <Button
                          onClick={handleConfirmIngredients}
                          size="lg"
                          className="gap-2"
                        >
                          <Check className="h-5 w-5" />
                          Confirm & Generate Recipe
                        </Button>
                      </div>
                    )}
                  </div>
                ) : null}
              </>
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

          {/* Generated Recipe Display */}
          {jobs?.recipe_job?.status === 'completed' && jobs.recipe_job.recipe_json && (
            <div className="mt-8">
              <div className="border-t border-border pt-8">
                <h2 className="text-2xl font-bold text-foreground mb-6">
                  Your Generated Recipe
                </h2>
                <RecipeDisplay recipeJson={jobs.recipe_job.recipe_json} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Ingredient Dialogs */}
      <AddIngredientDialog
        open={addDialogOpen}
        ingredientName={ingredientName}
        onOpenChange={(open) => {
          setAddDialogOpen(open);
          if (!open) setIngredientName("");
        }}
        onNameChange={setIngredientName}
        onSubmit={handleAddIngredient}
      />

      <EditIngredientDialog
        open={editDialogOpen}
        ingredientName={ingredientName}
        onOpenChange={(open) => {
          setEditDialogOpen(open);
          if (!open) {
            setIngredientName("");
            setEditingIndex(null);
          }
        }}
        onNameChange={setIngredientName}
        onSubmit={handleSaveEdit}
      />

      <DeleteIngredientDialog
        open={deleteDialogOpen}
        ingredientName={deletingIndex !== null ? ingredients[deletingIndex]?.name : ""}
        onOpenChange={(open) => {
          setDeleteDialogOpen(open);
          if (!open) setDeletingIndex(null);
        }}
        onConfirm={handleConfirmDelete}
      />
    </div>
  );
};
