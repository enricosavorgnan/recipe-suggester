import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import recipesApi, { Recipe } from "@/api/recipes";
import categoriesApi, { Category } from "@/api/categories";
import jobsApi, { IngredientsJob } from "@/api/jobs";
import { useState } from "react";
import { toast } from "sonner";
import { Sidebar } from "@/components/Sidebar";
import { ImageUpload } from "@/components/ImageUpload";
import { RecipeDetail } from "@/components/RecipeDetail";
import {
  RenameRecipeDialog,
  DeleteRecipeDialog,
  CategoryDialog,
  DeleteCategoryDialog,
} from "@/components/RecipeDialogs";

const Dashboard = () => {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [showUploadView, setShowUploadView] = useState(false);

  // Recipe dialog state
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [recipeToRename, setRecipeToRename] = useState<Recipe | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [deleteRecipeDialogOpen, setDeleteRecipeDialogOpen] = useState(false);
  const [recipeToDelete, setRecipeToDelete] = useState<Recipe | null>(null);

  // Category state
  const [selectedRecipes, setSelectedRecipes] = useState<Set<number>>(new Set());
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [categoryAction, setCategoryAction] = useState<'create' | 'rename' | null>(null);
  const [categoryName, setCategoryName] = useState("");
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [filterCategoryId, setFilterCategoryId] = useState<number | null>(null);
  const [deleteCategoryDialogOpen, setDeleteCategoryDialogOpen] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState<number | null>(null);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Fetch recipes
  const { data: recipes, isLoading } = useQuery({
    queryKey: ["recipes", filterCategoryId],
    queryFn: () => recipesApi.getRecipes(token!, filterCategoryId),
    enabled: !!token,
  });

  // Fetch categories
  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: () => categoriesApi.getCategories(token!),
    enabled: !!token,
  });

  // Recipe mutations
  const renameMutation = useMutation({
    mutationFn: ({ id, title }: { id: number; title: string }) =>
      recipesApi.updateRecipeTitle(id, { title }, token!),
    onSuccess: (updatedRecipe) => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      toast.success("Recipe renamed successfully");
      // Update the selected recipe if it's the one being renamed
      if (selectedRecipe && selectedRecipe.id === updatedRecipe.id) {
        setSelectedRecipe(updatedRecipe);
      }
      setRenameDialogOpen(false);
      setRecipeToRename(null);
      setNewTitle("");
    },
    onError: () => {
      toast.error("Failed to rename recipe");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => recipesApi.deleteRecipe(id, token!),
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      toast.success("Recipe deleted successfully");
      // If the deleted recipe was selected, clear the selection
      if (selectedRecipe && selectedRecipe.id === deletedId) {
        setSelectedRecipe(null);
      }
      setDeleteRecipeDialogOpen(false);
      setRecipeToDelete(null);
    },
    onError: () => {
      toast.error("Failed to delete recipe");
    },
  });

  // Category mutations
  const createCategoryMutation = useMutation({
    mutationFn: (name: string) => categoriesApi.createCategory({ name }, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      toast.success("Category created successfully");
      setCategoryDialogOpen(false);
      setCategoryName("");
    },
    onError: () => {
      toast.error("Failed to create category");
    },
  });

  const updateCategoryMutation = useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) =>
      categoriesApi.updateCategory(id, { name }, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      toast.success("Category renamed successfully");
      setCategoryDialogOpen(false);
      setCategoryName("");
      setSelectedCategoryId(null);
    },
    onError: () => {
      toast.error("Failed to rename category");
    },
  });

  const deleteCategoryMutation = useMutation({
    mutationFn: (id: number) => categoriesApi.deleteCategory(id, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      toast.success("Category deleted successfully");
      setDeleteCategoryDialogOpen(false);
      setCategoryToDelete(null);
    },
    onError: () => {
      toast.error("Failed to delete category");
    },
  });

  const assignCategoryMutation = useMutation({
    mutationFn: (data: { recipe_ids: number[]; category_id: number | null }) =>
      categoriesApi.assignCategories(data, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      toast.success("Category assigned successfully");
      setSelectedRecipes(new Set());
    },
    onError: () => {
      toast.error("Failed to assign category");
    },
  });

  // Handlers
  const handleNewRecipe = () => {
    setSelectedRecipe(null);
    setShowUploadView(true);
  };

  const handleSelectRecipe = (recipe: Recipe) => {
    setSelectedRecipe(recipe);
    setShowUploadView(false);
  };

  const handleRename = (recipe: Recipe) => {
    setRecipeToRename(recipe);
    setNewTitle(recipe.title);
    setRenameDialogOpen(true);
  };

  const handleRenameSubmit = () => {
    if (recipeToRename && newTitle.trim()) {
      renameMutation.mutate({ id: recipeToRename.id, title: newTitle.trim() });
    }
  };

  const handleDelete = (recipe: Recipe) => {
    setRecipeToDelete(recipe);
    setDeleteRecipeDialogOpen(true);
  };

  const confirmDeleteRecipe = () => {
    if (recipeToDelete) {
      deleteMutation.mutate(recipeToDelete.id);
    }
  };

  const toggleRecipeSelection = (recipeId: number) => {
    const newSelection = new Set(selectedRecipes);
    if (newSelection.has(recipeId)) {
      newSelection.delete(recipeId);
    } else {
      newSelection.add(recipeId);
    }
    setSelectedRecipes(newSelection);
  };

  const handleCreateCategory = () => {
    setCategoryAction('create');
    setCategoryName("");
    setCategoryDialogOpen(true);
  };

  const handleRenameCategory = (category: Category) => {
    setCategoryAction('rename');
    setSelectedCategoryId(category.id);
    setCategoryName(category.name);
    setCategoryDialogOpen(true);
  };

  const handleDeleteCategory = (categoryId: number) => {
    setCategoryToDelete(categoryId);
    setDeleteCategoryDialogOpen(true);
  };

  const confirmDeleteCategory = () => {
    if (categoryToDelete) {
      deleteCategoryMutation.mutate(categoryToDelete);
    }
  };

  const handleCategorySubmit = () => {
    if (!categoryName.trim()) return;

    if (categoryAction === 'create') {
      createCategoryMutation.mutate(categoryName.trim());
    } else if (categoryAction === 'rename' && selectedCategoryId) {
      updateCategoryMutation.mutate({ id: selectedCategoryId, name: categoryName.trim() });
    }
  };

  const handleAssignCategory = (categoryId: number | null) => {
    if (selectedRecipes.size === 0) {
      toast.error("Please select at least one recipe");
      return;
    }
    assignCategoryMutation.mutate({
      recipe_ids: Array.from(selectedRecipes),
      category_id: categoryId,
    });
  };

  const handleJobComplete = async (job: IngredientsJob) => {
    // Invalidate recipes query to refetch
    await queryClient.invalidateQueries({ queryKey: ["recipes", filterCategoryId] });

    // Switch to recipe detail view
    // Fetch the updated recipe data
    try {
      const updatedRecipes = await recipesApi.getRecipes(token!, filterCategoryId);
      const newRecipe = updatedRecipes?.find(r => r.id === job.recipe_id);
      if (newRecipe) {
        setSelectedRecipe(newRecipe);
        setShowUploadView(false);
      }
    } catch (error) {
      console.error("Failed to fetch recipe after job completion:", error);
    }
  };

  const handleRecipeCreated = () => {
    queryClient.invalidateQueries({ queryKey: ["recipes", filterCategoryId] });
  };

  return (
    <div className="flex h-screen bg-gradient-subtle overflow-hidden">
      <Sidebar
        user={user}
        recipes={recipes}
        categories={categories}
        isLoading={isLoading}
        selectedRecipe={showUploadView ? null : selectedRecipe}
        selectedRecipes={selectedRecipes}
        filterCategoryId={filterCategoryId}
        onLogout={handleLogout}
        onNewRecipe={handleNewRecipe}
        onSelectRecipe={handleSelectRecipe}
        onRenameRecipe={handleRename}
        onDeleteRecipe={handleDelete}
        onToggleRecipeSelection={toggleRecipeSelection}
        onCreateCategory={handleCreateCategory}
        onRenameCategory={handleRenameCategory}
        onDeleteCategory={handleDeleteCategory}
        onAssignCategory={handleAssignCategory}
        onClearSelection={() => setSelectedRecipes(new Set())}
        onFilterCategory={setFilterCategoryId}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 p-8 overflow-y-auto">
          {showUploadView ? (
            <ImageUpload
              token={token!}
              onJobComplete={handleJobComplete}
              onRecipeCreated={handleRecipeCreated}
            />
          ) : (
            <RecipeDetail recipe={selectedRecipe} token={token!} />
          )}
        </main>
      </div>

      {/* Dialogs */}
      <RenameRecipeDialog
        open={renameDialogOpen}
        recipe={recipeToRename}
        newTitle={newTitle}
        isPending={renameMutation.isPending}
        onOpenChange={setRenameDialogOpen}
        onTitleChange={setNewTitle}
        onSubmit={handleRenameSubmit}
      />

      <DeleteRecipeDialog
        open={deleteRecipeDialogOpen}
        recipe={recipeToDelete}
        isPending={deleteMutation.isPending}
        onOpenChange={setDeleteRecipeDialogOpen}
        onConfirm={confirmDeleteRecipe}
      />

      <CategoryDialog
        open={categoryDialogOpen}
        action={categoryAction}
        categoryName={categoryName}
        isPending={createCategoryMutation.isPending || updateCategoryMutation.isPending}
        onOpenChange={(open) => {
          setCategoryDialogOpen(open);
          if (!open) {
            setCategoryName("");
            setSelectedCategoryId(null);
          }
        }}
        onNameChange={setCategoryName}
        onSubmit={handleCategorySubmit}
      />

      <DeleteCategoryDialog
        open={deleteCategoryDialogOpen}
        isPending={deleteCategoryMutation.isPending}
        onOpenChange={setDeleteCategoryDialogOpen}
        onConfirm={confirmDeleteCategory}
      />
    </div>
  );
};

export default Dashboard;
