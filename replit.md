# Universal E-Commerce Telegram Mini App Template

## Overview

This is a **universal template** for creating e-commerce Telegram Mini Apps. The application is fully configurable through JSON files, allowing anyone to create their own online shop by simply changing configuration files without touching the code.

**Design Philosophy:**
- Mobile-first interface (max-width: 420px)
- Flat, minimal design with customizable pastel color palette
- Touch-optimized interactions
- Light mode only with configurable color scheme

## Recent Changes

### October 26, 2025 (Latest) - Custom Fonts and Logo Sizing
- **Custom Fonts**: Added support for custom font files with configurable font-family and font-weight
- **Typography Control**: Separate font-weight settings for product names, prices, and descriptions
- **Dynamic Logo Sizing**: Configurable logo size with automatic proportion preservation
- **FontLoader Component**: Automatic @font-face injection for custom fonts with CSS variable system

### October 19, 2025 - Template Conversion
- **Universal Template**: Converted flower shop into configurable template for any e-commerce business
- **Configuration System**: Created `config/` folder with `settings.json` for all shop settings
- **Dynamic Branding**: Shop name, logo, and colors now loaded from config
- **Currency System**: Configurable currency symbol, code, and position (before/after price)
- **Sort Options**: Customizable sort options with emoji support from config
- **Manager Contact**: Configurable Telegram manager contact
- **Theme System**: Dynamic CSS variable injection based on color scheme in config
- **API Endpoints**: Added `/api/config` and `/config/<filename>` for serving configuration

### October 12, 2025
- **Pure Flask Architecture**: Simplified application to use only Flask (removed Node.js/Express dependency)
- **Static File Serving**: Configured Flask to serve pre-built React frontend from `dist/public/`
- **Telegram Mini App Database Integration**: Updated database schema for full Telegram authentication support

### November 8, 2025 - VPS Deployment Improvements
- **Auto-fix Permissions**: `deploy_vps.sh` now automatically configures Nginx permissions
- **New Script**: `fix_permissions.sh` for quick resolution of 403 Forbidden errors
- **Updated Scripts**: All deployment scripts now handle permissions correctly
- **Enhanced Documentation**: Added comprehensive VPS deployment guides in Russian

## 🚀 VPS Deployment Quick Start

### Deploy in 2 Commands

```bash
# 1. Clone repository on VPS
git clone <your-repo> /opt/monvoir-deploy
cd /opt/monvoir-deploy

# 2. Run auto-deployment
chmod +x deploy_vps.sh
sudo ./deploy_vps.sh
```

**Done!** The script automatically installs PostgreSQL, Nginx, Node.js, builds frontend, and configures everything.

### Available Scripts

| Script | Purpose |
|--------|---------|
| `deploy_vps.sh` | Initial deployment (all-in-one) |
| `update_vps.sh` | Update deployed application |
| `fix_permissions.sh` | Fix 403 Forbidden errors |
| `backup_db.sh` | Backup PostgreSQL database |
| `restore_db.sh` | Restore database from backup |

### VPS Documentation

- 📘 **Quick Start (RU)**: `QUICK_START_RU.md` ⭐
- 📗 **Full Guide**: `DEPLOY_TO_VPS_README.md`
- 📕 **Scripts Reference**: `VPS_SCRIPTS_README.md`
- 📙 **GitHub Deployment**: `DEPLOY_FROM_GITHUB.md`

## Template Configuration

All shop settings are centralized in `config/settings.json`:

### Configuration Structure

```json
{
  "shopName": "Your Shop Name",
  "description": "Shop description",
  "logo": "/config/logo.svg",
  "currency": {
    "symbol": "₽",
    "code": "RUB",
    "position": "after"
  },
  "managerContact": "@your_telegram",
  "colorScheme": {
    "background": "#FEFEFE",
    "foreground": "#1A1A1A",
    "primary": "#EADCF0",
    // ... more colors
  },
  "sortOptions": [
    { "id": "new", "label": "New", "emoji": "✨" },
    // ... more options
  ],
  "ui": {
    "maxWidth": "420px",
    "productsPerPage": 12,
    "showCategoryIcons": true,
    "showPriceFilter": true
  },
  "texts": {
    "addToCart": "Add to Cart",
    "checkout": "Checkout",
    // ... more texts
  },
  "fonts": {
    "fontFamily": "Inter",
    "fontFile": null,
    "productName": { "weight": 500 },
    "price": { "weight": 600 },
    "description": { "weight": 400 }
  },
  "logoSize": 32
}
```

## System Architecture

### Frontend Architecture

**Technology Stack:**
- React 18 with TypeScript for component-based UI
- Vite as the build tool and dev server
- TanStack Query (React Query) for data fetching and state management
- Shadcn/ui component library with Radix UI primitives
- Tailwind CSS with dynamic theming

**Key Features:**
- `useConfig` hook: Loads and provides configuration throughout the app
- `ThemeApplier` component: Dynamically applies color scheme from config
- `FontLoader` component: Loads custom fonts and applies typography settings
- `formatPrice` utility: Formats prices according to currency settings
- Dynamic sort options from configuration
- Configurable UI texts and labels
- Custom font support with weight controls

### Backend Architecture

**Technology Stack:**
- Flask 3.1.2 (Python web framework)
- psycopg2-binary for PostgreSQL operations
- Neon serverless PostgreSQL database
- Static file serving for React frontend

**API Endpoints:**
- `GET /api/config` - Returns shop configuration from settings.json
- `GET /config/<filename>` - Serves static files from config folder (logo, etc.)
- `GET /api/categories` - List all categories
- `GET /api/products` - List products (optional: ?category_id filter)
- `GET /api/products/<id>` - Get single product
- `POST /api/auth/telegram` - Telegram authentication
- Cart and favorites endpoints (see original documentation)

### Database Schema

**Tables (unchanged from original):**
- `users`: id (UUID), telegram_id (BIGINT UNIQUE), username, first_name, last_name, password
- `categories`: id (UUID), name (text), icon (text) - **Stored in database, not config**
- `products`: id (UUID), name, description, price, images (text[]), category_id (UUID FK)
- `favorites`: id (UUID), user_id (UUID FK), product_id (UUID FK)
- `cart`: id (UUID), user_id (UUID FK), product_id (UUID FK), quantity (integer)

**Important**: Categories and products remain in the database. Only UI/branding configuration is in JSON files.

## How to Use This Template

### 1. Configure Your Shop

Edit `config/settings.json`:
- Set your shop name and description
- Configure currency (symbol, code, position)
- Set manager Telegram contact
- Customize color scheme (all colors in HEX format)
- Set logo size in pixels (default: 32)
- Configure typography (font family, custom font file, weights)
- Define sort options with emojis
- Adjust UI settings and texts

### 2. Add Your Logo

Replace `config/logo.svg` with your logo:
- Recommended: SVG format (200x200px)
- Alternative: PNG format
- Update the path in settings.json if using different filename

### 3. Populate Database

Add your categories and products to PostgreSQL:

```sql
-- Add categories
INSERT INTO categories (name, icon) VALUES ('Category Name', '🔥');

-- Add products
INSERT INTO products (name, description, price, images, category_id) 
VALUES ('Product Name', 'Description', 1000, ARRAY['url1.jpg'], 'category-id');
```

### 4. Run the Application

```bash
# Development
npm run dev

# Production
npm run build
python app.py
```

## Example Configurations

### Clothing Store
```json
{
  "shopName": "Fashion Boutique",
  "currency": { "symbol": "$", "code": "USD", "position": "before" },
  "colorScheme": {
    "primary": "#FF6B9D",
    "accent": "#C44569"
  }
}
```

### Electronics Shop
```json
{
  "shopName": "TechHub",
  "currency": { "symbol": "€", "code": "EUR", "position": "after" },
  "colorScheme": {
    "primary": "#2C3E50",
    "accent": "#3498DB"
  }
}
```

## External Dependencies

**Database:**
- Neon Serverless PostgreSQL
- Direct connections via psycopg2-binary
- DATABASE_URL environment variable for connection

**UI Components:**
- Radix UI primitives for accessible components
- Shadcn/ui component system
- Lucide React for iconography

**Fonts:**
- Google Fonts: Inter and Poppins families

## Deployment

1. Build the frontend:
   ```bash
   npm run build
   ```

2. Set environment variables:
   - `DATABASE_URL` - PostgreSQL connection string
   - `PORT` - Server port (default: 5000)

3. Start the application:
   ```bash
   python app.py
   ```

The application is ready for deployment as a pure Python/Flask application with no Node.js runtime dependency.

## Template Benefits

✅ **No Code Changes Required** - Configure everything via JSON  
✅ **Universal** - Works for any e-commerce business  
✅ **Fast Setup** - Change config and deploy in minutes  
✅ **Flexible** - Customizable colors, currency, texts, and more  
✅ **Telegram Native** - Built specifically for Telegram Mini Apps  
✅ **Mobile Optimized** - Touch-friendly interface  

---

**Note**: This template is production-ready and fully functional. Simply configure `config/settings.json` and populate your database with products to launch your own Telegram shop! 🚀
