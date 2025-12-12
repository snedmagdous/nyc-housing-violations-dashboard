/**
 * Building Search Page
 *
 * Allows users to search for buildings by address and filter by various criteria.
 *
 * Flow:
 * 1. User can type in search input OR use filters (or both!)
 * 2. After 500ms of no typing (debounced), API call is made
 * 3. Results are displayed as BuildingCard components
 * 4. User can click a card to see detailed view
 */

import { useState, useEffect } from 'react';
import { api } from '@/services/api';
import type { Building } from '@/types/violation';
import { SearchInput } from '@/components/common/SearchInput';
import { BuildingCard } from '@/components/common/BuildingCard';
import { FilterBar, type BuildingFilters } from '@/components/common/FilterBar';
import { BuildingDetailModal } from '@/components/common/BuildingDetailModal';
import { Pagination } from '@/components/common/Pagination';
import { useDebounce } from '@/hooks/useDebounce';
import './Search.css';

export const Search = () => {
  // State for search query (what user types)
  const [searchQuery, setSearchQuery] = useState('');

  // State for filters (borough, min violations, etc.)
  const [filters, setFilters] = useState<BuildingFilters>({});

  // State for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const RESULTS_PER_PAGE = 50;  // Show 50 buildings per page

  // State for search results from API
  const [buildings, setBuildings] = useState<Building[]>([]);

  // State for total count (may be more than what we're showing)
  const [totalCount, setTotalCount] = useState<number>(0);

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
   * Effect: Fetch buildings when search query or filters change
   *
   * Smart behavior:
   * - If there's a search query (3+ chars), use search endpoint
   * - If there are only filters, use list endpoint
   * - Filters apply to search results too!
   */
  useEffect(() => {
    const fetchBuildings = async () => {
      try {
        setLoading(true);
        setError(null);

        // Case 1: Text search with optional filters
        if (debouncedQuery.length >= 3) {
          // Use search endpoint and filter results client-side
          const response = await api.buildings.search(debouncedQuery);
          let results = response.buildings;

          // Apply borough filter if set
          if (filters.borough) {
            results = results.filter(b => b.boro === filters.borough);
          }

          setBuildings(results);
          setTotalCount(results.length);

          if (results.length === 0) {
            setError('No buildings found. Try adjusting your search or filters.');
          }
        }
        // Case 2: Only filters (no text search)
        else if (filters.borough || filters.minViolations || filters.minOpenViolations || filters.minRiskScore || filters.hasClassC) {
          // Fetch current page of results
          const response = await api.buildings.getAll({
            borough: filters.borough,
            min_violations: filters.minViolations,
            min_open_violations: filters.minOpenViolations,
            min_risk_score: filters.minRiskScore,
            has_class_c: filters.hasClassC,
            page: currentPage,
            page_size: RESULTS_PER_PAGE,  // 50 per page
            sort_by: 'risk_score',  // Show highest risk first
            sort_order: 'desc',
          });
          setBuildings(response.buildings);
          setTotalCount(response.total);  // Total available in database

          if (response.buildings.length === 0) {
            setError('No buildings found with these filters.');
          }
        }
        // Case 3: No search and no filters - show nothing
        else {
          setBuildings([]);
          setTotalCount(0);
        }
      } catch (err) {
        console.error('Search error:', err);
        setError('Failed to fetch buildings. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    // Only fetch if there's a query or filters
    const hasFilters = filters.borough || filters.minViolations || filters.minOpenViolations || filters.minRiskScore || filters.hasClassC;
    if (debouncedQuery.length >= 3 || hasFilters) {
      fetchBuildings();
    } else {
      setBuildings([]);
      setError(null);
    }
  }, [debouncedQuery, filters, currentPage]); // Re-run when query, filters, OR page changes

  /**
   * Reset to page 1 when filters change
   */
  useEffect(() => {
    setCurrentPage(1);
  }, [filters, debouncedQuery]);

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

  /**
   * Calculate total pages
   */
  const totalPages = Math.ceil(totalCount / RESULTS_PER_PAGE);

  /**
   * Handle page change
   */
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll to top of results
    window.scrollTo({ top: 0, behavior: 'smooth' });
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

      {/* Filter bar */}
      <FilterBar filters={filters} onFilterChange={setFilters} />

      {/* Search hints */}
      {searchQuery.length === 0 && !filters.borough && !filters.minViolations && !filters.minOpenViolations && !filters.minRiskScore && !filters.hasClassC && (
        <div className="search-hints">
          <h3>Search Tips:</h3>
          <ul>
            <li>🏠 Enter a street address (e.g., "123 Broadway")</li>
            <li>📮 Search by ZIP code (e.g., "10001")</li>
            <li>🏢 Use a building ID if you know it</li>
            <li>🔍 Minimum 3 characters required OR use filters below</li>
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
            <h2>
              {totalCount > buildings.length ? (
                <>Showing {buildings.length} of {totalCount.toLocaleString()} buildings</>
              ) : (
                <>Found {buildings.length} building{buildings.length !== 1 ? 's' : ''}</>
              )}
            </h2>
            <p>
              {totalCount > buildings.length && 'Top results sorted by risk score. '}
              Click a building to see detailed violation history
            </p>
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

          {/* Pagination - only show for filtered results */}
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          )}
        </div>
      )}

      {/* Building Detail Modal - Shows full violation history */}
      {selectedBuilding && (
        <BuildingDetailModal
          building={selectedBuilding}
          isOpen={true}
          onClose={handleCloseDetail}
        />
      )}
    </div>
  );
};
