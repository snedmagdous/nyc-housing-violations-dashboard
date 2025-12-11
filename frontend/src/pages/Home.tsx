/**
 * Home Page Component
 *
 * Landing page that introduces the project and shows key statistics.
 * This is the first page users see when they visit your dashboard.
 *
 * Features:
 * - Project mission and impact statement
 * - High-level statistics (total violations, open cases, etc.)
 * - Quick links to main features
 * - Recent highlights or trends
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/services/api';
import {
  DatabaseIcon,
  AlertIcon,
  BuildingIcon,
  FireIcon,
  SearchIcon,
  MapIcon,
  ChartIcon
} from '@/components/common/Icons';
import './Home.css';

interface DashboardStats {
  total_violations: number;
  open_violations: number;
  total_buildings: number;
  total_severe_violations: number;
}

export const Home = () => {
  // State to store statistics from the API
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * useEffect hook runs when component mounts (page loads)
   * We use it to fetch data from the API
   *
   * The empty array [] means this runs only once on mount
   */
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        // Call your FastAPI backend to get summary statistics
        const data = await api.analysis.getStats();
        setStats(data);
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError('Failed to load statistics. Is your backend running?');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="home-page">
      {/* Hero section with project mission */}
      <section className="hero">
        <h1 className="hero-title">NYC Housing Violations Dashboard</h1>
        <p className="hero-subtitle">
          Holding landlords accountable through data transparency
        </p>
        <p className="hero-description">
          This interactive dashboard exposes patterns of housing code violations across
          New York City, identifies repeat offenders, and reveals enforcement gaps in
          affordable housing protection. Built to empower tenant advocacy and inform
          policy decisions.
        </p>
      </section>

      {/* Statistics cards */}
      <section className="stats-section">
        <h2>Current Data Overview</h2>

        {loading && <p className="loading">Loading statistics...</p>}

        {error && <div className="error-message">{error}</div>}

        {stats && (
          <div className="stats-grid">
            {/* Total Violations Card */}
            <div className="stat-card">
              <div className="stat-icon">
                <DatabaseIcon size={40} />
              </div>
              <div className="stat-value">
                {stats.total_violations.toLocaleString()}
              </div>
              <div className="stat-label">Total Violations</div>
            </div>

            {/* Open Violations Card */}
            <div className="stat-card highlight">
              <div className="stat-icon">
                <AlertIcon size={40} />
              </div>
              <div className="stat-value">
                {stats.open_violations.toLocaleString()}
              </div>
              <div className="stat-label">Open Violations</div>
            </div>

            {/* Buildings Card */}
            <div className="stat-card">
              <div className="stat-icon">
                <BuildingIcon size={40} />
              </div>
              <div className="stat-value">
                {stats.total_buildings.toLocaleString()}
              </div>
              <div className="stat-label">Buildings with Violations</div>
            </div>

            {/* Severe Violations Card */}
            <div className="stat-card highlight">
              <div className="stat-icon">
                <FireIcon size={40} />
              </div>
              <div className="stat-value">
                {stats.total_severe_violations.toLocaleString()}
              </div>
              <div className="stat-label">Severe Violations (Class B/C)</div>
            </div>
          </div>
        )}
      </section>

      {/* Feature cards - guide users to main functionality */}
      <section className="features-section">
        <h2>Explore the Data</h2>
        <div className="features-grid">
          <Link to="/search" className="feature-card">
            <div className="feature-icon">
              <SearchIcon size={48} />
            </div>
            <h3>Building Search</h3>
            <p>
              Look up any NYC building by address to see its complete violation history,
              severity breakdown, and current status.
            </p>
          </Link>

          <Link to="/map" className="feature-card">
            <div className="feature-icon">
              <MapIcon size={48} />
            </div>
            <h3>Violation Map</h3>
            <p>
              Visualize violation hotspots across NYC. Explore geographic patterns and
              identify neighborhoods with concentrated housing injustice.
            </p>
          </Link>

          <Link to="/rankings" className="feature-card">
            <div className="feature-icon">
              <ChartIcon size={48} />
            </div>
            <h3>Landlord Rankings</h3>
            <p>
              See the worst offenders: landlords and property owners with the most
              violations, sorted by count and severity.
            </p>
          </Link>
        </div>
      </section>

      {/* Call to action */}
      <section className="cta-section">
        <h2>Why This Matters</h2>
        <p>
          Thousands of NYC tenants live in buildings with serious housing code
          violations—lack of heat, broken plumbing, pest infestations. This tool makes
          that data accessible and actionable for tenants, advocates, journalists, and
          policymakers fighting for housing justice.
        </p>
        <Link to="/about" className="cta-button">
          Learn More About This Project
        </Link>
      </section>
    </div>
  );
};
