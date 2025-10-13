# Flowery Bloom - Mobile Flower Shop

## Overview

Flowery Bloom is a mobile-first Telegram Mini App for an online flower shop. The application features a clean, pastel-themed interface designed exclusively for mobile devices (max 420px width). Built with React frontend and Flask backend, it provides an e-commerce experience for browsing and purchasing flowers and greeting cards with a focus on simplicity and aesthetic appeal.

## Recent Changes

### October 12, 2025 (Latest)
- **Pure Flask Architecture**: Simplified application to use only Flask (removed Node.js/Express dependency)
- **Static File Serving**: Configured Flask to serve pre-built React frontend from `dist/public/`
- **API Routes**: Added `/api` prefix to all Flask routes for proper SPA routing
- **Database Setup**: Connected Neon PostgreSQL database with environment variables
- **Production Build**: Created production build of React frontend (387.97 kB JS, 69.62 kB CSS)
- **Startup Scripts**: Created `run_flask.sh` for running pure Flask application on port 5000

### October 12, 2025 (Earlier)
- **Telegram Mini App Database Integration**: Updated database schema for full Telegram authentication support
- **Users Table**: Added `telegram_id` (BIGINT UNIQUE), `first_name`, `last_name` fields; made `username` and `password` optional
- **Cart Table**: Created cart persistence table with user/product references and quantity tracking
- **Schema Synchronization**: Aligned frontend types, Flask API, and seed scripts with Telegram-ready structure
- **Database Migration**: Successfully migrated existing database to new schema with ALTER TABLE commands

### October 11, 2025
- **Database Categories**: Migrated category data from hardcoded frontend arrays to PostgreSQL database with UUID-based schema
- **API Integration**: Added `/api/categories` endpoint and connected frontend to fetch categories dynamically
- **Filter Reset**: Implemented "Сбросить" (Reset) button in FilterBar that appears when any filters are active
- **UI Improvements**: Replaced native select with Shadcn Select component for sort dropdown with better mobile touch support
- **Image Carousel**: Added swipe-to-browse functionality for product images with smooth opacity transitions (300ms)
- **Visual Indicators**: Implemented dot indicators for image carousel with active state animation

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack:**
- React 18 with TypeScript for component-based UI
- Vite as the build tool and dev server
- TanStack Query (React Query) for data fetching and state management
- Shadcn/ui component library with Radix UI primitives
- Tailwind CSS for styling with custom design tokens

**Design Philosophy:**
- Mobile-only interface (max-width: 420px)
- Flat, minimal design with pastel color palette
- No hover effects or 3D elements - optimized for touch interactions
- Wildberries-inspired card layouts adapted to gentle aesthetic
- Light mode only with predefined color scheme (#FEFEFE background, #EADCF0 primary accent)

**Key Components:**
- `Header`: Sticky navigation with brand, favorites, and cart icons
- `FilterBar`: Horizontal scrollable category and sorting filters
- `ProductCard`: Two-column grid layout for product display
- `ProductGrid`: Container for product listings
- `ProductDetail`: Full product view with image gallery
- `CartItem`: Individual cart item management
- `Pagination`: Page navigation for product listings

**Routing Strategy:**
- Client-side page state management without traditional routing
- Page switching via state: 'home' | 'cart' | 'favorites' | 'product'
- Connected to PostgreSQL database via Flask API for all product data

### Backend Architecture

**Technology Stack:**
- Flask 3.1.2 (Python web framework)
- psycopg2-binary for PostgreSQL operations
- Neon serverless PostgreSQL database
- Static file serving for React frontend

**API Structure:**
- RESTful API endpoints prefixed with `/api`
- All routes return JSON responses
- Error handling with proper HTTP status codes
- Database operations via direct SQL queries with psycopg2

**API Endpoints:**
- `GET /api/categories` - List all categories
- `GET /api/products` - List products (optional: ?category_id filter)
- `GET /api/products/<id>` - Get single product
- `GET /api/favorites/<user_id>` - Get user's favorites
- `POST /api/favorites` - Add to favorites
- `DELETE /api/favorites/<user_id>/<product_id>` - Remove from favorites
- `POST /api/auth/telegram` - Telegram authentication
- `GET /api/cart/<user_id>` - Get user's cart
- `POST /api/cart` - Add to cart
- `PUT /api/cart` - Update cart quantity
- `DELETE /api/cart/<user_id>/<product_id>` - Remove from cart
- `DELETE /api/cart/<user_id>` - Clear cart

**Static File Serving:**
- Flask serves pre-built React app from `dist/public/`
- Catch-all route (`/<path:path>`) serves `index.html` for SPA routing
- Static assets (JS, CSS, images) served from `dist/public/assets/`

**Storage Layer:**
- PostgreSQL database (Neon) connected via DATABASE_URL
- Database schema with tables: categories, products, users, favorites, cart
- Full CRUD operations via SQL queries
- Database seeded via `seed_db.py` script

## Running the Application

### Pure Flask Mode (Recommended for Production/Deployment)

The application has been simplified to run on pure Flask without Node.js:

```bash
bash run_flask.sh
```

This script:
1. Seeds the database with initial data (categories and products)
2. Starts Flask server on port 5000
3. Serves pre-built React frontend from `dist/public/`
4. Exposes API endpoints on `/api/*`

**Note:** Before first run, ensure React frontend is built:
```bash
npm run build
```

### Development Mode

For development, rebuild the frontend after changes:

```bash
npm run build && python app.py
```

Flask serves the updated static files. For faster iteration, you can also run Vite directly in dev mode:

```bash
# Terminal 1 - Flask backend
PORT=5001 python app.py

# Terminal 2 - Vite frontend  
npm exec vite
```

Then access Vite dev server (with hot reload) at the Vite port, which proxies API calls to Flask on port 5001.

## Deployment

For deployment to services like Render or other platforms:

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
- Hot module replacement (HMR) in development
- Static file serving for production builds

### Data Models

**Current Schema (Telegram Mini App Ready):**
- `users` table: id (UUID), telegram_id (BIGINT UNIQUE), username (text), first_name (text), last_name (text), password (text optional)
- `categories` table: id (UUID), name (text), icon (text)
- `products` table: id (UUID), name (text), description (text), price (integer), images (text[]), category_id (UUID FK)
- `favorites` table: id (UUID), user_id (UUID FK), product_id (UUID FK), UNIQUE(user_id, product_id)
- `cart` table: id (UUID), user_id (UUID FK), product_id (UUID FK), quantity (integer), UNIQUE(user_id, product_id)
- All tables created and managed via SQL in seed_db.py

**Future Expansion:**
- Orders and order items tables
- Payment integration
- Delivery tracking

### State Management

**Client-Side:**
- React hooks (useState, useEffect) for local component state
- TanStack Query (React Query) for server state and caching
- Optimistic updates for cart and favorites
- Automatic cache invalidation on mutations

**Server-Side:**
- PostgreSQL database for persistent storage
- Direct SQL queries via psycopg2
- Session-based cart and favorites per user

### Styling System

**Tailwind Configuration:**
- Custom color palette using CSS variables
- HSL color format with alpha channel support
- Responsive spacing units (2, 4, 8, 12, 16, 20, 24px)
- Custom border radius values (sm: 8px, md: 12px, lg: 16px)

**Design Tokens:**
- Flat button styles with outline variants
- Card-based layouts with subtle borders
- Elevation system using opacity-based overlays
- Touch-friendly sizing (minimum 44px touch targets)

## External Dependencies

### Third-Party Services

**Database:**
- Neon Serverless PostgreSQL
- Direct connections via psycopg2-binary
- DATABASE_URL environment variable for connection

**UI Components:**
- Radix UI primitives for accessible components (dialogs, dropdowns, tooltips, etc.)
- Shadcn/ui component system built on Radix
- Lucide React for iconography

**Backend:**
- Flask 3.1.2 for web framework
- psycopg2-binary for PostgreSQL adapter
- python-dotenv for environment management

**Frontend Build:**
- Vite for development and production builds
- TypeScript for frontend type safety
- Tailwind CSS for styling

**Fonts:**
- Google Fonts: Inter and Poppins families
- Preconnect optimization for font loading

### Image Hosting

**Current Implementation:**
- Unsplash URLs for mock product images
- Design guidelines mention Cloudinary for production
- Image URLs stored in database (not binary data)

### Future Integrations

**Telegram Mini App:**
- Application designed as Telegram Mini App
- Mobile-optimized viewport settings
- Touch-friendly interactions throughout

**Payment Processing:**
- Not yet implemented
- Order flow currently ends with manager contact (@flowery_b1oom)

**Content Delivery:**
- Static assets served via Vite in development
- Production build outputs to `dist/public`
- Asset path aliases configured for images