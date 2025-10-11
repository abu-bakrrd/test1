import { Heart, ShoppingCart, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useRef } from "react";

interface ProductDetailProps {
  id: string;
  name: string;
  description: string;
  price: number;
  images: string[];
  isFavorite?: boolean;
  onToggleFavorite?: (id: string) => void;
  onAddToCart?: (id: string) => void;
  onBack?: () => void;
}

export default function ProductDetail({
  id,
  name,
  description,
  price,
  images,
  isFavorite = false,
  onToggleFavorite,
  onAddToCart,
  onBack,
}: ProductDetailProps) {
  const [currentImage, setCurrentImage] = useState(0);
  const [favorite, setFavorite] = useState(isFavorite);
  const touchStartX = useRef(0);
  const touchEndX = useRef(0);

  const nextImage = () => {
    setCurrentImage((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentImage((prev) => (prev - 1 + images.length) % images.length);
  };

  const handleFavorite = () => {
    setFavorite(!favorite);
    onToggleFavorite?.(id);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    touchEndX.current = e.touches[0].clientX;
  };

  const handleTouchEnd = () => {
    const swipeDistance = touchStartX.current - touchEndX.current;
    const minSwipeDistance = 50;

    if (Math.abs(swipeDistance) > minSwipeDistance) {
      if (swipeDistance > 0) {
        nextImage();
      } else {
        prevImage();
      }
    }

    touchStartX.current = 0;
    touchEndX.current = 0;
  };

  return (
    <div className="max-w-[420px] mx-auto" data-testid="product-detail">
      {/* Image Gallery */}
      <div
        className="relative aspect-square bg-muted"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        <img
          src={images[currentImage]}
          alt={name}
          className="w-full h-full object-cover"
        />
        
        {images.length > 1 && (
          <>
            <Button
              size="icon"
              variant="ghost"
              onClick={prevImage}
              className="absolute left-2 top-1/2 -translate-y-1/2 bg-background/80 h-8 w-8"
              data-testid="button-prev-image"
            >
              <ChevronLeft className="w-5 h-5" />
            </Button>
            
            <Button
              size="icon"
              variant="ghost"
              onClick={nextImage}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-background/80 h-8 w-8"
              data-testid="button-next-image"
            >
              <ChevronRight className="w-5 h-5" />
            </Button>

            <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1">
              {images.map((_, idx) => (
                <div
                  key={idx}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    idx === currentImage ? "bg-foreground" : "bg-foreground/30"
                  }`}
                />
              ))}
            </div>
          </>
        )}
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <h1 className="text-xl font-semibold mb-2" data-testid="text-product-detail-name">
              {name}
            </h1>
            <p className="text-2xl font-bold text-primary" data-testid="text-product-detail-price">
              {price.toLocaleString()} сум
            </p>
          </div>
          
          <Button
            size="icon"
            variant="outline"
            onClick={handleFavorite}
            data-testid="button-toggle-favorite"
          >
            <Heart
              className={`w-5 h-5 ${favorite ? "fill-primary text-primary" : ""}`}
            />
          </Button>
        </div>

        <p className="text-sm text-muted-foreground mb-6" data-testid="text-product-description">
          {description}
        </p>

        <Button
          onClick={() => onAddToCart?.(id)}
          className="w-full gap-2"
          data-testid="button-add-to-cart-detail"
        >
          <ShoppingCart className="w-5 h-5" />
          Добавить в корзину
        </Button>
      </div>
    </div>
  );
}
