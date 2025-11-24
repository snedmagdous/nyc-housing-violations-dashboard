/**
 * TypeScript type definitions for NYC Housing Violations
 *
 * These types match the data structure from your PostgreSQL database
 * and FastAPI backend. They provide type safety and autocomplete in your IDE.
 */

/**
 * Violation severity classes in NYC housing code:
 * - Class A: Non-hazardous violations (e.g., peeling paint in non-lead areas)
 * - Class B: Hazardous violations (e.g., no heat, water leaks)
 * - Class C: Immediately hazardous violations (e.g., no heat in winter, major structural issues)
 * - Class I: Violations that are immediately hazardous
 */
export type ViolationClass = 'A' | 'B' | 'C' | 'I';

/**
 * Main Violation interface - represents a single housing code violation
 */
export interface Violation {
  // Unique identifiers
  violationid: number;
  buildingid: number;

  // Building location information
  boro: string;                    // Borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island)
  housenumber: string;
  streetname: string;
  full_address: string;            // Formatted full address
  zip: string;

  // Building identifiers used by NYC
  bin: string | null;              // Building Identification Number
  bbl: string | null;              // Borough-Block-Lot number

  // Geographic data
  latitude: number;
  longitude: number;
  nta: string | null;              // Neighborhood Tabulation Area
  communityboard: string | null;

  // Violation details
  class: ViolationClass;           // Severity class
  inspectiondate: string;          // ISO date string
  approveddate: string | null;
  originalcertifybydate: string | null;
  originalcorrectbydate: string | null;
  novid: number;
  novdescription: string;
  novissueddate: string | null;

  // Current status
  currentstatusid: number;
  currentstatus: string;
  currentstatusdate: string | null;

  // Derived fields from your data cleaning pipeline
  severity_score: number;          // Numerical score based on class (C=3, B=2, A=1)
  is_open: boolean;                // Whether violation is still open
  is_severe: boolean;              // Class B or C
  is_rent_impairing: boolean;      // Affects habitability (heat, water, etc.)

  // Temporal fields for analysis
  year: number;
  month: number;
  quarter: number;
}

/**
 * Aggregated building data with violation statistics
 * Used for the building search and rankings features
 */
export interface Building {
  buildingid: number;
  bin: string | null;
  bbl: string | null;
  boro: string;
  full_address: string;
  zip: string;

  // Geographic data
  latitude: number;
  longitude: number;
  nta: string | null;
  communityboard: string | null;
  geom: any;  // PostGIS geometry object

  // Aggregated violation statistics
  total_violations: number;
  open_violations: number;
  class_a_count: number;
  class_b_count: number;
  class_c_count: number;
  class_i_count: number;
  severe_violations: number;
  rent_impairing_violations: number;

  // Temporal information
  first_violation_date: string;
  most_recent_violation_date: string;

  // Risk assessment (from your ML model)
  risk_score: number;
}

/**
 * API response wrapper for paginated results
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

/**
 * Filters for querying violations
 * Used in search forms and API requests
 */
export interface ViolationFilters {
  // Geographic filters
  boro?: string;
  zip?: string;
  nta?: string;

  // Violation characteristics
  class?: ViolationClass[];
  is_open?: boolean;
  is_severe?: boolean;
  is_rent_impairing?: boolean;

  // Date range
  start_date?: string;
  end_date?: string;

  // Pagination
  page?: number;
  per_page?: number;
}

/**
 * Temporal aggregation for trend analysis
 * Used in charts showing violations over time
 */
export interface TemporalAggregation {
  date: string;              // Date or month
  count: number;             // Number of violations
  class_a_count?: number;
  class_b_count?: number;
  class_c_count?: number;
}

/**
 * Geographic cluster/hotspot data for map visualization
 */
export interface ViolationHotspot {
  center: [number, number];  // [latitude, longitude]
  radius: number;            // Radius in meters
  violation_count: number;
  severity_score: number;
}

/**
 * Landlord/owner ranking data
 * For "worst offenders" feature
 */
export interface LandlordRanking {
  owner_name: string;
  building_count: number;
  total_violations: number;
  severe_violations: number;
  open_violations: number;
  avg_risk_score: number;
}
