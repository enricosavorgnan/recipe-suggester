import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { LogOut, ChefHat, MoreVertical, Edit, Trash2 } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import recipesApi, { Recipe } from "@/api/recipes";
import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

const Dashboard = () => {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [recipeToRename, setRecipeToRename] = useState<Recipe | null>(null);
  const [newTitle, setNewTitle] = useState("");

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Fetch recipes
  const { data: recipes, isLoading } = useQuery({
    queryKey: ["recipes"],
    queryFn: () => recipesApi.getRecipes(token!),
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
    if (confirm(`Are you sure you want to delete "${recipe.title}"?`)) {
      deleteMutation.mutate(recipe.id);
    }
  };

  return (
    <div className="flex min-h-screen bg-gradient-subtle">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-border/50 shadow-lg flex flex-col">
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
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
            Recipe History
          </h2>
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Loading recipes...</div>
          ) : recipes && recipes.length > 0 ? (
            <div className="space-y-1">
              {recipes.map((recipe) => (
                <div
                  key={recipe.id}
                  className={`group flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors ${
                    selectedRecipe?.id === recipe.id
                      ? "bg-primary/10 text-primary"
                      : "hover:bg-accent text-foreground"
                  }`}
                  onClick={() => setSelectedRecipe(recipe)}
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
      <div className="flex-1 flex flex-col">
        <main className="flex-1 p-8">
          {selectedRecipe ? (
            <div className="bg-card rounded-2xl shadow-card p-8 border border-border/50">
              <h2 className="text-3xl font-bold text-foreground mb-6">
                {selectedRecipe.title}
              </h2>
              <div className="space-y-4">
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
                <div>
                  <p className="text-sm font-semibold text-muted-foreground">Last Updated</p>
                  <p className="text-lg text-foreground">
                    {new Date(selectedRecipe.updated_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-card rounded-2xl shadow-card p-8 border border-border/50">
              <h2 className="text-3xl font-bold text-foreground mb-4">
                Welcome to Recipe Suggester
              </h2>
              <p className="text-muted-foreground text-lg">
                Select a recipe from the sidebar to view details
              </p>
            </div>
          )}
        </main>
      </div>

      {/* Rename Dialog */}
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
    </div>
  );
};

export default Dashboard;
