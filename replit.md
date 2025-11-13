# Universal E-Commerce Telegram Mini App Template

## Overview

This is a **universal template** for creating e-commerce Telegram Mini Apps. The application is fully configurable through JSON files, allowing anyone to create their own online shop by simply changing configuration files without touching the code.

**Design Philosophy:**
- Mobile-first interface (max-width: 420px)
- Flat, minimal design with customizable pastel color palette
- Touch-optimized interactions
- Light mode only with configurable color scheme

## Recent Changes

### November 13, 2025 (Latest) - Automated Database Setup & Remote Access
- **Automatic Database Initialization**: Database tables now created automatically during deployment
- **Interactive Remote DB Access**: Deploy scripts now ask if you want to enable remote PostgreSQL access
- **One-Step Setup**: No manual database configuration needed - everything happens during deployment
- **Smart Defaults**: Both `auto_deploy.sh` and `deploy_vps.sh` handle DB setup automatically
- **Secure Remote Access**: Optional remote DB access with automatic firewall configuration
- **Connection String Display**: Shows ready-to-use DATABASE_URL after enabling remote access

### November 12, 2025 - Remote Database Access & Bot Deployment
- **Remote DB Access**: New `enable_remote_db.sh` script to configure PostgreSQL for remote connections
- **Local Bot Development**: Full support for running bot locally on Windows/Mac with remote DB connection
- **VPS Bot Deployment**: New `deploy_bot_to_vps.sh` for running bot as systemd service on VPS
- **Database Connection Resilience**: Added retry logic with 3 attempts and 2s delays
- **Telegram Auto-Reconnection**: Exponential backoff (5-60s) for handling network disruptions
- **Environment Variable Support**: Full `.env` file support in bot.py and db_operations.py
- **Type Safety**: Fixed all LSP errors with proper type hints and cast() usage
- **Comprehensive Docs**: Added `BOT_DEPLOYMENT.md` and `REMOTE_DB_ACCESS.md` guides

### November 09, 2025 - Telegram Bot Windows EXE Support
- **Automated Token Collection**: `deploy_vps.sh` now requests all Telegram bot tokens during VPS deployment
- **Separate Bot Environment**: Creates dedicated `.env` file in `telegram_bot/` with all required credentials
- **Category Synchronization**: Automatically syncs categories from `config/settings.json` to `telegram_bot/settingsbot.json`
- **Admin ID Management**: Safely handles Telegram admin ID input (numeric IDs, removes @ prefix if present)

### October 26, 2025 - Custom Fonts and Logo Sizing
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

### November 9, 2025 - One-Command Auto-Deploy
- **New `auto_deploy.sh`**: Fully automatic deployment without any questions - just one command!
- **Auto-generated passwords**: Secure random DB passwords generated automatically
- **No user input**: All parameters use smart defaults or can be set via environment variables
- **3-5 minute deploy**: Fastest deployment method available
- **New Documentation**: Added `БЫСТРАЯ_УСТАНОВКА.md` (One-Command Install guide)

### November 8, 2025 - VPS Deployment Improvements
- **GitHub Integration**: `deploy_vps.sh` now supports direct cloning from GitHub
- **Interactive Deploy**: Download and run deployment script directly from GitHub
- **Auto-fix Permissions**: `deploy_vps.sh` automatically configures Nginx permissions
- **New Script**: `fix_permissions.sh` for quick resolution of 403 Forbidden errors
- **Enhanced Documentation**: Added `GITHUB_QUICK_START.md` for interactive deployment
- **Flexible Source**: Support for both GitHub and local file deployment

## 🚀 VPS Deployment Quick Start

### ⚡ Auto-Deploy (1 Command, No Questions!)

**Fastest way - fully automatic:**

```bash
# Connect to VPS
ssh root@YOUR_VPS_IP

# Auto-deploy from GitHub (one command!)
GITHUB_REPO="https://github.com/YOUR_USERNAME/YOUR_REPO.git" \
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/auto_deploy.sh | sudo bash
```

**Done in 3-5 minutes!** Opens at: `http://YOUR_VPS_IP`

- ✅ No questions asked - all defaults
- ✅ Auto-generated DB password
- ✅ Clones from GitHub automatically
- ✅ Builds and starts everything

---

### 📋 Interactive Deploy (with custom settings)

**If you want to customize settings:**

```bash
# Connect to VPS
ssh root@YOUR_VPS_IP

# Download and run deployment script
wget https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/deploy_vps.sh
chmod +x deploy_vps.sh
sudo ./deploy_vps.sh
```

When prompted, enter your GitHub repository URL or leave empty for local files.

**Alternative - Clone first, then deploy:**

```bash
# 1. Clone repository on VPS
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git /opt/shop-deploy
cd /opt/shop-deploy

# 2. Run auto-deployment (leave GitHub URL empty to use local files)
chmod +x deploy_vps.sh
sudo ./deploy_vps.sh
```

### Available Scripts

| Script | Purpose | Interactive |
|--------|---------|-------------|
| `auto_deploy.sh` | **Fastest** - Auto-deploy without questions | No ❌ |
| `deploy_vps.sh` | Interactive deployment with custom settings | Yes ✅ |
| `update_vps.sh` | Update deployed application | Yes ✅ |
| `fix_permissions.sh` | Fix 403 Forbidden errors | No ❌ |
| `backup_db.sh` | Backup PostgreSQL database | No ❌ |
| `restore_db.sh` | Restore database from backup | Yes ✅ |

### 📚 Documentation

**All documentation is in the `docs/` folder:**

- 📖 **[COMPLETE GUIDE](docs/ПОЛНОЕ_РУКОВОДСТВО.md)** ⭐⭐⭐ - Everything in one file!
  - How to customize your shop
  - How to deploy to VPS
  - How to update
  - Domain and SSL setup
  - Troubleshooting

**Quick Links:**
- ⚡ **[One-Command Install](docs/БЫСТРАЯ_УСТАНОВКА.md)** - Auto-deploy, no questions
- 🚀 **[Interactive Install](docs/QUICK_START_RU.md)** - Step-by-step with customization
- 🌐 **[Domain & SSL](docs/DOMAIN_SETUP_RU.md)** - Custom domain setup
- 🔧 **[All Scripts](docs/VPS_SCRIPTS_README.md)** - Scripts reference

**[📁 Browse all documentation](docs/README.md)**

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

### Example Store 1
```json
{
  "shopName": "My Fashion Store",
  "currency": { "symbol": "$", "code": "USD", "position": "before" },
  "colorScheme": {
    "primary": "#FF6B9D",
    "accent": "#C44569"
  }
}
```

### Example Store 2
```json
{
  "shopName": "My Electronics Shop",
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
