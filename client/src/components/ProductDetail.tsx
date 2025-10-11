import { Heart, ShoppingCart, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
  const touchStartY = useRef(0);
  const isSwiping = useRef(false);

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
    touchStartY.current = e.touches[0].clientY;
    isSwiping.current = false;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    touchEndX.current = e.touches[0].clientX;
    
    const swipeDistance = Math.abs(touchStartX.current - touchEndX.current);
    const verticalDistance = Math.abs(touchStartY.current - e.touches[0].clientY);
    
    if (swipeDistance > 10 && swipeDistance > verticalDistance) {
      isSwiping.current = true;
    }
  };

  const handleTouchEnd = () => {
    const swipeDistance = touchStartX.current - touchEndX.current;
    const minSwipeDistance = 50;

    if (isSwiping.current && Math.abs(swipeDistance) > minSwipeDistance) {
      if (swipeDistance > 0) {
        nextImage();
      } else {
        prevImage();
      }
    }

    isSwiping.current = false;
    touchStartX.current = 0;
    touchEndX.current = 0;
  };

  return (
    <div className="min-h-screen bg-background pb-6" data-testid="product-detail">
      <div className="max-w-[420px] mx-auto">
        {/* Back Button Header */}
        <div className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm border-b px-4 py-3 flex items-center gap-3">
          <Button
            size="icon"
            variant="ghost"
            onClick={onBack}
            data-testid="button-back"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h2 className="text-lg font-semibold">Детали товара</h2>
        </div>

        {/* Image Gallery */}
        <div
          className="relative aspect-square bg-muted"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          <div className="relative w-full h-full">
            {images.map((img, idx) => (
              <img
                key={idx}
                src={img}
                alt={name}
                className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-300 ${
                  idx === currentImage ? "opacity-100" : "opacity-0"
                }`}
              />
            ))}
          </div>
          
          {/* Image Indicators */}
          {images.length > 1 && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1.5">
              {images.map((_, idx) => (
                <div
                  key={idx}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    idx === currentImage 
                      ? "w-8 bg-foreground" 
                      : "w-1.5 bg-foreground/40"
                  }`}
                />
              ))}
            </div>
          )}

          {/* Favorite Button Overlay */}
          <Button
            size="icon"
            variant="ghost"
            onClick={handleFavorite}
            className="absolute top-3 right-3 bg-background/90 backdrop-blur-sm"
            data-testid="button-toggle-favorite"
          >
            <Heart
              className={`w-5 h-5 ${favorite ? "fill-primary text-primary" : ""}`}
            />
          </Button>
        </div>

        {/* Product Info */}
        <div className="p-4 space-y-4">
          <div>
            <h1 className="text-2xl font-bold mb-2" data-testid="text-product-detail-name">
              {name}
            </h1>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold text-primary" data-testid="text-product-detail-price">
                {price.toLocaleString()}
              </p>
              <span className="text-sm text-muted-foreground">сум</span>
            </div>
          </div>

          <div className="border-t pt-4">
            <h3 className="text-sm font-semibold mb-2">Описание</h3>
            <p className="text-sm text-muted-foreground leading-relaxed" data-testid="text-product-description">
              {description}
            </p>
          </div>

          {/* Action Button */}
          <Button
            onClick={() => onAddToCart?.(id)}
            className="w-full gap-2 h-12"
            size="lg"
            data-testid="button-add-to-cart-detail"
          >
            <ShoppingCart className="w-5 h-5" />
            Добавить в корзину
          </Button>
        </div>
      </div>
    </div>
  );
}
