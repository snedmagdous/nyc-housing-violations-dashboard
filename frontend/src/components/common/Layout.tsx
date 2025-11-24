/**
 * Layout Component
 *
 * Wraps all pages with consistent structure:
 * - Navigation bar at the top
 * - Main content area
 * - Footer (optional)
 *
 * Using the Layout pattern provides:
 * - Consistent spacing and styling across all pages
 * - Single place to add global elements (navbar, footer, modals)
 * - Cleaner page components (they don't need to include navbar)
 */

import type { ReactNode } from 'react';
import { Navbar } from './Navbar';
import './Layout.css';

interface LayoutProps {
  children: ReactNode;  // The page content that will be wrapped
}

export const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="layout">
      {/* Navigation bar - appears on every page */}
      <Navbar />

      {/* Main content area - this is where page components render */}
      <main className="main-content">
        {children}
      </main>

      {/* Footer - you can add project info, links, etc. */}
      <footer className="footer">
        <div className="footer-content">
          <p>
            Data from{' '}
            <a
              href="https://opendata.cityofnewyork.us/"
              target="_blank"
              rel="noopener noreferrer"
            >
              NYC Open Data
            </a>
          </p>
          <p>
            Built with 💜 for housing justice |{' '}
            <a
              href="https://github.com/snedmagdous/nyc-housing-violations-dashboard"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
};
