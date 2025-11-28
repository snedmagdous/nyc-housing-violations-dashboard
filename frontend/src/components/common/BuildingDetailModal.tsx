/**
 * BuildingDetailModal Component
 *
 * Shows detailed information about a building including:
 * - Building summary (address, stats)
 * - Full list of violations with details
 * - Ability to filter/sort violations
 *
 * This modal appears when user clicks a BuildingCard
 */

// IMPORTS
// -------
// React hooks we'll use
import { useState, useEffect } from 'react';

// Our API service to fetch violation data
import { api } from '@/services/api';

// TypeScript types for type safety
import type { Building, Violation } from '@/types/violation';

// Styles for this component
import './BuildingDetailModal.css';


// COMPONENT PROPS (what gets passed in from parent)
// -------------------------------------------------
interface BuildingDetailModalProps {
  building: Building;           // The building to show details for
  isOpen: boolean;              // Whether modal is visible
  onClose: () => void;          // Function to call when closing modal
}


// MAIN COMPONENT
// --------------
export const BuildingDetailModal = ({ building, isOpen, onClose }: BuildingDetailModalProps) => {

  // STATE VARIABLES
  // ---------------
  // violations: Array of violation objects from the API
  // Initially empty [], will be filled when we fetch from API
  const [violations, setViolations] = useState<Violation[]>([]);

  // loading: Boolean - are we currently fetching data?
  // Shows spinner while waiting for API response
  const [loading, setLoading] = useState(false);

  // error: String or null - any error message to show user
  // If API call fails, we store the error message here
  const [error, setError] = useState<string | null>(null);


  // EFFECT: FETCH VIOLATIONS WHEN MODAL OPENS
  // ------------------------------------------
  // This runs whenever 'building' or 'isOpen' changes
  // Purpose: Load violation data from API when modal becomes visible
  useEffect(() => {
    // Only fetch if modal is actually open
    if (!isOpen) return;

    // Define async function to fetch violations
    // (can't use async directly in useEffect)
    const fetchViolations = async () => {
      try {
        setLoading(true);      // Show loading spinner
        setError(null);        // Clear any previous errors

        // Call our API service
        // This hits: GET /api/buildings/{building.buildingid}/violations
        const response = await api.violations.getByBuilding(building.buildingid);

        // Store the violations in state
        // This will trigger a re-render showing the violations
        setViolations(response);

      } catch (err) {
        // If API call fails, show error message to user
        console.error('Failed to fetch violations:', err);
        setError('Failed to load violations. Please try again.');
      } finally {
        // Always hide loading spinner, whether success or failure
        setLoading(false);
      }
    };

    // Execute the fetch function
    fetchViolations();
  }, [building.buildingid, isOpen]);  // Re-run if building changes or modal opens


  // HELPER FUNCTION: Format dates nicely
  // -------------------------------------
  // Converts "2025-11-18" to "Nov 18, 2025"
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };


  // HELPER FUNCTION: Get color for violation class
  // -----------------------------------------------
  // Returns CSS class name based on severity
  // Class C (most severe) = red, Class A (least) = yellow
  const getClassColor = (violationClass: string): string => {
    switch (violationClass) {
      case 'C': return 'class-c';        // Immediately hazardous - RED
      case 'I': return 'class-i';        // Immediately hazardous - RED
      case 'B': return 'class-b';        // Hazardous - ORANGE
      case 'A': return 'class-a';        // Non-hazardous - YELLOW
      default: return '';
    }
  };


  // DON'T RENDER IF MODAL IS CLOSED
  // --------------------------------
  // If isOpen is false, return null (render nothing)
  if (!isOpen) return null;


  // RENDER THE MODAL
  // ----------------
  return (
    // Overlay: Dark background covering whole screen
    // onClick={onClose}: Clicking backdrop closes modal
    <div className="modal-overlay" onClick={onClose}>

      {/* Modal content box - the actual white box in center */}
      {/* stopPropagation: Clicking inside box doesn't close modal */}
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>

        {/* HEADER SECTION */}
        {/* -------------- */}
        <div className="modal-header">
          <div>
            {/* Building address as main heading */}
            <h2>{building.full_address}</h2>

            {/* Secondary info: ID, borough, ZIP */}
            <p className="building-meta">
              Building ID: {building.buildingid} | {building.boro} | ZIP: {building.zip}
            </p>
          </div>

          {/* X button to close modal */}
          <button
            className="close-button"
            onClick={onClose}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>


        {/* SUMMARY STATS SECTION */}
        {/* --------------------- */}
        <div className="stats-section">
          {/* Grid of stat cards */}
          <div className="stat-card">
            <div className="stat-value">{building.total_violations}</div>
            <div className="stat-label">Total Violations</div>
          </div>

          <div className="stat-card highlight">
            <div className="stat-value">{building.open_violations}</div>
            <div className="stat-label">Open Violations</div>
          </div>

          <div className="stat-card">
            <div className="stat-value">{building.severe_violations}</div>
            <div className="stat-label">Severe (B/C)</div>
          </div>

          <div className="stat-card">
            <div className="stat-value">{building.risk_score.toFixed(1)}</div>
            <div className="stat-label">Risk Score</div>
          </div>
        </div>


        {/* VIOLATIONS LIST SECTION */}
        {/* ----------------------- */}
        <div className="violations-section">
          <h3>Violation History</h3>

          {/* LOADING STATE: Show spinner while fetching */}
          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading violations...</p>
            </div>
          )}

          {/* ERROR STATE: Show error message if fetch failed */}
          {error && (
            <div className="error-state">
              {error}
            </div>
          )}

          {/* SUCCESS STATE: Show list of violations */}
          {!loading && !error && violations.length > 0 && (
            <div className="violations-list">
              {/* Map over each violation and create a card */}
              {violations.map((violation) => (
                <div
                  key={violation.violationid}
                  className="violation-item"
                >
                  {/* Top row: Class badge, status, date */}
                  <div className="violation-header">
                    {/* Class badge (A, B, C) with color */}
                    <span className={`class-badge ${getClassColor(violation.class)}`}>
                      Class {violation.class}
                    </span>

                    {/* Status: OPEN or CLOSED */}
                    <span className={`status-badge ${violation.is_open ? 'open' : 'closed'}`}>
                      {violation.is_open ? 'OPEN' : 'CLOSED'}
                    </span>

                    {/* Inspection date */}
                    <span className="violation-date">
                      {formatDate(violation.inspectiondate)}
                    </span>
                  </div>

                  {/* Violation description - the actual problem */}
                  <div className="violation-description">
                    {violation.novdescription}
                  </div>

                  {/* Additional details */}
                  <div className="violation-meta">
                    {/* Apartment number if specific to an apartment */}
                    {violation.apartment && (
                      <span>Apt: {violation.apartment}</span>
                    )}

                    {/* Story/floor - handle basement/ground specially */}
                    {/* Only show if story is a valid number (including 0) */}
                    {violation.story !== null && violation.story !== undefined && (
                      <span>
                        {violation.story === 0
                          ? 'Ground/Basement'
                          : `Floor: ${violation.story}`
                        }
                      </span>
                    )}

                    {/* Rent impairing flag - important! */}
                    {violation.is_rent_impairing && (
                      <span className="rent-impairing">⚠ Rent Impairing</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* EMPTY STATE: No violations found */}
          {!loading && !error && violations.length === 0 && (
            <div className="empty-state">
              No violations found for this building.
            </div>
          )}
        </div>


        {/* FOOTER SECTION */}
        {/* -------------- */}
        <div className="modal-footer">
          <button className="close-btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
