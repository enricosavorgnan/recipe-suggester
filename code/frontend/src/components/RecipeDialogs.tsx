import { Button } from "@/components/ui/button";
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
import { Recipe } from "@/api/recipes";
import { Category } from "@/api/categories";

interface RenameRecipeDialogProps {
  open: boolean;
  recipe: Recipe | null;
  newTitle: string;
  isPending: boolean;
  onOpenChange: (open: boolean) => void;
  onTitleChange: (title: string) => void;
  onSubmit: () => void;
}

export const RenameRecipeDialog = ({
  open,
  recipe,
  newTitle,
  isPending,
  onOpenChange,
  onTitleChange,
  onSubmit,
}: RenameRecipeDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Rename Recipe</DialogTitle>
          <DialogDescription>
            Enter a new title for "{recipe?.title}"
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <Label htmlFor="title" className="mb-2">
            Recipe Title
          </Label>
          <Input
            id="title"
            value={newTitle}
            onChange={(e) => onTitleChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onSubmit();
              }
            }}
            placeholder="Enter recipe title"
            autoFocus
          />
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>
          <Button
            onClick={onSubmit}
            disabled={!newTitle.trim() || isPending}
          >
            {isPending ? "Renaming..." : "Rename"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

interface DeleteRecipeDialogProps {
  open: boolean;
  recipe: Recipe | null;
  isPending: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
}

export const DeleteRecipeDialog = ({
  open,
  recipe,
  isPending,
  onOpenChange,
  onConfirm,
}: DeleteRecipeDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Recipe</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete "{recipe?.title}"? This action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={isPending}
          >
            {isPending ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

interface CategoryDialogProps {
  open: boolean;
  action: 'create' | 'rename' | null;
  categoryName: string;
  isPending: boolean;
  onOpenChange: (open: boolean) => void;
  onNameChange: (name: string) => void;
  onSubmit: () => void;
}

export const CategoryDialog = ({
  open,
  action,
  categoryName,
  isPending,
  onOpenChange,
  onNameChange,
  onSubmit,
}: CategoryDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {action === 'create' ? 'Create Category' : 'Rename Category'}
          </DialogTitle>
          <DialogDescription>
            {action === 'create'
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
            onChange={(e) => onNameChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onSubmit();
              }
            }}
            placeholder="Enter category name"
            autoFocus
          />
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>
          <Button
            onClick={onSubmit}
            disabled={!categoryName.trim() || isPending}
          >
            {isPending
              ? "Saving..."
              : action === 'create'
              ? "Create"
              : "Rename"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

interface DeleteCategoryDialogProps {
  open: boolean;
  isPending: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
}

export const DeleteCategoryDialog = ({
  open,
  isPending,
  onOpenChange,
  onConfirm,
}: DeleteCategoryDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
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
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={isPending}
          >
            {isPending ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
