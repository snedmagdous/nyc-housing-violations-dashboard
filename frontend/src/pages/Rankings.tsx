/**
 * Landlord Rankings Page
 *
 * Shows "worst offender" landlords ranked by violations.
 *
 * TODO: Implement rankings with:
 * - Sortable table of landlords/owners
 * - Columns: name, building count, total violations, severe violations, risk score
 * - Bar chart visualization
 * - Filter by borough
 * - Click to see all buildings owned by landlord
 */

export const Rankings = () => {
  return (
    <div className="rankings-page">
      <h1>Landlord Rankings</h1>
      <p>Worst offenders: landlords and property owners with the most violations.</p>

      <div style={{ padding: '2rem', background: '#f7fafc', borderRadius: '8px' }}>
        <h2>📊 Coming Soon</h2>
        <p>This page will include:</p>
        <ul>
          <li>Sortable table of landlords by violation count</li>
          <li>Breakdown of violation classes (A, B, C)</li>
          <li>Number of buildings per landlord</li>
          <li>Average risk score</li>
          <li>Bar chart visualization</li>
          <li>Filter by borough and sort options</li>
        </ul>
      </div>
    </div>
  );
};
