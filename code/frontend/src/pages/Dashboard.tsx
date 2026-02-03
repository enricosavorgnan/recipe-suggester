import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { LogOut, ChefHat, MoreVertical, Edit, Trash2, Plus, Check, FolderPlus, Tags } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import recipesApi, { Recipe } from "@/api/recipes";
import categoriesApi, { Category } from "@/api/categories";
import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";

const Dashboard = () => {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [recipeToRename, setRecipeToRename] = useState<Recipe | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [showUploadView, setShowUploadView] = useState(false);

  // Category state
  const [selectedRecipes, setSelectedRecipes] = useState<Set<number>>(new Set());
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [categoryAction, setCategoryAction] = useState<'create' | 'rename' | null>(null);
  const [categoryName, setCategoryName] = useState("");
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [filterCategoryId, setFilterCategoryId] = useState<number | null>(null);

  // Delete confirmation state
  const [deleteRecipeDialogOpen, setDeleteRecipeDialogOpen] = useState(false);
  const [recipeToDelete, setRecipeToDelete] = useState<Recipe | null>(null);
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

  // Rename mutation
  const renameMutation = useMutation({
    mutationFn: ({ id, title }: { id: number; title: string }) =>
      recipesApi.updateRecipeTitle(id, { title }, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      toast.success("Recipe renamed successfully");
      setRenameDialogOpen(false);
      setRecipeToRename(null);
      setNewTitle("");
    },
    onError: () => {
      toast.error("Failed to rename recipe");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => recipesApi.deleteRecipe(id, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      toast.success("Recipe deleted successfully");
      if (selectedRecipe && selectedRecipe.id === deleteMutation.variables) {
        setSelectedRecipe(null);
      }
    },
    onError: () => {
      toast.error("Failed to delete recipe");
    },
  });

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
      setDeleteRecipeDialogOpen(false);
      setRecipeToDelete(null);
    }
  };

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

  const handleNewRecipe = () => {
    setSelectedRecipe(null);
    setShowUploadView(true);
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
      setDeleteCategoryDialogOpen(false);
      setCategoryToDelete(null);
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

  return (
    <div className="flex h-screen bg-gradient-subtle overflow-hidden">
      {/* Sidebar */}
      <aside className="w-80 bg-card border-r border-border/50 shadow-lg flex flex-col">
        {/* Sidebar Header */}
        <div className="p-6 border-b border-border/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
              <ChefHat className="h-6 w-6 text-primary-foreground" />
            </div>
            <h1 className="text-xl font-bold text-foreground">
              Recipe Suggester
            </h1>
          </div>
        </div>

        {/* Sidebar Content - Recipe History */}
        <nav className="flex-1 p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Recipe History
            </h2>
            <Button
              onClick={handleNewRecipe}
              size="sm"
              className="gap-1"
            >
              <Plus className="h-4 w-4" />
              New Recipe
            </Button>
          </div>

          {/* Category Management */}
          <div className="mb-4 space-y-2">
            <Label className="text-xs">Category</Label>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="w-full justify-start gap-2">
                  <Tags className="h-4 w-4" />
                  Manage Categories
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56">
                <DropdownMenuItem onClick={handleCreateCategory}>
                  <FolderPlus className="h-4 w-4 mr-2" />
                  New Category
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setFilterCategoryId(null)}>
                  <Tags className="h-4 w-4 mr-2" />
                  All Recipes
                  {filterCategoryId === null && <Check className="h-4 w-4 ml-auto" />}
                </DropdownMenuItem>
                {categories && categories.length > 0 && (
                  <>
                    <DropdownMenuSeparator />
                    {categories.map((category) => (
                      <DropdownMenuItem
                        key={category.id}
                        className="flex items-center justify-between group"
                        onSelect={(e) => e.preventDefault()}
                        onClick={() => setFilterCategoryId(category.id)}
                      >
                        <span className="flex items-center gap-2 flex-1">
                          {category.name}
                          {filterCategoryId === category.id && <Check className="h-4 w-4" />}
                        </span>
                        <div className="flex gap-1 opacity-0 group-hover:opacity-100">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRenameCategory(category);
                            }}
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 text-destructive hover:text-destructive hover:bg-destructive/10"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteCategory(category.id);
                            }}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </DropdownMenuItem>
                    ))}
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Assign Category to Selected */}
            {selectedRecipes.size > 0 && (
              <div className="flex gap-2">
                <Select onValueChange={(value) => handleAssignCategory(value === "none" ? null : parseInt(value))}>
                  <SelectTrigger className="h-8 text-xs">
                    <SelectValue placeholder={`Assign ${selectedRecipes.size} recipe(s)`} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Remove Category</SelectItem>
                    {categories?.map((category) => (
                      <SelectItem key={category.id} value={category.id.toString()}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2"
                  onClick={() => setSelectedRecipes(new Set())}
                >
                  Clear
                </Button>
              </div>
            )}
          </div>
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Loading recipes...</div>
          ) : recipes && recipes.length > 0 ? (
            <div className="space-y-1">
              {recipes.map((recipe) => (
                <div
                  key={recipe.id}
                  className={`group flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                    selectedRecipe?.id === recipe.id && !showUploadView
                      ? "bg-muted"
                      : "hover:bg-muted/50"
                  }`}
                >
                  <Checkbox
                    checked={selectedRecipes.has(recipe.id)}
                    onCheckedChange={() => toggleRecipeSelection(recipe.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <div
                    className="flex items-center justify-between flex-1 min-w-0"
                    onClick={() => {
                      setSelectedRecipe(recipe);
                      setShowUploadView(false);
                    }}
                  >
                    <span className="text-sm font-medium truncate flex-1">
                      {recipe.title}
                    </span>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleRename(recipe)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Rename
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleDelete(recipe)}
                          className="text-destructive"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">No recipes yet</div>
          )}
        </nav>

        {/* Sidebar Footer - User Info */}
        <div className="p-4 border-t border-border/50">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold">
              {(user?.full_name || user?.email || "U")[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">
                {user?.full_name || user?.email}
              </p>
            </div>
          </div>
          <Button
            onClick={handleLogout}
            variant="outline"
            size="sm"
            className="w-full gap-2"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 p-8 overflow-y-auto">
          {showUploadView ? (
            <div className="h-full flex flex-col">
              <h2 className="text-3xl font-bold text-foreground mb-6">
                Create new recipe
              </h2>
              <div className="flex-1 border-2 border-dashed border-border rounded-xl p-12 flex flex-col items-center justify-center">
                <ChefHat className="h-16 w-16 text-muted-foreground mb-4" />
                <p className="text-lg font-semibold text-foreground mb-2">
                  Upload Fridge Image
                </p>
                <p className="text-sm text-muted-foreground mb-6">
                  Drag and drop an image here, or click to select
                </p>
                <Button>Choose File</Button>
              </div>
            </div>
          ) : selectedRecipe ? (
            <div className="h-full flex flex-col">
              <h2 className="text-3xl font-bold text-foreground mb-6">
                {selectedRecipe.title}
              </h2>
              <div className="space-y-6">
                <div>
                  <p className="text-sm font-semibold text-muted-foreground">Recipe ID</p>
                  <p className="text-lg text-foreground">{selectedRecipe.id}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-muted-foreground">Created At</p>
                  <p className="text-lg text-foreground">
                    {new Date(selectedRecipe.created_at).toLocaleString()}
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
          ) : (
            <div className="h-full flex flex-col items-center justify-center">
              <ChefHat className="h-24 w-24 text-muted-foreground mb-6" />
              <h2 className="text-3xl font-bold text-foreground mb-4">
                Welcome to Recipe Suggester
              </h2>
              <p className="text-muted-foreground text-lg">
                Select a recipe from the sidebar or create a new one
              </p>
            </div>
          )}
        </main>
      </div>

      {/* Rename Recipe Dialog */}
      <Dialog open={renameDialogOpen} onOpenChange={setRenameDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename Recipe</DialogTitle>
            <DialogDescription>
              Enter a new title for "{recipeToRename?.title}"
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="title" className="mb-2">
              Recipe Title
            </Label>
            <Input
              id="title"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleRenameSubmit();
                }
              }}
              placeholder="Enter recipe title"
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setRenameDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleRenameSubmit}
              disabled={!newTitle.trim() || renameMutation.isPending}
            >
              {renameMutation.isPending ? "Renaming..." : "Rename"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Category Dialog */}
      <Dialog open={categoryDialogOpen} onOpenChange={setCategoryDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {categoryAction === 'create' ? 'Create Category' : 'Rename Category'}
            </DialogTitle>
            <DialogDescription>
              {categoryAction === 'create'
                ? 'Enter a name for the new category'
                : 'Enter a new name for the category'}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="category-name" className="mb-2">
              Category Name
            </Label>
            <Input
              id="category-name"
              value={categoryName}
              onChange={(e) => setCategoryName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleCategorySubmit();
                }
              }}
              placeholder="Enter category name"
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setCategoryDialogOpen(false);
                setCategoryName("");
                setSelectedCategoryId(null);
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCategorySubmit}
              disabled={!categoryName.trim() || createCategoryMutation.isPending || updateCategoryMutation.isPending}
            >
              {createCategoryMutation.isPending || updateCategoryMutation.isPending
                ? "Saving..."
                : categoryAction === 'create'
                ? "Create"
                : "Rename"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Recipe Confirmation Dialog */}
      <Dialog open={deleteRecipeDialogOpen} onOpenChange={setDeleteRecipeDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Recipe</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{recipeToDelete?.title}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDeleteRecipeDialogOpen(false);
                setRecipeToDelete(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDeleteRecipe}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Category Confirmation Dialog */}
      <Dialog open={deleteCategoryDialogOpen} onOpenChange={setDeleteCategoryDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Category</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this category? Recipes in this category will not be deleted, but will be unassigned.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDeleteCategoryDialogOpen(false);
                setCategoryToDelete(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDeleteCategory}
              disabled={deleteCategoryMutation.isPending}
            >
              {deleteCategoryMutation.isPending ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Dashboard;
