/**
 * Worst Buildings Page
 *
 * Accountability dashboard showing NYC buildings ranked by housing violations
 * Inspired by NYC Public Advocate's Worst Landlord Watchlist
 *
 * Features:
 * - Sortable table of buildings ranked by violations
 * - Filter by borough, violation count, risk score
 * - Search by building address
 * - Expandable details for each building
 * - Visual indicators for severity
 */

import { useState, useEffect, useRef } from 'react';
import { api } from '@/services/api';
import type { LandlordRanking } from '@/types/violation';
import { InfoIcon } from '@/components/common/Icons';
import './Rankings.css';

type SortField = 'total_violations' | 'severe_violations' | 'risk_score' | 'building_count';
type SortOrder = 'asc' | 'desc';

export const Rankings = () => {
  // STATE
  const [landlords, setLandlords] = useState<LandlordRanking[]>([]);
  const [filteredLandlords, setFilteredLandlords] = useState<LandlordRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLandlord, setSelectedLandlord] = useState<string | null>(null);
  const tableRef = useRef<HTMLDivElement>(null);

  // FILTERS & SORTING
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<SortField>('total_violations');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [limitResults, setLimitResults] = useState(100);

  // FETCH LANDLORD RANKINGS
  useEffect(() => {
    const fetchRankings = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch landlords sorted by total violations initially
        const data = await api.analysis.getLandlordRankings('total_violations', 200);
        setLandlords(data);
        setFilteredLandlords(data);
      } catch (err) {
        console.error('Failed to fetch landlord rankings:', err);
        setError('Failed to load landlord rankings. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchRankings();
  }, []);

  // FILTER & SORT
  useEffect(() => {
    let results = [...landlords];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      results = results.filter(landlord =>
        landlord.owner_name.toLowerCase().includes(query)
      );
    }

    // Sort
    results.sort((a, b) => {
      let aValue: number, bValue: number;

      switch (sortField) {
        case 'total_violations':
          aValue = a.total_violations;
          bValue = b.total_violations;
          break;
        case 'severe_violations':
          aValue = a.severe_violations;
          bValue = b.severe_violations;
          break;
        case 'risk_score':
          aValue = a.avg_risk_score;
          bValue = b.avg_risk_score;
          break;
        case 'building_count':
          aValue = a.building_count;
          bValue = b.building_count;
          break;
        default:
          aValue = a.total_violations;
          bValue = b.total_violations;
      }

      return sortOrder === 'desc' ? bValue - aValue : aValue - bValue;
    });

    // Limit results
    results = results.slice(0, limitResults);

    setFilteredLandlords(results);
  }, [landlords, searchQuery, sortField, sortOrder, limitResults]);

  // CLOSE EXPANDED LANDLORD ON OUTSIDE CLICK
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectedLandlord && tableRef.current) {
        const target = event.target as HTMLElement;
        // Check if click is outside the table or on a different landlord row
        if (!tableRef.current.contains(target) ||
            (target.closest('.landlord-row') && !target.closest('.landlord-details-row'))) {
          // Only close if not clicking on the same expanded row
          const clickedRow = target.closest('.landlord-row');
          if (clickedRow && clickedRow.classList.contains('expanded')) {
            return; // Don't close if clicking the expanded row itself
          }
          setSelectedLandlord(null);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [selectedLandlord]);

  // HANDLE SORT
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Toggle order if same field
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      // New field, default to descending
      setSortField(field);
      setSortOrder('desc');
    }
  };

  // RENDER SORT INDICATOR
  const renderSortIndicator = (field: SortField) => {
    if (sortField !== field) return <span className="sort-indicator">⇅</span>;
    return sortOrder === 'desc' ? <span className="sort-indicator">↓</span> : <span className="sort-indicator">↑</span>;
  };

  // GET RISK COLOR
  const getRiskColor = (score: number): string => {
    if (score >= 70) return '#991b1b'; // Dark red
    if (score >= 50) return '#ef4444'; // Red
    if (score >= 30) return '#f59e0b'; // Orange
    return '#facc15'; // Yellow
  };

  // CALCULATE SUMMARY STATS
  const totalBuildings = filteredLandlords.reduce((sum, l) => sum + l.building_count, 0);
  const totalViolations = filteredLandlords.reduce((sum, l) => sum + l.total_violations, 0);
  const totalSevere = filteredLandlords.reduce((sum, l) => sum + l.severe_violations, 0);
  const totalOpen = filteredLandlords.reduce((sum, l) => sum + l.open_violations, 0);

  if (loading) {
    return (
      <div className="rankings-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading landlord rankings...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rankings-page">
        <div className="error-state">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="rankings-page">
      {/* HEADER */}
      <div className="rankings-header">
        <div className="header-content">
          <h1>NYC Worst Buildings</h1>
          <p className="header-subtitle">
            Tracking housing code violations across New York City
          </p>
        </div>

        {/* SUMMARY STATS */}
        <div className="summary-stats">
          <div className="stat-card">
            <div className="stat-value">{filteredLandlords.length}</div>
            <div className="stat-label">Buildings</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{totalBuildings.toLocaleString()}</div>
            <div className="stat-label">Buildings</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{totalViolations.toLocaleString()}</div>
            <div className="stat-label">Total Violations</div>
          </div>
          <div className="stat-card severe">
            <div className="stat-value">{totalSevere.toLocaleString()}</div>
            <div className="stat-label">Severe (B/C)</div>
          </div>
          <div className="stat-card open">
            <div className="stat-value">{totalOpen.toLocaleString()}</div>
            <div className="stat-label">Still Open</div>
          </div>
        </div>
      </div>

      {/* CONTROLS */}
      <div className="rankings-controls">
        {/* OWNER INFO NOTE */}
        <div className="owner-info-note">
          <InfoIcon size={18} className="note-icon" />
          Owner information not available in public dataset.
        </div>

        {/* SEARCH */}
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by building address..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button
              className="search-clear"
              onClick={() => setSearchQuery('')}
              aria-label="Clear search"
            >
              ✕
            </button>
          )}
        </div>

        {/* LIMIT SELECTOR */}
        <div className="limit-selector">
          <label>Show:</label>
          <select value={limitResults} onChange={(e) => setLimitResults(Number(e.target.value))}>
            <option value={25}>Top 25</option>
            <option value={50}>Top 50</option>
            <option value={100}>Top 100</option>
            <option value={200}>All ({landlords.length})</option>
          </select>
        </div>
      </div>

      {/* TABLE */}
      <div className="rankings-table-container" ref={tableRef}>
        <table className="rankings-table">
          <thead>
            <tr>
              <th className="rank-column">#</th>
              <th className="name-column">Building Address</th>
              <th className="sortable" onClick={() => handleSort('building_count')}>
                Properties {renderSortIndicator('building_count')}
              </th>
              <th className="sortable" onClick={() => handleSort('total_violations')}>
                Total Violations {renderSortIndicator('total_violations')}
              </th>
              <th className="sortable" onClick={() => handleSort('severe_violations')}>
                Severe (B/C) {renderSortIndicator('severe_violations')}
              </th>
              <th>Open</th>
              <th className="sortable" onClick={() => handleSort('risk_score')}>
                Avg Risk Score {renderSortIndicator('risk_score')}
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredLandlords.map((landlord, index) => (
              <>
                <tr
                  key={landlord.owner_name}
                  className={`landlord-row ${selectedLandlord === landlord.owner_name ? 'expanded' : ''}`}
                  onClick={() => setSelectedLandlord(selectedLandlord === landlord.owner_name ? null : landlord.owner_name)}
                >
                {/* RANK */}
                <td className="rank-cell">
                  <div className={`rank-badge ${index < 3 ? 'top-three' : ''}`}>
                    {index + 1}
                  </div>
                </td>

                {/* NAME */}
                <td className="name-cell">
                  <div className="landlord-name">{landlord.owner_name}</div>
                </td>

                {/* BUILDINGS */}
                <td className="number-cell">
                  {landlord.building_count}
                </td>

                {/* TOTAL VIOLATIONS */}
                <td className="number-cell violations-cell">
                  <span className="violations-total">{landlord.total_violations.toLocaleString()}</span>
                </td>

                {/* SEVERE VIOLATIONS */}
                <td className="number-cell severe-cell">
                  <span className="severe-badge">{landlord.severe_violations.toLocaleString()}</span>
                </td>

                {/* OPEN VIOLATIONS */}
                <td className="number-cell open-cell">
                  {landlord.open_violations > 0 && (
                    <span className="open-badge">{landlord.open_violations.toLocaleString()}</span>
                  )}
                  {landlord.open_violations === 0 && <span className="text-muted">—</span>}
                </td>

                {/* RISK SCORE */}
                <td className="number-cell risk-cell">
                  <div className="risk-score" style={{ color: getRiskColor(landlord.avg_risk_score) }}>
                    <div className="risk-value">{landlord.avg_risk_score.toFixed(1)}</div>
                    <div className="risk-bar">
                      <div
                        className="risk-fill"
                        style={{
                          width: `${landlord.avg_risk_score}%`,
                          backgroundColor: getRiskColor(landlord.avg_risk_score),
                        }}
                      ></div>
                    </div>
                  </div>
                </td>
              </tr>
              {selectedLandlord === landlord.owner_name && (
                <tr className="landlord-details-row">
                  <td colSpan={7}>
                    <div className="landlord-details">
                      <h3>Building Profile</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <span className="detail-label">Address:</span>
                          <span className="detail-value">{landlord.owner_name}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Properties Owned:</span>
                          <span className="detail-value">{landlord.building_count}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Total Violations:</span>
                          <span className="detail-value">{landlord.total_violations.toLocaleString()}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Severe Violations (B/C):</span>
                          <span className="detail-value severe">{landlord.severe_violations.toLocaleString()}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Open Violations:</span>
                          <span className="detail-value open">{landlord.open_violations.toLocaleString()}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Average Risk Score:</span>
                          <span className="detail-value" style={{ color: getRiskColor(landlord.avg_risk_score) }}>
                            {landlord.avg_risk_score.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      {/* EMPTY STATE */}
      {filteredLandlords.length === 0 && (
        <div className="empty-state">
          <p>No buildings match your search.</p>
          <button onClick={() => setSearchQuery('')}>Clear search</button>
        </div>
      )}
    </div>
  );
};
