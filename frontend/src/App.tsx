/**
 * App.tsx - Main Application Component
 *
 * This is the root component of your React application.
 * It sets up React Router for navigation between pages.
 *
 * React Router Concepts:
 * - BrowserRouter: Enables client-side routing (URL changes without page reload)
 * - Routes: Container for all route definitions
 * - Route: Maps a URL path to a component
 *
 * When user navigates to a URL:
 * - React Router matches the URL to a Route
 * - The corresponding component is rendered inside the Layout
 * - No page reload happens - fast, smooth transitions!
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/common/Layout';
import { Home } from '@/pages/Home';
import { Search } from '@/pages/Search';
import { Map } from '@/pages/Map';
import { Rankings } from '@/pages/Rankings';
import { About } from '@/pages/About';

function App() {
  return (
    /**
     * BrowserRouter enables routing throughout the app
     * It uses the browser's History API to sync UI with URL
     */
    <BrowserRouter>
      {/* Layout wraps all pages with navbar and footer */}
      <Layout>
        {/* Routes container - only one route will render at a time */}
        <Routes>
          {/* Home page - shown when user visits / */}
          <Route path="/" element={<Home />} />

          {/* Building search - /search */}
          <Route path="/search" element={<Search />} />

          {/* Interactive map - /map */}
          <Route path="/map" element={<Map />} />

          {/* Landlord rankings - /rankings */}
          <Route path="/rankings" element={<Rankings />} />

          {/* About page - /about */}
          <Route path="/about" element={<About />} />

          {/* 404 Not Found - catches all other routes */}
          <Route
            path="*"
            element={
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <h1>404 - Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <a href="/">Go back to home</a>
              </div>
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
