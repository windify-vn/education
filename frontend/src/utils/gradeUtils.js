/**
 * Utility functions for grade/assessment handling
 */

/**
 * Get Tailwind CSS classes for grade badge based on grade value
 * Supports both Vietnamese grading (Xuất sắc, Giỏi, Khá, etc.) and letter grading (A, B, C, D, F)
 *
 * @param {string} grade - The grade value
 * @returns {string} Tailwind CSS classes
 */
export function getGradeBadgeClass(grade) {
  if (!grade) return 'bg-gray-100 text-gray-700'

  const g = grade.toString().trim()

  // Xếp loại tiếng Việt
  if (g === 'Xuất sắc' || g === 'Giỏi') return 'bg-green-100 text-green-700'
  if (g === 'Khá') return 'bg-blue-100 text-blue-700'
  if (g === 'Trung bình') return 'bg-amber-100 text-amber-700'
  if (g === 'Yếu' || g === 'Kém') return 'bg-red-100 text-red-700'

  // Xếp loại chữ cái
  const upper = g.toUpperCase()
  if (upper === 'A' || upper === 'A+') return 'bg-green-100 text-green-700'
  if (upper === 'B' || upper === 'B+') return 'bg-blue-100 text-blue-700'
  if (upper === 'C' || upper === 'C+') return 'bg-amber-100 text-amber-700'
  if (upper === 'D' || upper === 'D+' || upper === 'F')
    return 'bg-red-100 text-red-700'

  // Default cho các trường hợp khác
  return 'bg-gray-100 text-gray-700'
}

/**
 * Get score color based on percentage
 *
 * @param {number} percentage - Score percentage (0-100)
 * @returns {string} Hex color code
 */
export function getScoreColor(percentage) {
  if (percentage >= 80) return '#10B981' // green
  if (percentage >= 60) return '#F59E0B' // amber
  if (percentage >= 40) return '#F25A23' // primary/orange
  return '#EF4444' // red
}

/**
 * Get progress bar color class based on percentage
 *
 * @param {number} percentage - Progress percentage (0-100)
 * @returns {string} Tailwind CSS class
 */
export function getProgressColorClass(percentage) {
  if (percentage >= 80) return 'bg-green-500'
  if (percentage >= 60) return 'bg-amber-500'
  if (percentage >= 40) return 'bg-orange-500'
  return 'bg-red-500'
}
