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

interface AddIngredientDialogProps {
  open: boolean;
  ingredientName: string;
  onOpenChange: (open: boolean) => void;
  onNameChange: (name: string) => void;
  onSubmit: () => void;
}

export const AddIngredientDialog = ({
  open,
  ingredientName,
  onOpenChange,
  onNameChange,
  onSubmit,
}: AddIngredientDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Ingredient</DialogTitle>
          <DialogDescription>
            Enter the name of the ingredient you want to add
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <Label htmlFor="ingredient-name" className="mb-2">
            Ingredient Name
          </Label>
          <Input
            id="ingredient-name"
            value={ingredientName}
            onChange={(e) => onNameChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onSubmit();
              }
            }}
            placeholder="e.g., Tomato"
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
            disabled={!ingredientName.trim()}
          >
            Add
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

interface EditIngredientDialogProps {
  open: boolean;
  ingredientName: string;
  onOpenChange: (open: boolean) => void;
  onNameChange: (name: string) => void;
  onSubmit: () => void;
}

export const EditIngredientDialog = ({
  open,
  ingredientName,
  onOpenChange,
  onNameChange,
  onSubmit,
}: EditIngredientDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Ingredient</DialogTitle>
          <DialogDescription>
            Update the name of the ingredient
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <Label htmlFor="edit-ingredient-name" className="mb-2">
            Ingredient Name
          </Label>
          <Input
            id="edit-ingredient-name"
            value={ingredientName}
            onChange={(e) => onNameChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onSubmit();
              }
            }}
            placeholder="e.g., Tomato"
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
            disabled={!ingredientName.trim()}
          >
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

interface DeleteIngredientDialogProps {
  open: boolean;
  ingredientName: string;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
}

export const DeleteIngredientDialog = ({
  open,
  ingredientName,
  onOpenChange,
  onConfirm,
}: DeleteIngredientDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Ingredient</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete "{ingredientName}"? This action cannot be undone.
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
          >
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
