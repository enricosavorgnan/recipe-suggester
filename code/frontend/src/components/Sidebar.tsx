import { ChefHat, LogOut, MoreVertical, Edit, Trash2, Plus, Check, FolderPlus, Tags } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Recipe } from "@/api/recipes";
import { Category } from "@/api/categories";

interface SidebarProps {
  user: { full_name?: string; email?: string } | null;
  recipes: Recipe[] | undefined;
  categories: Category[] | undefined;
  isLoading: boolean;
  selectedRecipe: Recipe | null;
  selectedRecipes: Set<number>;
  filterCategoryId: number | null;
  onLogout: () => void;
  onNewRecipe: () => void;
  onSelectRecipe: (recipe: Recipe) => void;
  onRenameRecipe: (recipe: Recipe) => void;
  onDeleteRecipe: (recipe: Recipe) => void;
  onToggleRecipeSelection: (recipeId: number) => void;
  onCreateCategory: () => void;
  onRenameCategory: (category: Category) => void;
  onDeleteCategory: (categoryId: number) => void;
  onAssignCategory: (categoryId: number | null) => void;
  onClearSelection: () => void;
  onFilterCategory: (categoryId: number | null) => void;
}

export const Sidebar = ({
  user,
  recipes,
  categories,
  isLoading,
  selectedRecipe,
  selectedRecipes,
  filterCategoryId,
  onLogout,
  onNewRecipe,
  onSelectRecipe,
  onRenameRecipe,
  onDeleteRecipe,
  onToggleRecipeSelection,
  onCreateCategory,
  onRenameCategory,
  onDeleteCategory,
  onAssignCategory,
  onClearSelection,
  onFilterCategory,
}: SidebarProps) => {
  return (
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
            onClick={onNewRecipe}
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
              <DropdownMenuItem onClick={onCreateCategory}>
                <FolderPlus className="h-4 w-4 mr-2" />
                New Category
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onFilterCategory(null)}>
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
                      onClick={() => onFilterCategory(category.id)}
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
                            onRenameCategory(category);
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
                            onDeleteCategory(category.id);
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
              <Select onValueChange={(value) => onAssignCategory(value === "none" ? null : parseInt(value))}>
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
                onClick={onClearSelection}
              >
                Clear
              </Button>
            </div>
          )}
        </div>

        {/* Recipe List */}
        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading recipes...</div>
        ) : recipes && recipes.length > 0 ? (
          <div className="space-y-1">
            {recipes.map((recipe) => (
              <div
                key={recipe.id}
                className={`group flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                  selectedRecipe?.id === recipe.id
                    ? "bg-muted"
                    : "hover:bg-muted/50"
                }`}
              >
                <Checkbox
                  checked={selectedRecipes.has(recipe.id)}
                  onCheckedChange={() => onToggleRecipeSelection(recipe.id)}
                  onClick={(e) => e.stopPropagation()}
                />
                <div
                  className="flex items-center justify-between flex-1 min-w-0"
                  onClick={() => onSelectRecipe(recipe)}
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
                      <DropdownMenuItem onClick={() => onRenameRecipe(recipe)}>
                        <Edit className="h-4 w-4 mr-2" />
                        Rename
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => onDeleteRecipe(recipe)}
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
          onClick={onLogout}
          variant="outline"
          size="sm"
          className="w-full gap-2"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </aside>
  );
};
