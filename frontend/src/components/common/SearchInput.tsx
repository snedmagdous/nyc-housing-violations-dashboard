/**
 * SearchInput Component
 *
 * A search input with a search icon and clear button.
 * Handles user input and triggers search callbacks.
 *
 * Props:
 * - value: Current search value (controlled component)
 * - onChange: Called when user types
 * - onSearch: Called when user submits (hits Enter)
 * - placeholder: Placeholder text
 * - loading: Shows loading indicator
 */

import { useState } from 'react';
import { SearchIcon } from './Icons';
import './SearchInput.css';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  onSearch?: () => void;
  placeholder?: string;
  loading?: boolean;
}

export const SearchInput = ({
  value,
  onChange,
  onSearch,
  placeholder = 'Search by address, zip code, or building ID...',
  loading = false,
}: SearchInputProps) => {
  const [isFocused, setIsFocused] = useState(false);

  /**
   * Handle Enter key press to trigger search
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && onSearch) {
      onSearch();
    }
  };

  /**
   * Clear the search input
   */
  const handleClear = () => {
    onChange('');
  };

  return (
    <div className={`search-input-wrapper ${isFocused ? 'focused' : ''}`}>
      {/* Search icon */}
      <div className="search-icon">
        {loading ? (
          // Loading spinner
          <div className="spinner-small" />
        ) : (
          // Search icon
          <SearchIcon size={20} />
        )}
      </div>

      {/* Input field */}
      <input
        type="search"
        id="building-search"
        className="search-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={placeholder}
        aria-label="Search for buildings by address, zip code, or building ID"
      />

      {/* Clear button (only shown when there's text) */}
      {value && (
        <button
          type="button"
          className="clear-button"
          onClick={handleClear}
          aria-label="Clear search"
        >
          ✕
        </button>
      )}
    </div>
  );
};
