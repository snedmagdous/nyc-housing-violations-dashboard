/**
 * Building Search Page
 *
 * Allows users to search for buildings by address and view violation history.
 *
 * TODO: Implement search functionality with:
 * - Search input with autocomplete
 * - Results list showing buildings matching query
 * - Building detail view with violation breakdown
 * - Filters (borough, violation class, date range)
 */

export const Search = () => {
  return (
    <div className="search-page">
      <h1>Building Search</h1>
      <p>Search for NYC buildings by address to view their violation history.</p>

      <div style={{ padding: '2rem', background: '#f7fafc', borderRadius: '8px' }}>
        <h2>🚧 Coming Soon</h2>
        <p>This page will include:</p>
        <ul>
          <li>Address search with autocomplete</li>
          <li>Building violation history</li>
          <li>Severity breakdown charts</li>
          <li>Timeline of violations</li>
          <li>Risk score display</li>
        </ul>
      </div>
    </div>
  );
};
