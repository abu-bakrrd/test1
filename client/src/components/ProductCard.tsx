import { Heart, ShoppingCart, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useRef } from "react";

interface ProductCardProps {
  id: string;
  name: string;
  price: number;
  images: string[];
  isFavorite?: boolean;
  isInCart?: boolean;
  onToggleFavorite?: (id: string) => void;
  onAddToCart?: (id: string) => void;
  onClick?: (id: string) => void;
  onCartClick?: () => void;
}

export default function ProductCard({
  id,
  name,
  price,
  images,
  isFavorite = false,
  isInCart = false,
  onToggleFavorite,
  onAddToCart,
  onClick,
  onCartClick,
}: ProductCardProps) {
  const [currentImage, setCurrentImage] = useState(0);
  const touchStartX = useRef(0);
  const touchEndX = useRef(0);

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleFavorite?.(id);
  };

  const handleCartClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isInCart) {
      onCartClick?.();
    } else {
      onAddToCart?.(id);
    }
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    touchEndX.current = e.touches[0].clientX;
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.stopPropagation();
    
    const swipeDistance = touchStartX.current - touchEndX.current;
    const minSwipeDistance = 50;

    if (Math.abs(swipeDistance) > minSwipeDistance) {
      if (swipeDistance > 0) {
        setCurrentImage((prev) => (prev + 1) % images.length);
      } else {
        setCurrentImage((prev) => (prev - 1 + images.length) % images.length);
      }
    }

    touchStartX.current = 0;
    touchEndX.current = 0;
  };

  return (
    <div
      onClick={() => onClick?.(id)}
      className="bg-card rounded-md border border-card-border overflow-hidden cursor-pointer"
      data-testid={`card-product-${id}`}
    >
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
          loading="lazy"
        />
        <button
          onClick={handleFavoriteClick}
          className="absolute top-2 left-2 w-8 h-8 rounded-full bg-background/80 flex items-center justify-center z-10"
          data-testid={`button-favorite-${id}`}
        >
          <Heart
            className={`w-5 h-5 ${isFavorite ? "fill-red-500 text-red-500" : "text-foreground"}`}
          />
        </button>
        
        {images.length > 1 && (
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1 z-10">
            {images.map((_, idx) => (
              <div
                key={idx}
                className={`w-1.5 h-1.5 rounded-full transition-colors ${
                  idx === currentImage ? "bg-foreground" : "bg-foreground/30"
                }`}
              />
            ))}
          </div>
        )}
      </div>
      
      <div className="p-3">
        <h3 className="text-sm font-medium text-foreground line-clamp-2 mb-1" data-testid={`text-product-name-${id}`}>
          {name}
        </h3>
        <div className="flex items-center justify-between">
          <p className="text-base font-semibold text-foreground" data-testid={`text-product-price-${id}`}>
            {price.toLocaleString()} сум
          </p>
          <Button
            size="icon"
            variant={isInCart ? "default" : "ghost"}
            onClick={handleCartClick}
            className="h-8 w-8"
            data-testid={`button-add-to-cart-${id}`}
          >
            {isInCart ? (
              <Check className="w-4 h-4" />
            ) : (
              <ShoppingCart className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
