/**
 * BuildingCard Component
 *
 * Displays a building's summary information as a card.
 * Used in search results to show building at a glance.
 *
 * Props explained:
 * - building: The building data from the API
 * - onClick: Function to call when card is clicked (to show details)
 */

import type { Building } from '@/types/violation';
import './BuildingCard.css';

interface BuildingCardProps {
  building: Building;
  onClick?: () => void;  // Optional click handler
}

export const BuildingCard = ({ building, onClick }: BuildingCardProps) => {
  /**
   * Helper function to determine risk level based on score
   * Risk score is a number - we convert it to a label and color
   */
  const getRiskLevel = (score: number): { label: string; className: string } => {
    if (score >= 75) return { label: 'Critical', className: 'risk-critical' };
    if (score >= 50) return { label: 'High', className: 'risk-high' };
    if (score >= 25) return { label: 'Medium', className: 'risk-medium' };
    return { label: 'Low', className: 'risk-low' };
  };

  const risk = getRiskLevel(building.risk_score);

  return (
    <div
      className={`building-card ${onClick ? 'clickable' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {/* Header with address and borough */}
      <div className="building-header">
        <h3 className="building-address">{building.full_address}</h3>
        <span className="building-borough">{building.boro}</span>
      </div>

      {/* Risk score badge */}
      <div className={`risk-badge ${risk.className}`}>
        {risk.label} Risk
        <span className="risk-score">{building.risk_score.toFixed(1)}</span>
      </div>

      {/* Statistics grid */}
      <div className="building-stats">
        <div className="stat">
          <span className="stat-label">Total Violations</span>
          <span className="stat-value">{building.total_violations}</span>
        </div>

        <div className="stat">
          <span className="stat-label">Open</span>
          <span className="stat-value highlight">{building.open_violations}</span>
        </div>

        <div className="stat">
          <span className="stat-label">Severe (B/C)</span>
          <span className="stat-value">{building.severe_violations}</span>
        </div>

        <div className="stat">
          <span className="stat-label">Rent Impairing</span>
          <span className="stat-value">{building.rent_impairing_violations}</span>
        </div>
      </div>

      {/* Violation class breakdown */}
      <div className="violation-breakdown">
        <div className="breakdown-item">
          <span className="class-label class-c">Class C</span>
          <span>{building.class_c_count}</span>
        </div>
        <div className="breakdown-item">
          <span className="class-label class-b">Class B</span>
          <span>{building.class_b_count}</span>
        </div>
        <div className="breakdown-item">
          <span className="class-label class-a">Class A</span>
          <span>{building.class_a_count}</span>
        </div>
      </div>

      {/* Additional info */}
      <div className="building-footer">
        <span className="building-id">Building ID: {building.buildingid}</span>
      </div>

      {/* Click hint if clickable */}
      {onClick && (
        <div className="click-hint">
          Click for details →
        </div>
      )}
    </div>
  );
};
