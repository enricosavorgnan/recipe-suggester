import { useState, useEffect, useRef } from "react";
import { ChefHat, Loader2, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useMutation } from "@tanstack/react-query";
import recipesApi from "@/api/recipes";
import jobsApi, { IngredientsJob } from "@/api/jobs";
import { toast } from "sonner";

interface ImageUploadProps {
  token: string;
  onJobComplete?: (job: IngredientsJob) => void;
  onRecipeCreated?: () => void;
}

const loadingMessages = [
  "Scanning the image...",
  "Preparing the list of ingredients...",
];

export const ImageUpload = ({ token, onJobComplete, onRecipeCreated }: ImageUploadProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [confirmUploadOpen, setConfirmUploadOpen] = useState(false);
  const [currentJob, setCurrentJob] = useState<IngredientsJob | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Upload mutations
  const createRecipeMutation = useMutation({
    mutationFn: () => recipesApi.createRecipe(token),
    onSuccess: () => {
      onRecipeCreated?.();
    },
    onError: () => {
      toast.error("Failed to create recipe");
    },
  });

  const uploadImageMutation = useMutation({
    mutationFn: ({ recipeId, file }: { recipeId: number; file: File }) =>
      recipesApi.uploadImage(recipeId, file, token),
    onError: () => {
      toast.error("Failed to upload image");
      setIsProcessing(false);
    },
  });

  const createJobMutation = useMutation({
    mutationFn: (recipeId: number) => jobsApi.createIngredientsJob(recipeId, token),
    onSuccess: (job) => {
      setCurrentJob(job);
      setIsProcessing(true);
    },
    onError: () => {
      toast.error("Failed to start ML job");
      setIsProcessing(false);
    },
  });

  // Rotating loading messages
  useEffect(() => {
    if (!isProcessing) return;

    const interval = setInterval(() => {
      setLoadingMessageIndex((prev) => (prev + 1) % loadingMessages.length);
    }, 2000);

    return () => clearInterval(interval);
  }, [isProcessing]);

  // Polling for job status
  useEffect(() => {
    if (!currentJob || !isProcessing) return;

    const pollInterval = setInterval(async () => {
      try {
        const job = await jobsApi.getIngredientsJob(currentJob.id, token);
        setCurrentJob(job);

        if (job.status !== 'running') {
          setIsProcessing(false);
          clearInterval(pollInterval);

          if (job.status === 'completed') {
            toast.success("Ingredients detected successfully!");
            onJobComplete?.(job);
          } else if (job.status === 'failed') {
            toast.error("Failed to detect ingredients");
          }
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 1000);

    return () => clearInterval(pollInterval);
  }, [currentJob, isProcessing, token, onJobComplete]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setConfirmUploadOpen(true);
    }
  };

  const handleConfirmUpload = async () => {
    if (!selectedFile) return;

    setConfirmUploadOpen(false);

    // Create recipe
    const recipe = await createRecipeMutation.mutateAsync();

    // Upload image
    await uploadImageMutation.mutateAsync({ recipeId: recipe.id, file: selectedFile });

    // Start ML job
    await createJobMutation.mutateAsync(recipe.id);

    // Clear file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleCancelUpload = () => {
    setConfirmUploadOpen(false);
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="h-full flex flex-col">
      <h2 className="text-3xl font-bold text-foreground mb-6">
        Create new recipe
      </h2>

      {isProcessing && previewUrl ? (
        <div className="flex flex-col items-center gap-6">
          <img
            src={previewUrl}
            alt="Uploaded"
            className="max-w-xs rounded-lg shadow-lg"
          />
          <div className="flex items-center gap-3">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
            <p className="text-lg font-medium text-foreground">
              {loadingMessages[loadingMessageIndex]}
            </p>
          </div>
        </div>
      ) : currentJob && currentJob.status === 'completed' ? (
        <div className="space-y-6">
          {previewUrl && (
            <div className="flex justify-center">
              <img
                src={previewUrl}
                alt="Uploaded"
                className="max-w-xs rounded-lg shadow-lg"
              />
            </div>
          )}
          <div>
            <h3 className="text-xl font-semibold text-foreground mb-4">
              Detected Ingredients (JSON)
            </h3>
            <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm">
              {JSON.stringify(JSON.parse(currentJob.ingredients_json || '{}'), null, 2)}
            </pre>
          </div>
        </div>
      ) : (
        <div className="flex-1 border-2 border-dashed border-border rounded-xl p-12 flex flex-col items-center justify-center">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
          />
          <ChefHat className="h-16 w-16 text-muted-foreground mb-4" />
          <p className="text-lg font-semibold text-foreground mb-2">
            Upload Fridge Image
          </p>
          <p className="text-sm text-muted-foreground mb-6">
            Click to select an image of your fridge or ingredients
          </p>
          <Button onClick={() => fileInputRef.current?.click()}>
            Choose File
          </Button>
        </div>
      )}

      {/* Upload Confirmation Dialog */}
      <Dialog open={confirmUploadOpen} onOpenChange={setConfirmUploadOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Confirm Image Upload</DialogTitle>
            <DialogDescription>
              Please review the image before starting ingredient detection
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-center py-4">
            {previewUrl && (
              <img
                src={previewUrl}
                alt="Preview"
                className="max-h-96 rounded-lg shadow-lg"
              />
            )}
          </div>
          <DialogFooter className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleCancelUpload}
            >
              <X className="h-4 w-4 mr-2" />
              Change Image
            </Button>
            <Button
              onClick={handleConfirmUpload}
              disabled={createRecipeMutation.isPending || uploadImageMutation.isPending || createJobMutation.isPending}
            >
              <Check className="h-4 w-4 mr-2" />
              {createRecipeMutation.isPending || uploadImageMutation.isPending || createJobMutation.isPending
                ? "Uploading..."
                : "Start Detection"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
