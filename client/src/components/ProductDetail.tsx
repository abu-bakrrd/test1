import { Heart, ShoppingCart, ArrowLeft, Check, Image as ImageIcon } from "lucide-react";
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
  isInCart?: boolean;
  onToggleFavorite?: (id: string) => void;
  onAddToCart?: (id: string) => void;
  onBack?: () => void;
  onCartClick?: () => void;
}

export default function ProductDetail({
  id,
  name,
  description,
  price,
  images,
  isFavorite = false,
  isInCart = false,
  onToggleFavorite,
  onAddToCart,
  onBack,
  onCartClick,
}: ProductDetailProps) {
  const [currentImage, setCurrentImage] = useState(0);
  const [imageErrors, setImageErrors] = useState<Set<number>>(new Set());
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
    onToggleFavorite?.(id);
  };

  const handleCartAction = () => {
    if (isInCart) {
      onCartClick?.();
    } else {
      onAddToCart?.(id);
    }
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
        <div className="sticky top-0 z-20 bg-background/95 backdrop-blur-sm border-b px-4 py-3 flex items-center gap-3">
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
        <div className="p-4">
          <div
            className="relative aspect-square bg-muted rounded-xl overflow-hidden"
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
          >
            <div className="relative w-full h-full">
              {images.map((img, idx) => (
                imageErrors.has(idx) ? (
                  <div
                    key={idx}
                    className={`absolute inset-0 w-full h-full flex items-center justify-center transition-opacity duration-300 ${
                      idx === currentImage ? "opacity-100" : "opacity-0"
                    }`}
                  >
                    <ImageIcon className="w-20 h-20 text-muted-foreground/40" />
                  </div>
                ) : (
                  <img
                    key={idx}
                    src={img}
                    alt={name}
                    className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-300 ${
                      idx === currentImage ? "opacity-100" : "opacity-0"
                    }`}
                    onError={() => {
                      setImageErrors(prev => new Set(prev).add(idx));
                    }}
                  />
                )
              ))}
            </div>
            
            {/* Favorite Button */}
            <button
              onClick={handleFavorite}
              className="absolute top-3 left-3 w-9 h-9 rounded-full bg-background/80 backdrop-blur-sm flex items-center justify-center z-10"
              data-testid="button-toggle-favorite"
            >
              <Heart
                className={`w-5 h-5 ${isFavorite ? "fill-red-500 text-red-500" : "text-foreground"}`}
              />
            </button>

            {/* Image Indicators */}
            {images.length > 1 && (
              <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1 z-10">
                {images.map((_, idx) => (
                  <div
                    key={idx}
                    className={`h-1.5 rounded-full transition-all duration-300 ${
                      idx === currentImage 
                        ? "w-4 bg-foreground" 
                        : "w-1.5 bg-foreground/30"
                    }`}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Product Info */}
        <div className="px-4 space-y-4">
          <div>
            <h1 className="text-2xl font-bold mb-2" data-testid="text-product-detail-name">
              {name}
            </h1>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold text-foreground" data-testid="text-product-detail-price">
                {price.toLocaleString()}
              </p>
              <span className="text-lg text-muted-foreground">сум</span>
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
            onClick={handleCartAction}
            className="w-full gap-2 h-12"
            size="lg"
            variant={isInCart ? "default" : "default"}
            data-testid="button-add-to-cart-detail"
          >
            {isInCart ? (
              <>
                <Check className="w-5 h-5" />
                Перейти в корзину
              </>
            ) : (
              <>
                <ShoppingCart className="w-5 h-5" />
                Добавить в корзину
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
