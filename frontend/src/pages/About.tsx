/**
 * About Page
 *
 * Explains the project mission, methodology, and data sources.
 * Provides context for why this tool exists and how to use it.
 */

import {
  TargetIcon,
  DatabaseIcon,
  MicroscopeIcon,
  ShieldIcon,
  CodeIcon,
  UserIcon,
  HeartIcon,
} from '@/components/common/Icons';
import './About.css';

export const About = () => {
  return (
    <div className="about-page">
      <h1>About This Project</h1>

      <section className="about-section">
        <div className="section-header">
          <div className="section-icon">
            <TargetIcon size={32} />
          </div>
          <h2>Mission</h2>
        </div>
        <p>
          This dashboard was built to hold landlords accountable through data transparency.
          Thousands of NYC tenants live in buildings with serious housing code violations—lack
          of heat, broken plumbing, pest infestations, and more. While this data is publicly
          available, it's fragmented and difficult to interpret.
        </p>
        <p>
          This tool transforms raw violation data into actionable insights, making it accessible
          for tenants, advocates, journalists, and policymakers fighting for housing justice.
        </p>
      </section>

      <section className="about-section">
        <div className="section-header">
          <div className="section-icon">
            <DatabaseIcon size={32} />
          </div>
          <h2>Data Sources</h2>
        </div>
        <ul>
          <li>
            <strong>HPD Housing Maintenance Code Violations</strong> - NYC Open Data
            <br />
            1.5M+ violation records from 2018-present
          </li>
          <li>
            <strong>Building Information</strong> - Including ownership, location, and
            characteristics
          </li>
          <li>
            <strong>Geographic Data</strong> - NYC borough boundaries and neighborhood tabulation
            areas
          </li>
        </ul>
      </section>

      <section className="about-section">
        <div className="section-header">
          <div className="section-icon">
            <MicroscopeIcon size={32} />
          </div>
          <h2>Methodology</h2>
        </div>
        <p>The analysis pipeline includes:</p>
        <ul>
          <li>
            <strong>Data Cleaning</strong> - Standardizing addresses, handling missing values,
            removing duplicates
          </li>
          <li>
            <strong>Feature Engineering</strong> - Creating severity scores, risk indicators,
            and temporal features
          </li>
          <li>
            <strong>Geospatial Analysis</strong> - Identifying violation hotspots and clustering
          </li>
          <li>
            <strong>Machine Learning</strong> - Predicting building risk scores for proactive
            intervention
          </li>
          <li>
            <strong>Statistical Testing</strong> - Identifying significant disparities in
            enforcement
          </li>
        </ul>
      </section>

      <section className="about-section">
        <div className="section-header">
          <div className="section-icon">
            <ShieldIcon size={32} />
          </div>
          <h2>Understanding Violation Classes</h2>
        </div>
        <div className="violation-classes">
          <div className="class-card class-c">
            <h3>Class C</h3>
            <p>
              <strong>Immediately Hazardous</strong>
              <br />
              Conditions that pose imminent danger to life or health (e.g., no heat in winter,
              major structural problems)
            </p>
          </div>
          <div className="class-card class-b">
            <h3>Class B</h3>
            <p>
              <strong>Hazardous</strong>
              <br />
              Conditions that are hazardous but not immediately dangerous (e.g., water leaks,
              insufficient lighting)
            </p>
          </div>
          <div className="class-card class-a">
            <h3>Class A</h3>
            <p>
              <strong>Non-Hazardous</strong>
              <br />
              Conditions that are violations but not hazardous (e.g., peeling paint in non-lead
              areas)
            </p>
          </div>
        </div>
      </section>

      <section className="about-section">
        <div className="section-header">
          <div className="section-icon">
            <CodeIcon size={32} />
          </div>
          <h2>Technology</h2>
        </div>
        <p>Built with:</p>
        <ul>
          <li>
            <strong>Backend:</strong> FastAPI, PostgreSQL with PostGIS, Python (pandas,
            scikit-learn)
          </li>
          <li>
            <strong>Frontend:</strong> React, TypeScript, Recharts, Leaflet
          </li>
          <li>
            <strong>Data Pipeline:</strong> ETL with data validation and quality checks
          </li>
        </ul>
      </section>

      <section className="about-section">
        <div className="section-header">
          <div className="section-icon">
            <UserIcon size={32} />
          </div>
          <h2>About the Developer</h2>
        </div>
        <p>
          <strong>Maya Murry</strong>
          <br />
          Cornell University, B.Sc. Computer Science (May 2025)
          <br />
          Lead Full-Stack Developer at an AI Healthcare Startup
        </p>
        <p>
          This project was built as a portfolio piece demonstrating data engineering, full-stack
          development, and commitment to using technology for social impact.
        </p>
        <div className="contact-links">
          <a
            href="https://github.com/snedmagdous/nyc-housing-violations-dashboard"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub Repository
          </a>
          <a href="https://mayamurry.com" target="_blank" rel="noopener noreferrer">
            Portfolio
          </a>
          <a
            href="https://www.linkedin.com/in/maya-murry"
            target="_blank"
            rel="noopener noreferrer"
          >
            LinkedIn
          </a>
        </div>
      </section>

      <section className="about-section">
        <div className="section-header">
          <div className="section-icon">
            <HeartIcon size={32} />
          </div>
          <h2>Acknowledgments</h2>
        </div>
        <p>
          This project uses data from NYC Open Data and builds on the work of tenant advocacy
          organizations fighting for housing justice across New York City.
        </p>
        <p>
          <em>
            Technology should serve the collective, dismantle systems of oppression, and empower
            those fighting for their rights.
          </em>
        </p>
      </section>
    </div>
  );
};
