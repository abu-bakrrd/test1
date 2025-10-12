import { useState, useEffect } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./lib/queryClient";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { TelegramProvider } from "@/contexts/TelegramContext";
import Home from "@/pages/Home";
import Cart from "@/pages/Cart";
import Favorites from "@/pages/Favorites";
import Product from "@/pages/Product";

//todo: remove mock functionality
interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  images: string[];
}

interface FavoriteItem {
  id: string;
  name: string;
  price: number;
  images: string[];
  isFavorite: boolean;
}

type Page = 'home' | 'cart' | 'favorites' | 'product';

// Mock products data for getting product info
const mockProductsData: Record<string, { name: string; price: number; images: string[] }> = {
  '1': { name: 'Букет красных роз', price: 150000, images: ['https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=400&fit=crop'] },
  '2': { name: 'Розовые тюльпаны', price: 90000, images: ['https://images.unsplash.com/photo-1520763185298-1b434c919102?w=400&h=400&fit=crop'] },
  '3': { name: 'Белые пионы', price: 120000, images: ['https://images.unsplash.com/photo-1591886960571-74d43a9d4166?w=400&h=400&fit=crop'] },
  '4': { name: 'Букет полевых цветов', price: 75000, images: ['https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=400&h=400&fit=crop'] },
  '5': { name: 'Фиолетовые лаванды', price: 85000, images: ['https://images.unsplash.com/photo-1499002238440-d264edd596ec?w=400&h=400&fit=crop'] },
  '6': { name: 'Желтые герберы', price: 95000, images: ['https://images.unsplash.com/photo-1477414348463-c0eb7f1359b6?w=400&h=400&fit=crop'] },
  '7': { name: 'Розовые пионы', price: 130000, images: ['https://images.unsplash.com/photo-1588509095738-c342c5d917d2?w=400&h=400&fit=crop'] },
  '8': { name: 'Подсолнухи', price: 70000, images: ['https://images.unsplash.com/photo-1597848212624-e30b9aeb6394?w=400&h=400&fit=crop'] },
  '9': { name: 'Белые розы', price: 140000, images: ['https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=400&h=400&fit=crop'] },
  '10': { name: 'Сиреневые хризантемы', price: 100000, images: ['https://images.unsplash.com/photo-1563535655-c6d52fdf3a89?w=400&h=400&fit=crop'] },
  '11': { name: 'Смешанный букет', price: 110000, images: ['https://images.unsplash.com/photo-1487070183336-b863922373d4?w=400&h=400&fit=crop'] },
  '12': { name: 'Орхидеи', price: 160000, images: ['https://images.unsplash.com/photo-1584714268709-c3dd9c92b378?w=400&h=400&fit=crop'] },
};

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  
  // Load from localStorage
  const [cartItems, setCartItems] = useState<CartItem[]>(() => {
    const saved = localStorage.getItem('flowery-bloom-cart');
    return saved ? JSON.parse(saved) : [];
  });
  
  const [favoriteItems, setFavoriteItems] = useState<FavoriteItem[]>(() => {
    const saved = localStorage.getItem('flowery-bloom-favorites');
    return saved ? JSON.parse(saved) : [];
  });

  // Save to localStorage
  useEffect(() => {
    localStorage.setItem('flowery-bloom-cart', JSON.stringify(cartItems));
  }, [cartItems]);

  useEffect(() => {
    localStorage.setItem('flowery-bloom-favorites', JSON.stringify(favoriteItems));
  }, [favoriteItems]);

  const handleAddToCart = (id: string) => {
    const existingItem = cartItems.find(item => item.id === id);
    
    if (existingItem) {
      setCartItems(cartItems.map(item =>
        item.id === id ? { ...item, quantity: item.quantity + 1 } : item
      ));
    } else {
      const productData = mockProductsData[id];
      if (productData) {
        setCartItems([...cartItems, {
          id,
          ...productData,
          quantity: 1,
        }]);
      }
    }
  };

  const handleToggleFavorite = (id: string) => {
    const isFavorite = favoriteItems.some(item => item.id === id);
    
    if (isFavorite) {
      setFavoriteItems(favoriteItems.filter(item => item.id !== id));
    } else {
      const productData = mockProductsData[id];
      if (productData) {
        setFavoriteItems([...favoriteItems, {
          id,
          ...productData,
          isFavorite: true,
        }]);
      }
    }
  };

  const handleProductClick = (id: string) => {
    setSelectedProductId(id);
    setCurrentPage('product');
  };

  const handleQuantityChange = (id: string, quantity: number) => {
    setCartItems(cartItems.map(item =>
      item.id === id ? { ...item, quantity } : item
    ));
  };

  const handleRemoveItem = (id: string) => {
    setCartItems(cartItems.filter(item => item.id !== id));
  };

  const handleClearCart = () => {
    setCartItems([]);
  };

  const handleClearFavorites = () => {
    setFavoriteItems([]);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <TelegramProvider>
          <div className="max-w-[420px] mx-auto bg-background min-h-screen">
            {currentPage === 'home' && (
              <Home
                onCartClick={() => setCurrentPage('cart')}
                onFavoritesClick={() => setCurrentPage('favorites')}
                onProductClick={handleProductClick}
                cartCount={cartItems.reduce((sum, item) => sum + item.quantity, 0)}
                favoritesCount={favoriteItems.length}
                onAddToCart={handleAddToCart}
                onToggleFavorite={handleToggleFavorite}
                favoriteIds={favoriteItems.map(item => item.id)}
                cartItemIds={cartItems.map(item => item.id)}
              />
            )}
            
            {currentPage === 'cart' && (
              <Cart
                items={cartItems}
                onBack={() => setCurrentPage('home')}
                onQuantityChange={handleQuantityChange}
                onRemoveItem={handleRemoveItem}
                onClearCart={handleClearCart}
              />
            )}
            
            {currentPage === 'favorites' && (
              <Favorites
                items={favoriteItems}
                onBack={() => setCurrentPage('home')}
                onClearAll={handleClearFavorites}
                onToggleFavorite={handleToggleFavorite}
                onAddToCart={handleAddToCart}
                onProductClick={handleProductClick}
              />
            )}
            
            {currentPage === 'product' && (
              <Product
                productId={selectedProductId}
                onBack={() => setCurrentPage('home')}
                onAddToCart={handleAddToCart}
                onToggleFavorite={handleToggleFavorite}
                isFavorite={favoriteItems.some(item => item.id === selectedProductId)}
                isInCart={cartItems.some(item => item.id === selectedProductId)}
                onCartClick={() => setCurrentPage('cart')}
              />
            )}
          </div>
          <Toaster />
        </TelegramProvider>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
