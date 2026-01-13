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
import { MapContainer, TileLayer, GeoJSON, useMap, Marker, Popup } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Import heatmap plugin
// @ts-ignore - leaflet.heat doesn't have perfect TypeScript support
import 'leaflet.heat';

// API and types
import { api } from '@/services/api';
import type { Building } from '@/types/violation';

// Components
import { BuildingDetailModal } from '@/components/common/BuildingDetailModal';
import { FilterBar, type BuildingFilters } from '@/components/common/FilterBar';
import { FireIcon, MarkerIcon } from '@/components/common/Icons';

// Styles
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
  const pointsRef = useRef(points);

  // Update points ref when points change
  useEffect(() => {
    pointsRef.current = points;
  }, [points]);

  // Function to create/recreate heatmap
  const createHeatmap = () => {
    // Remove old heatmap layer if exists
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
      heatLayerRef.current = null;
    }

    if (pointsRef.current.length === 0) return;

    // Get current zoom level for dynamic sizing
    const currentZoom = map.getZoom();
    const dynamicRadius = Math.max(20, Math.min(50, currentZoom * 2.5));
    const dynamicBlur = Math.max(25, Math.min(60, currentZoom * 3));

    // Create heatmap layer
    // @ts-ignore
    heatLayerRef.current = L.heatLayer(pointsRef.current, {
      radius: dynamicRadius,
      blur: dynamicBlur,
      minOpacity: 0.6,
      maxZoom: 20,
      max: 100,
      gradient: {
        0.0: 'rgba(254, 249, 195, 0.6)',
        0.15: 'rgba(254, 240, 138, 0.65)',
        0.25: 'rgba(253, 224, 71, 0.7)',
        0.35: 'rgba(250, 204, 21, 0.75)',
        0.45: 'rgba(245, 158, 11, 0.8)',
        0.6: 'rgba(249, 115, 22, 0.85)',
        0.75: 'rgba(239, 68, 68, 0.9)',
        0.85: 'rgba(220, 38, 38, 0.93)',
        1.0: 'rgba(153, 27, 27, 0.95)',
      },
    }).addTo(map);
  };

  useEffect(() => {
    // Remove old markers
    markersRef.current.forEach(marker => map.removeLayer(marker));
    markersRef.current = [];

    // Create initial heatmap
    createHeatmap();

    if (buildings.length === 0) return;

    // Add invisible clickable markers for each building
    // These allow users to click on buildings but remain invisible
    const newMarkers = buildings.map((building) => {
      const marker = L.circleMarker([building.latitude, building.longitude], {
        radius: 10,         // Hit area for clicking
        fillOpacity: 0,     // Invisible
        opacity: 0,         // Invisible border
        fillColor: 'transparent',
        color: 'transparent',
        weight: 0,          // No border
        interactive: true,  // Still clickable
      });

      // Show enhanced tooltip on hover
      const riskColor = building.risk_score > 70 ? '#991b1b' :
                        building.risk_score > 50 ? '#ef4444' :
                        building.risk_score > 30 ? '#f59e0b' : '#facc15';

      marker.bindTooltip(`
        <div style="font-size: 0.875rem; min-width: 200px;">
          <div style="font-weight: 700; margin-bottom: 0.5rem; color: #1f2937;">
            ${building.full_address}
          </div>
          <div style="display: flex; gap: 0.5rem; margin-bottom: 0.25rem;">
            <span style="font-weight: 600; color: ${riskColor};">
              Risk: ${building.risk_score.toFixed(1)}
            </span>
            <span style="color: #6b7280;">•</span>
            <span style="color: #6b7280;">
              ${building.total_violations} total
            </span>
          </div>
          ${building.open_violations > 0 ? `
            <div style="font-size: 0.8125rem; color: #ef4444; margin-top: 0.25rem;">
              ⚠ ${building.open_violations} open violation${building.open_violations !== 1 ? 's' : ''}
            </div>
          ` : ''}
          ${building.class_c_count > 0 ? `
            <div style="font-size: 0.8125rem; color: #dc2626; font-weight: 600; margin-top: 0.25rem;">
              🚨 ${building.class_c_count} Class C (critical)
            </div>
          ` : ''}
          <div style="font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem; font-style: italic;">
            Click for details
          </div>
        </div>
      `, {
        direction: 'top',
        offset: [0, -10],
        className: 'building-tooltip',
      });

      // Click to show details
      marker.on('click', () => {
        onBuildingClick(building);
      });

      marker.addTo(map);
      return marker;
    });

    markersRef.current = newMarkers;

    // Recreate heatmap on zoom to ensure proper alignment
    const handleZoomEnd = () => {
      createHeatmap();
    };

    map.on('zoomend', handleZoomEnd);
    map.on('moveend', handleZoomEnd);

    // Cleanup on unmount
    return () => {
      map.off('zoomend', handleZoomEnd);
      map.off('moveend', handleZoomEnd);
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
  const hasSetInitialBoundsRef = useRef(false);

  useEffect(() => {
    // Only fit bounds on initial load, not when filters change
    if (!hasSetInitialBoundsRef.current) {
      if (buildings.length > 0) {
        // Fit map to show all buildings
        const bounds = L.latLngBounds(
          buildings.map(b => [b.latitude, b.longitude] as [number, number])
        );
        map.fitBounds(bounds, { padding: [50, 50] });
        hasSetInitialBoundsRef.current = true;
      } else {
        // Default NYC view
        map.setView([40.7128, -74.0060], 11);
        hasSetInitialBoundsRef.current = true;
      }
    }
  }, [buildings, map]);

  return null;
}


// BOROUGH LABEL COMPONENT
// ------------------------
function BoroughLabels() {
  const map = useMap();

  useEffect(() => {
    // Borough centroids (approximate centers for label placement)
    const boroughCenters: Array<{ name: string; coords: [number, number] }> = [
      { name: 'MANHATTAN', coords: [40.7831, -73.9712] },
      { name: 'BROOKLYN', coords: [40.6782, -73.9442] },
      { name: 'QUEENS', coords: [40.7282, -73.7949] },
      { name: 'BRONX', coords: [40.8448, -73.8648] },
      { name: 'STATEN ISLAND', coords: [40.5795, -74.1502] },
    ];

    console.log('Creating borough labels:', boroughCenters.length);

    const markers: L.Marker[] = [];

    boroughCenters.forEach(({ name, coords }) => {
      // Adjust icon size for Staten Island (longer name)
      const iconWidth = name === 'STATEN ISLAND' ? 140 : 120;

      const icon = L.divIcon({
        className: 'borough-label',
        html: `<div class="borough-label-text">${name}</div>`,
        iconSize: [iconWidth, 30],
        iconAnchor: [iconWidth / 2, 15],
      });

      const marker = L.marker(coords, {
        icon,
        interactive: false,
        zIndexOffset: 1000, // Ensure labels appear on top
      }).addTo(map);

      markers.push(marker);
      console.log(`Added label for ${name} at`, coords);
    });

    return () => {
      markers.forEach(marker => map.removeLayer(marker));
    };
  }, [map]);

  return null;
}


// COMPONENT TO ADD GRAY OVERLAY OUTSIDE NYC
// ------------------------------------------
// Simply adds a semi-transparent gray rectangle over the whole world
// The borough GeoJSON layers will be rendered on top with the actual map tiles showing through
function NYCMaskOverlay() {
  const map = useMap();

  useEffect(() => {
    // Just add a simple gray rectangle over everything
    // The map tiles and borough boundaries will show through
    const worldBounds: L.LatLngBoundsExpression = [
      [-90, -180],
      [90, 180]
    ];

    const grayOverlay = L.rectangle(worldBounds, {
      color: 'transparent',
      fillColor: '#374151',
      fillOpacity: 0.5,
      interactive: false,
      pane: 'tilePane', // Put it with the tiles so it's behind everything else
    }).addTo(map);

    console.log('Gray overlay added to map');

    return () => {
      map.removeLayer(grayOverlay);
    };
  }, [map]);

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
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'heatmap' | 'markers'>('heatmap');

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


  // FILTER BUILDINGS BY SEARCH QUERY
  // ---------------------------------
  const filteredBuildings = buildings.filter(building => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      building.full_address.toLowerCase().includes(query) ||
      building.boro.toLowerCase().includes(query)
    );
  });

  // CONVERT BUILDINGS TO HEATMAP POINTS
  // -----------------------------------
  // Each point is [lat, lng, intensity] where intensity is based on risk score
  const heatmapPoints: Array<[number, number, number]> = filteredBuildings.map(building => [
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
    color: '#9ca3af',      // Light gray border (sleek and subtle)
    weight: 1.5,           // Thinner border for sleeker look
    opacity: 0.6,          // Semi-transparent
    fillColor: 'none',     // No fill
    fillOpacity: 0,        // Transparent
  };


  // NYC CENTER COORDINATES
  // ----------------------
  const nycCenter: [number, number] = [40.7128, -74.0060];


  return (
    <div className="map-page-fullscreen">

      {/* FLOATING CONTROLS - TOP RIGHT */}
      <div className="map-controls-container">
        {/* Search Box */}
        <div className="map-search-box">
          <input
            type="text"
            placeholder="Search address, borough, or owner..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="map-search-input"
          />
          {searchQuery && (
            <button
              className="map-search-clear"
              onClick={() => setSearchQuery('')}
              aria-label="Clear search"
            >
              ✕
            </button>
          )}
        </div>

        {/* View Mode Toggle */}
        <div className="view-mode-toggle">
          <button
            className={viewMode === 'heatmap' ? 'active' : ''}
            onClick={() => setViewMode('heatmap')}
            aria-label="Heatmap view"
          >
            <FireIcon size={16} /> Heatmap
          </button>
          <button
            className={viewMode === 'markers' ? 'active' : ''}
            onClick={() => setViewMode('markers')}
            aria-label="Markers view"
          >
            <MarkerIcon size={16} /> Markers
          </button>
        </div>
      </div>

      {/* FILTER BUTTON - TOP LEFT NEXT TO ZOOM CONTROLS */}
      <div className="map-filter-left-container">
        <button
          className="filter-toggle-btn"
          onClick={() => setShowFilters(!showFilters)}
          aria-label="Toggle filters"
        >
          {showFilters ? '✕ Close' : '⚙ Filters'}
        </button>
      </div>

      {/* FLOATING FILTER PANEL */}
      {showFilters && (
        <div className="floating-filter-panel">
          <h3>Filter Violations</h3>
          <FilterBar filters={filters} onFilterChange={setFilters} />
          <div className="filter-stats">
            {searchQuery ? (
              <>
                Showing {filteredBuildings.length.toLocaleString()} of {buildings.length.toLocaleString()} buildings
              </>
            ) : (
              <>
                Showing {buildings.length.toLocaleString()} buildings
              </>
            )}
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

            {/* Borough name labels */}
            <BoroughLabels />

            {/* Gray overlay outside NYC */}
            <NYCMaskOverlay />

            {/* Auto-fit map bounds */}
            <MapBoundsController buildings={filteredBuildings} />

            {/* CONDITIONAL VIEW: HEATMAP OR MARKERS */}
            {viewMode === 'heatmap' ? (
              <HeatmapLayer
                points={heatmapPoints}
                buildings={filteredBuildings}
                onBuildingClick={handleBuildingClick}
              />
            ) : (
              <MarkerClusterGroup
                chunkedLoading
                maxClusterRadius={50}
                spiderfyOnMaxZoom
                showCoverageOnHover={false}
                zoomToBoundsOnClick
              >
                {filteredBuildings.map((building) => {
                  const riskColor = building.risk_score > 70 ? '#991b1b' :
                                    building.risk_score > 50 ? '#ef4444' :
                                    building.risk_score > 30 ? '#f59e0b' : '#facc15';

                  return (
                    <Marker
                      key={building.buildingid}
                      position={[building.latitude, building.longitude]}
                      eventHandlers={{
                        click: () => handleBuildingClick(building),
                      }}
                    >
                      <Popup>
                        <div style={{ minWidth: '200px' }}>
                          <div style={{ fontWeight: 700, marginBottom: '0.5rem', color: '#1f2937' }}>
                            {building.full_address}
                          </div>
                          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.25rem' }}>
                            <span style={{ fontWeight: 600, color: riskColor }}>
                              Risk: {building.risk_score.toFixed(1)}
                            </span>
                            <span style={{ color: '#6b7280' }}>•</span>
                            <span style={{ color: '#6b7280' }}>
                              {building.total_violations} violations
                            </span>
                          </div>
                          {building.open_violations > 0 && (
                            <div style={{ fontSize: '0.8125rem', color: '#ef4444', marginTop: '0.25rem' }}>
                              {building.open_violations} open violation{building.open_violations !== 1 ? 's' : ''}
                            </div>
                          )}
                          {building.class_c_count > 0 && (
                            <div style={{ fontSize: '0.8125rem', color: '#dc2626', fontWeight: 600, marginTop: '0.25rem' }}>
                              {building.class_c_count} Class C (critical)
                            </div>
                          )}
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}
              </MarkerClusterGroup>
            )}
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
