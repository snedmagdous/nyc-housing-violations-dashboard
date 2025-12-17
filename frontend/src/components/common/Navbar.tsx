/**
 * Navbar Component
 *
 * Main navigation bar for the entire application.
 * Provides links to different sections of the dashboard.
 *
 * React Router's Link component is used instead of <a> tags because:
 * - It prevents full page reloads (faster navigation)
 * - Maintains application state
 * - Provides active link styling
 */

import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

/**
 * Helper function to determine if a nav link is active
 * Used to highlight the current page in the navigation
 */
const isActiveLink = (path: string, currentPath: string): boolean => {
  if (path === '/') {
    return currentPath === '/';
  }
  return currentPath.startsWith(path);
};

export const Navbar = () => {
  // useLocation hook gives us the current route
  const location = useLocation();

  return (
    <nav className="navbar">
      {/* Logo and project title */}
      <div className="navbar-brand">
        <Link to="/" className="navbar-logo">
          NYC Housing Violations
        </Link>
        <span className="navbar-subtitle">Holding landlords accountable</span>
      </div>

      {/* Main navigation links */}
      <ul className="navbar-nav">
        <li>
          <Link
            to="/"
            className={`nav-link ${isActiveLink('/', location.pathname) ? 'active' : ''}`}
          >
            Home
          </Link>
        </li>

        <li>
          <Link
            to="/search"
            className={`nav-link ${isActiveLink('/search', location.pathname) ? 'active' : ''}`}
          >
            Building Search
          </Link>
        </li>

        <li>
          <Link
            to="/map"
            className={`nav-link ${isActiveLink('/map', location.pathname) ? 'active' : ''}`}
          >
            Violation Map
          </Link>
        </li>

        <li>
          <Link
            to="/rankings"
            className={`nav-link ${isActiveLink('/rankings', location.pathname) ? 'active' : ''}`}
          >
            Landlord Rankings
          </Link>
        </li>

        <li>
          <Link
            to="/about"
            className={`nav-link ${isActiveLink('/about', location.pathname) ? 'active' : ''}`}
          >
            About
          </Link>
        </li>
      </ul>
    </nav>
  );
};
