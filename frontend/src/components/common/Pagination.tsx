/**
 * Pagination Component
 *
 * Shows page numbers and navigation controls
 *
 * Design:
 * - Previous button
 * - Page numbers (1, 2, 3, ... if many pages)
 * - Next button
 * - Highlights current page
 */

import './Pagination.css';

interface PaginationProps {
  currentPage: number;      // Which page we're on now
  totalPages: number;       // Total number of pages
  onPageChange: (page: number) => void;  // Called when user clicks a page
}

export const Pagination = ({ currentPage, totalPages, onPageChange }: PaginationProps) => {

  // Don't show pagination if only 1 page or no pages
  if (totalPages <= 1) return null;

  /**
   * Generate array of page numbers to show
   *
   * Logic:
   * - Always show first page, last page, current page
   * - Show 2 pages before and after current
   * - Use "..." for gaps
   *
   * Examples:
   * - If current = 1, total = 10: [1, 2, 3, 4, 5, ..., 10]
   * - If current = 5, total = 10: [1, ..., 3, 4, 5, 6, 7, ..., 10]
   * - If current = 10, total = 10: [1, ..., 6, 7, 8, 9, 10]
   */
  const getPageNumbers = (): (number | string)[] => {
    const pages: (number | string)[] = [];

    // If 7 or fewer pages, show all
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
      return pages;
    }

    // Always add first page
    pages.push(1);

    // Calculate range around current page
    const startPage = Math.max(2, currentPage - 2);
    const endPage = Math.min(totalPages - 1, currentPage + 2);

    // Add ... if gap between 1 and start
    if (startPage > 2) {
      pages.push('...');
    }

    // Add pages around current
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    // Add ... if gap before last page
    if (endPage < totalPages - 1) {
      pages.push('...');
    }

    // Always add last page
    pages.push(totalPages);

    return pages;
  };

  const pageNumbers = getPageNumbers();

  return (
    <div className="pagination">
      {/* Previous button */}
      <button
        className="pagination-btn"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        aria-label="Previous page"
      >
        « Previous
      </button>

      {/* Page numbers */}
      {pageNumbers.map((page, index) => {
        // If it's "...", show as text (not clickable)
        if (page === '...') {
          return (
            <span key={`ellipsis-${index}`} className="pagination-ellipsis">
              ...
            </span>
          );
        }

        // Otherwise it's a page number
        const pageNum = page as number;
        return (
          <button
            key={pageNum}
            className={`pagination-btn ${currentPage === pageNum ? 'active' : ''}`}
            onClick={() => onPageChange(pageNum)}
          >
            {pageNum}
          </button>
        );
      })}

      {/* Next button */}
      <button
        className="pagination-btn"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        aria-label="Next page"
      >
        Next »
      </button>
    </div>
  );
};
