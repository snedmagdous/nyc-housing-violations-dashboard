/**
 * Violation Density Heatmap
 *
 * Full-screen interactive heatmap showing violation density across NYC.
 * Visual style similar to election density maps (blue/red) but using
 * green → yellow → red gradient for violation severity.
 *
 * Features:
 * - Full-screen Leaflet map with NYC borough boundaries
 * - Heatmap layer showing violation density
 * - Color gradient: green (low) → yellow (medium) → red (high)
 * - Floating filter panel
 * - Click buildings to see details
 */

// IMPORTS
// -------
import { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

// API and types
import { api } from '@/services/api';
import type { Building } from '@/types/violation';

// Components
import { BuildingDetailModal } from '@/components/common/BuildingDetailModal';
import { FilterBar, type BuildingFilters } from '@/components/common/FilterBar';

// Styles
import 'leaflet/dist/leaflet.css';
import './Map.css';

// NYC borough boundaries GeoJSON
import nycBoroughs from '@/data/nyc-boroughs.json';


// HEATMAP LAYER COMPONENT
// -----------------------
// Custom component that creates a heatmap layer using leaflet.heat
interface HeatmapLayerProps {
  points: Array<[number, number, number]>; // [lat, lng, intensity]
  buildings: Building[]; // For click interaction
  onBuildingClick: (building: Building) => void;
}

function HeatmapLayer({ points, buildings, onBuildingClick }: HeatmapLayerProps) {
  const map = useMap();
  const heatLayerRef = useRef<any>(null);
  const markersRef = useRef<L.CircleMarker[]>([]);

  useEffect(() => {
    // Remove old heatmap layer if exists
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
    }

    // Remove old markers
    markersRef.current.forEach(marker => map.removeLayer(marker));
    markersRef.current = [];

    if (points.length === 0) return;

    // Create heatmap layer with custom gradient (yellow → red)
    heatLayerRef.current = (L as any).heatLayer(points, {
      radius: 25,           // Size of heat points
      blur: 35,             // Blur amount
      maxZoom: 17,          // Max zoom where heatmap shows
      max: 100,             // Maximum intensity value
      gradient: {           // Color gradient (yellow to red, no green)
        0.0: '#fef08a',     // Very light yellow (low)
        0.2: '#fde047',     // Light yellow
        0.35: '#facc15',    // Yellow
        0.5: '#f59e0b',     // Orange
        0.7: '#ef4444',     // Red
        1.0: '#b91c1c',     // Dark red (critical)
      },
    }).addTo(map);

    // Add invisible clickable markers for each building
    // These allow users to click on buildings even though we're showing a heatmap
    const newMarkers = buildings.map((building) => {
      const marker = L.circleMarker([building.latitude, building.longitude], {
        radius: 8,
        fillOpacity: 0,     // Invisible
        opacity: 0,         // Invisible
        interactive: true,  // But still clickable!
      });

      // Show tooltip on hover
      marker.bindTooltip(`
        <div style="font-size: 0.875rem;">
          <strong>${building.full_address}</strong><br/>
          <span style="color: #ef4444;">Risk: ${building.risk_score.toFixed(1)}</span> |
          ${building.total_violations} violations
        </div>
      `, {
        direction: 'top',
        offset: [0, -10],
      });

      // Click to show details
      marker.on('click', () => {
        onBuildingClick(building);
      });

      marker.addTo(map);
      return marker;
    });

    markersRef.current = newMarkers;

    // Cleanup on unmount
    return () => {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current);
      }
      markersRef.current.forEach(marker => map.removeLayer(marker));
    };
  }, [points, buildings, map, onBuildingClick]);

  return null;
}


// COMPONENT TO FIT MAP TO NYC BOUNDS
// -----------------------------------
function MapBoundsController({ buildings }: { buildings: Building[] }) {
  const map = useMap();

  useEffect(() => {
    if (buildings.length > 0) {
      // Fit map to show all buildings
      const bounds = L.latLngBounds(
        buildings.map(b => [b.latitude, b.longitude] as [number, number])
      );
      map.fitBounds(bounds, { padding: [50, 50] });
    } else {
      // Default NYC view
      map.setView([40.7128, -74.0060], 11);
    }
  }, [buildings, map]);

  return null;
}


// MAIN MAP COMPONENT
// ------------------
export const Map = () => {

  // STATE
  // -----
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(null);
  const [filters, setFilters] = useState<BuildingFilters>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);


  // FETCH BUILDINGS ON MOUNT AND WHEN FILTERS CHANGE
  // ------------------------------------------------
  useEffect(() => {
    const fetchBuildings = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch buildings based on filters
        const response = await api.buildings.getAll({
          borough: filters.borough,
          page: 1,
          page_size: 1000,  // Maximum allowed by API
          sort_by: 'risk_score',
          sort_order: 'desc',
        });

        setBuildings(response.buildings);
      } catch (err) {
        console.error('Failed to fetch buildings:', err);
        setError('Failed to load map data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchBuildings();
  }, [filters]);


  // CONVERT BUILDINGS TO HEATMAP POINTS
  // -----------------------------------
  // Each point is [lat, lng, intensity] where intensity is based on risk score
  const heatmapPoints: Array<[number, number, number]> = buildings.map(building => [
    building.latitude,
    building.longitude,
    building.risk_score, // Use risk score as intensity (0-100)
  ]);


  // HANDLE BUILDING CLICK
  // ---------------------
  const handleBuildingClick = (building: Building) => {
    setSelectedBuilding(building);
  };


  // BOROUGH BOUNDARY STYLE
  // ----------------------
  const boroughStyle = {
    color: '#374151',      // Medium gray border (visible on light map)
    weight: 2.5,           // Border width
    opacity: 0.9,          // Border opacity
    fillColor: 'none',     // No fill
    fillOpacity: 0,        // Transparent
  };


  // NYC CENTER COORDINATES
  // ----------------------
  const nycCenter: [number, number] = [40.7128, -74.0060];


  return (
    <div className="map-page-fullscreen">

      {/* FLOATING FILTER TOGGLE BUTTON */}
      <button
        className="filter-toggle-btn"
        onClick={() => setShowFilters(!showFilters)}
        aria-label="Toggle filters"
      >
        {showFilters ? '✕ Close' : '⚙ Filters'}
      </button>

      {/* FLOATING FILTER PANEL */}
      {showFilters && (
        <div className="floating-filter-panel">
          <h3>Filter Violations</h3>
          <FilterBar filters={filters} onFilterChange={setFilters} />
          <div className="filter-stats">
            Showing {buildings.length.toLocaleString()} buildings
          </div>
        </div>
      )}

      {/* LOADING OVERLAY */}
      {loading && (
        <div className="map-loading-overlay">
          <div className="spinner"></div>
          <p>Loading violation data...</p>
        </div>
      )}

      {/* ERROR OVERLAY */}
      {error && (
        <div className="map-error-overlay">
          <div className="error-content">
            <h3>Error Loading Map</h3>
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>
              Retry
            </button>
          </div>
        </div>
      )}

      {/* THE MAP - FULL SCREEN */}
      {!error && (
        <div className="map-container-fullscreen">
          <MapContainer
            center={nycCenter}
            zoom={11}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={true}
            zoomControl={true}
          >
            {/* Base map tiles - Light theme */}
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* NYC Borough Boundaries */}
            <GeoJSON
              data={nycBoroughs as any}
              style={boroughStyle}
            />

            {/* Auto-fit map bounds */}
            <MapBoundsController buildings={buildings} />

            {/* HEATMAP LAYER */}
            <HeatmapLayer
              points={heatmapPoints}
              buildings={buildings}
              onBuildingClick={handleBuildingClick}
            />
          </MapContainer>

          {/* LEGEND - Floating bottom-right */}
          <div className="map-legend-fullscreen">
            <h4>Violation Density</h4>
            <div className="legend-gradient">
              <div className="gradient-bar"></div>
              <div className="gradient-labels">
                <span>Low</span>
                <span>Medium</span>
                <span>High</span>
              </div>
            </div>
            <div className="legend-note">
              Hover over areas to see building details
            </div>
          </div>
        </div>
      )}

      {/* BUILDING DETAIL MODAL */}
      {selectedBuilding && (
        <BuildingDetailModal
          building={selectedBuilding}
          isOpen={true}
          onClose={() => setSelectedBuilding(null)}
        />
      )}
    </div>
  );
};
