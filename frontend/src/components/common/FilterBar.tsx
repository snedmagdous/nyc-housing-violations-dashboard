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

        {/* Future filters will go here */}
        {/*
        <div className="filter-group">
          <label htmlFor="min-violations-filter">Min Violations</label>
          <input
            type="number"
            id="min-violations-filter"
            className="filter-input"
            placeholder="e.g. 5"
            min="0"
          />
        </div>
        */}
      </div>
    </div>
  );
};
