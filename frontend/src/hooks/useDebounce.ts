/**
 * useDebounce Hook
 *
 * Delays updating a value until the user stops changing it.
 * Useful for search inputs - prevents making API calls on every keystroke.
 *
 * How it works:
 * 1. User types "hello" quickly
 * 2. Hook waits 500ms after last keystroke
 * 3. Only then returns the final value "hello"
 * 4. This triggers only ONE API call instead of 5
 *
 * @param value - The value to debounce (e.g., search query)
 * @param delay - How long to wait in milliseconds (default: 500ms)
 * @returns The debounced value
 *
 * Example usage:
 * const [searchQuery, setSearchQuery] = useState('');
 * const debouncedQuery = useDebounce(searchQuery, 500);
 *
 * useEffect(() => {
 *   // This only runs 500ms after user stops typing
 *   api.buildings.search(debouncedQuery);
 * }, [debouncedQuery]);
 */

import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number = 500): T {
  // State to store the debounced value
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // Set up a timer to update debounced value after delay
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Cleanup function: cancel the timer if value changes again
    // This is the "debouncing" - we cancel and restart the timer on each change
    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]); // Re-run when value or delay changes

  return debouncedValue;
}
