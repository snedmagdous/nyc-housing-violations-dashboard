/**
 * Building Search Page
 *
 * Allows users to search for buildings by address and view violation history.
 *
 * Flow:
 * 1. User types in search input
 * 2. After 500ms of no typing (debounced), API call is made
 * 3. Results are displayed as BuildingCard components
 * 4. User can click a card to see detailed view
 */

import { useState, useEffect } from 'react';
import { api } from '@/services/api';
import type { Building } from '@/types/violation';
import { SearchInput } from '@/components/common/SearchInput';
import { BuildingCard } from '@/components/common/BuildingCard';
import { useDebounce } from '@/hooks/useDebounce';
import './Search.css';

export const Search = () => {
  // State for search query (what user types)
  const [searchQuery, setSearchQuery] = useState('');

  // State for search results from API
  const [buildings, setBuildings] = useState<Building[]>([]);

  // State for selected building (when user clicks a card)
  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(null);

  // Loading and error states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Debounce the search query
   * This delays the API call until user stops typing for 500ms
   */
  const debouncedQuery = useDebounce(searchQuery, 500);

  /**
   * Effect: Make API call when debounced query changes
   * This only runs 500ms after user stops typing
   */
  useEffect(() => {
    // Don't search if query is too short (less than 3 characters)
    if (debouncedQuery.length < 3) {
      setBuildings([]);
      return;
    }

    const searchBuildings = async () => {
      try {
        setLoading(true);
        setError(null);

        // Call the API search endpoint
        const response = await api.buildings.search(debouncedQuery);

        setBuildings(response.buildings);

        // Show message if no results
        if (response.count === 0) {
          setError('No buildings found. Try a different search term.');
        }
      } catch (err) {
        console.error('Search error:', err);
        setError('Failed to search buildings. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    searchBuildings();
  }, [debouncedQuery]); // Re-run when debounced query changes

  /**
   * Handle building card click
   * Shows detailed view of selected building
   */
  const handleBuildingClick = (building: Building) => {
    setSelectedBuilding(building);
    // Scroll to top to show details
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /**
   * Close detailed view
   */
  const handleCloseDetail = () => {
    setSelectedBuilding(null);
  };

  return (
    <div className="search-page">
      <div className="search-header">
        <h1>Building Search</h1>
        <p>Search for NYC buildings by address, zip code, or building ID</p>
      </div>

      {/* Search input */}
      <div className="search-container">
        <SearchInput
          value={searchQuery}
          onChange={setSearchQuery}
          loading={loading}
          placeholder="Try searching for '123 Main St' or '10001'..."
        />
      </div>

      {/* Search hints */}
      {searchQuery.length === 0 && (
        <div className="search-hints">
          <h3>Search Tips:</h3>
          <ul>
            <li>🏠 Enter a street address (e.g., "123 Broadway")</li>
            <li>📮 Search by ZIP code (e.g., "10001")</li>
            <li>🏢 Use a building ID if you know it</li>
            <li>🔍 Minimum 3 characters required</li>
          </ul>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="search-status">
          <div className="spinner"></div>
          <p>Searching...</p>
        </div>
      )}

      {/* Error message */}
      {error && !loading && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Search results */}
      {!loading && !error && buildings.length > 0 && (
        <div className="search-results">
          <div className="results-header">
            <h2>Found {buildings.length} building{buildings.length !== 1 ? 's' : ''}</h2>
            <p>Click a building to see detailed violation history</p>
          </div>

          <div className="results-grid">
            {buildings.map((building) => (
              <BuildingCard
                key={building.buildingid}
                building={building}
                onClick={() => handleBuildingClick(building)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Detailed view modal (will implement in next step) */}
      {selectedBuilding && (
        <div className="detail-modal">
          <div className="detail-modal-content">
            <button className="close-button" onClick={handleCloseDetail}>
              ✕
            </button>
            <h2>{selectedBuilding.full_address}</h2>
            <p>Building ID: {selectedBuilding.buildingid}</p>
            <p className="detail-note">
              🚧 Detailed view coming soon! Will show:
              <ul>
                <li>Complete violation history</li>
                <li>Violation timeline chart</li>
                <li>Class breakdown visualization</li>
                <li>Individual violation details</li>
              </ul>
            </p>
            <button onClick={handleCloseDetail} className="close-detail-button">
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
