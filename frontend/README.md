# NYC Housing Violations Dashboard - Frontend

Modern React + TypeScript dashboard for visualizing NYC housing violations data.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety and better developer experience
- **Vite** - Lightning-fast build tool and dev server
- **React Router** - Client-side routing
- **Recharts** - Data visualization library
- **Leaflet** - Interactive maps
- **Axios** - HTTP client for API calls

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/          # Navbar, Layout, etc.
│   │   ├── charts/          # Data visualization components
│   │   └── map/             # Map-related components
│   ├── pages/               # Route components (Home, Search, Map, etc.)
│   ├── services/            # API service layer
│   │   └── api.ts           # Centralized API calls to FastAPI backend
│   ├── types/               # TypeScript type definitions
│   │   └── violation.ts     # Data models for violations and buildings
│   ├── hooks/               # Custom React hooks
│   ├── utils/               # Helper functions
│   ├── styles/              # Global styles
│   ├── App.tsx              # Main app component with routing
│   ├── main.tsx             # App entry point
│   └── index.css            # Global CSS
├── public/                  # Static assets
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Your FastAPI backend running on `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (already done during setup)
npm install
```

### Development

```bash
# Start development server (with hot reload)
npm run dev
```

This will:
- Start Vite dev server on `http://localhost:5173`
- Auto-open browser
- Proxy API requests to your FastAPI backend (avoids CORS issues)
- Enable hot module replacement (instant updates on save)

### Building for Production

```bash
# Create optimized production build
npm run build

# Preview production build locally
npm run preview
```

The build output will be in the `dist/` folder.

## Key Features Implemented

### ✅ Completed

1. **Project Foundation**
   - React + TypeScript setup with Vite
   - Modern folder structure following best practices
   - Path aliases configured (`@/` → `src/`)
   - TypeScript strict mode enabled

2. **Routing**
   - React Router for client-side navigation
   - 5 main routes: Home, Search, Map, Rankings, About
   - Layout wrapper with navbar and footer
   - 404 page for invalid routes

3. **UI Components**
   - Responsive navigation bar with active link highlighting
   - Consistent layout wrapper
   - Home page with statistics dashboard
   - About page with project info and methodology

4. **API Integration**
   - Centralized API service layer (`api.ts`)
   - Type-safe API calls to FastAPI backend
   - Request/response interceptors for logging and error handling
   - Organized by domain (violations, buildings, analysis)

5. **Styling**
   - Global CSS variables for consistent theming
   - Responsive design (mobile-friendly)
   - Modern gradient color scheme (purple/blue)
   - Smooth animations and transitions
   - Custom scrollbar styling

### 🚧 To Be Implemented

1. **Building Search Page**
   - Address search with autocomplete
   - Building detail view with violation history
   - Charts showing violation trends
   - Filters by class, date range

2. **Interactive Map Page**
   - Leaflet map of NYC
   - Clustered markers for buildings
   - Heatmap overlay
   - Popup details on click

3. **Landlord Rankings Page**
   - Sortable table of worst offenders
   - Bar charts for visualization
   - Filter by borough

4. **Data Visualization Components**
   - Recharts components for trends
   - Violation class breakdown charts
   - Temporal analysis visualizations

## Important Concepts Explained

### React Hooks Used

- **useState**: Manages component state (e.g., storing API data)
- **useEffect**: Runs side effects (e.g., fetching data on component mount)
- **useLocation**: Gets current route from React Router

Example from Home page:
```typescript
const [stats, setStats] = useState<DashboardStats | null>(null);

useEffect(() => {
  const fetchStats = async () => {
    const data = await api.analysis.getStats();
    setStats(data);
  };
  fetchStats();
}, []); // Empty array = run once on mount
```

### Why Vite?

Vite is faster than Create React App because:
- Uses native ES modules (no bundling in dev)
- Hot Module Replacement is instant
- Optimized production builds with Rollup
- Pre-configured for TypeScript and React

### TypeScript Benefits

- **Type Safety**: Catch errors before runtime
- **Autocomplete**: Better IDE suggestions (try typing `api.` and see!)
- **Refactoring**: Safely rename and restructure
- **Documentation**: Types serve as inline docs

### Path Aliases

Instead of:
```typescript
import { api } from '../../../services/api'
```

You can write:
```typescript
import { api } from '@/services/api'
```

Cleaner and easier to refactor! Configured in `vite.config.ts` and `tsconfig.app.json`.

## API Integration

The frontend communicates with your FastAPI backend via the `api` service object:

```typescript
import { api } from '@/services/api';

// Example: Get all violations with filters
const violations = await api.violations.getAll({
  boro: 'Manhattan',
  is_open: true,
  page: 1,
  per_page: 50
});

// Example: Search buildings
const buildings = await api.buildings.search('123 Main St');

// Example: Get statistics for dashboard
const stats = await api.analysis.getStats();

// Example: Get violation trends over time
const trends = await api.violations.getTrends('month', {
  start_date: '2024-01-01',
  end_date: '2024-12-31'
});
```

All API calls are type-safe thanks to TypeScript! Your IDE will show you exactly what parameters each function accepts and what it returns.

## Environment Variables

Create a `.env` file in the frontend directory (optional):

```env
# API base URL (default: http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

The proxy in `vite.config.ts` handles routing `/api/*` requests to your backend automatically in development.

## Troubleshooting

### API calls failing?

1. **Check backend is running**: Make sure FastAPI is running on `http://localhost:8000`
2. **Check browser console**: Look for CORS errors or 404s
3. **Check network tab**: See if requests are being sent correctly
4. **Vite proxy**: The proxy forwards `/api/*` requests to port 8000

### TypeScript errors?

1. Run `npm install` to ensure all types are installed
2. Check that `@types/leaflet` is in `devDependencies`
3. Restart VS Code to reload TypeScript server
4. Check `tsconfig.app.json` for correct configuration

### Import errors with `@/`?

1. Check `vite.config.ts` has the alias: `'@': path.resolve(__dirname, './src')`
2. Check `tsconfig.app.json` has: `"paths": { "@/*": ["./src/*"] }`
3. Restart dev server after config changes

### Blank page on load?

1. Check browser console for errors
2. Make sure `main.tsx` imports and renders `App`
3. Check that `index.html` includes the script tag for `main.tsx`

## Next Steps

### 1. Implement Building Search Page

**What to build:**
- Search input component with real-time API calls
- Autocomplete dropdown using `api.buildings.search()`
- Result cards showing building stats
- Click to see detailed violation history

**Components to create:**
- `src/components/common/SearchInput.tsx`
- `src/components/common/BuildingCard.tsx`
- Update `src/pages/Search.tsx` with full implementation

**API calls to use:**
```typescript
// Search buildings
const buildings = await api.buildings.search(query);

// Get building details
const building = await api.buildings.getById(buildingId);

// Get violations for building
const violations = await api.violations.getByBuilding(buildingId);
```

### 2. Add Interactive Map

**What to build:**
- Leaflet map component showing NYC
- Markers for buildings with violations
- Clustering for performance
- Popup on marker click with building info

**Components to create:**
- `src/components/map/ViolationMap.tsx`
- `src/components/map/BuildingMarker.tsx`
- `src/components/map/MapLegend.tsx`
- Update `src/pages/Map.tsx`

**Libraries to use:**
- `react-leaflet` (already installed)
- Don't forget to import Leaflet CSS: `import 'leaflet/dist/leaflet.css'`

### 3. Build Data Visualizations

**What to build:**
- Line chart showing violation trends over time
- Bar chart for violation class breakdown
- Pie chart for status distribution

**Components to create:**
- `src/components/charts/TrendChart.tsx`
- `src/components/charts/ClassBreakdownChart.tsx`
- `src/components/charts/StatusPieChart.tsx`

**Use Recharts:**
```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
```

## Code Examples

### Creating a new page

1. Create file in `src/pages/MyPage.tsx`
2. Add route in `src/App.tsx`:
```typescript
<Route path="/mypage" element={<MyPage />} />
```
3. Add link in `src/components/common/Navbar.tsx`

### Making an API call

```typescript
import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import { Violation } from '@/types/violation';

export const MyComponent = () => {
  const [data, setData] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await api.violations.getAll();
        setData(result.items);
      } catch (err) {
        setError('Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return <div>{/* Render data */}</div>;
};
```

## Resources

- [React Docs](https://react.dev) - Official React documentation
- [TypeScript Handbook](https://www.typescriptlang.org/docs/) - Learn TypeScript
- [Vite Guide](https://vitejs.dev/guide/) - Vite documentation
- [React Router Docs](https://reactrouter.com) - Routing guide
- [Recharts Examples](https://recharts.org/en-US/examples) - Chart examples
- [Leaflet Docs](https://leafletjs.com/reference.html) - Map API reference
- [React Leaflet](https://react-leaflet.js.org/) - React wrapper for Leaflet

## Questions?

Check the extensive comments in the code! Every file has detailed explanations of:
- What the code does
- Why certain patterns are used
- How to extend and modify it

Key files to read:
- `src/App.tsx` - Routing explanation
- `src/services/api.ts` - API architecture
- `src/types/violation.ts` - Data model documentation
- `vite.config.ts` - Build configuration
