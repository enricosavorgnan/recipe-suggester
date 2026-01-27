import { Edit, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Ingredient {
  name: string;
  confidence?: number;
}

interface IngredientItemProps {
  ingredient: Ingredient;
  onEdit: () => void;
  onDelete: () => void;
}

export const IngredientItem = ({ ingredient, onEdit, onDelete }: IngredientItemProps) => {
  const getConfidenceColor = (confidence?: number): string => {
    if (!confidence) return "text-muted-foreground";
    if (confidence >= 0.75) return "text-green-600";
    if (confidence >= 0.5) return "text-yellow-600";
    return "text-red-600";
  };

  const getConfidenceBgColor = (confidence?: number): string => {
    if (!confidence) return "bg-muted";
    if (confidence >= 0.75) return "bg-green-100";
    if (confidence >= 0.5) return "bg-yellow-100";
    return "bg-red-100";
  };

  return (
    <div className="flex items-center justify-between gap-3 p-3 bg-card rounded-lg border border-border shadow-sm group hover:shadow-md hover:border-border/80 transition-all">
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <span className="text-sm font-medium text-foreground truncate">
          {ingredient.name}
        </span>
        {ingredient.confidence !== undefined && (
          <span
            className={`text-xs font-semibold px-2 py-0.5 rounded-full ${getConfidenceColor(ingredient.confidence)} ${getConfidenceBgColor(ingredient.confidence)}`}
          >
            {Math.round(ingredient.confidence * 100)}%
          </span>
        )}
      </div>
      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="sm"
          className="h-7 w-7 p-0"
          onClick={onEdit}
        >
          <Edit className="h-3.5 w-3.5" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="h-7 w-7 p-0 text-destructive hover:text-destructive hover:bg-destructive/10"
          onClick={onDelete}
        >
          <Trash2 className="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>
  );
};
