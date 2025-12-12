/**
 * FilterBar Component
 *
 * Provides filtering controls for building search.
 * Starting with borough filter, can easily add more filters later.
 *
 * Props:
 * - filters: Current filter values
 * - onFilterChange: Callback when any filter changes
 */

import './FilterBar.css';

export interface BuildingFilters {
  borough?: string;
  minViolations?: number;
  minOpenViolations?: number;
  minRiskScore?: number;
  hasClassC?: boolean;
  sortBy?: string;
}

interface FilterBarProps {
  filters: BuildingFilters;
  onFilterChange: (filters: BuildingFilters) => void;
}

export const FilterBar = ({ filters, onFilterChange }: FilterBarProps) => {
  /**
   * Handle borough selection change
   */
  const handleBoroughChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onFilterChange({
      ...filters,
      borough: value === '' ? undefined : value,
    });
  };

  /**
   * Handle minimum violations change
   */
  const handleMinViolationsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onFilterChange({
      ...filters,
      minViolations: value === '' ? undefined : parseInt(value),
    });
  };

  /**
   * Handle minimum open violations change
   */
  const handleMinOpenViolationsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onFilterChange({
      ...filters,
      minOpenViolations: value === '' ? undefined : parseInt(value),
    });
  };

  /**
   * Handle minimum risk score change
   */
  const handleMinRiskScoreChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onFilterChange({
      ...filters,
      minRiskScore: value === '' ? undefined : parseInt(value),
    });
  };

  /**
   * Handle has Class C violations checkbox
   */
  const handleHasClassCChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({
      ...filters,
      hasClassC: e.target.checked ? true : undefined,
    });
  };

  /**
   * Clear all filters
   */
  const handleClearFilters = () => {
    onFilterChange({});
  };

  /**
   * Count how many filters are active
   */
  const activeFilterCount = Object.values(filters).filter(
    (value) => value !== undefined && value !== ''
  ).length;

  return (
    <div className="filter-bar">
      <div className="filter-bar-header">
        <h3>Filters</h3>
        {activeFilterCount > 0 && (
          <button className="clear-filters-btn" onClick={handleClearFilters}>
            Clear all ({activeFilterCount})
          </button>
        )}
      </div>

      <div className="filter-controls">
        {/* Borough Filter */}
        <div className="filter-group">
          <label htmlFor="borough-filter">Borough</label>
          <select
            id="borough-filter"
            className="filter-select"
            value={filters.borough || ''}
            onChange={handleBoroughChange}
          >
            <option value="">All Boroughs</option>
            <option value="BROOKLYN">Brooklyn</option>
            <option value="BRONX">Bronx</option>
            <option value="MANHATTAN">Manhattan</option>
            <option value="QUEENS">Queens</option>
            <option value="STATEN ISLAND">Staten Island</option>
          </select>
        </div>

        {/* Min Violations Filter */}
        <div className="filter-group">
          <label htmlFor="min-violations-filter">Min Total Violations</label>
          <input
            type="number"
            id="min-violations-filter"
            className="filter-input"
            placeholder="e.g. 10"
            min="0"
            value={filters.minViolations || ''}
            onChange={handleMinViolationsChange}
          />
        </div>

        {/* Min Open Violations Filter */}
        <div className="filter-group">
          <label htmlFor="min-open-violations-filter">Min Open Violations</label>
          <input
            type="number"
            id="min-open-violations-filter"
            className="filter-input"
            placeholder="e.g. 5"
            min="0"
            value={filters.minOpenViolations || ''}
            onChange={handleMinOpenViolationsChange}
          />
        </div>

        {/* Min Risk Score Filter */}
        <div className="filter-group">
          <label htmlFor="min-risk-score-filter">Min Risk Score (0-100)</label>
          <input
            type="number"
            id="min-risk-score-filter"
            className="filter-input"
            placeholder="e.g. 50"
            min="0"
            max="100"
            value={filters.minRiskScore || ''}
            onChange={handleMinRiskScoreChange}
          />
        </div>

        {/* Class C (Severe) Violations Filter */}
        <div className="filter-group filter-checkbox">
          <label htmlFor="has-class-c-filter">
            <input
              type="checkbox"
              id="has-class-c-filter"
              className="filter-checkbox-input"
              checked={filters.hasClassC || false}
              onChange={handleHasClassCChange}
            />
            <span>Only buildings with Class C violations</span>
          </label>
        </div>
      </div>
    </div>
  );
};
