// Convert 'YYYY-MM-DD' to 'DD-MM-YYYY'
export function formatDateYMDToDMY(input) {
  if (!input) return ''

  // If Date instance
  if (input instanceof Date && !isNaN(input)) {
    const yyyy = input.getFullYear()
    const mm = String(input.getMonth() + 1).padStart(2, '0')
    const dd = String(input.getDate()).padStart(2, '0')
    return `${dd}-${mm}-${yyyy}`
  }

  // If string 'YYYY-MM-DD' (or with time)
  const str = String(input).trim()
  const datePart = str.split('T')[0]
  const parts = datePart.split('-')
  if (parts.length !== 3) return str

  const [yyyy, mm, dd] = parts
  if (!yyyy || !mm || !dd) return str
  return `${dd.padStart(2, '0')}-${mm.padStart(2, '0')}-${yyyy}`
}

// Convert 'YYYY-MM-DD HH:MM:SS[.fraction]' to 'HH:MM:SS DD-MM-YYYY'
export function formatDateTimeToTimeDMY(input) {
  if (!input) return ''

  // Accept Date or string
  if (input instanceof Date && !isNaN(input)) {
    const yyyy = input.getFullYear()
    const mm = String(input.getMonth() + 1).padStart(2, '0')
    const dd = String(input.getDate()).padStart(2, '0')
    const hh = String(input.getHours()).padStart(2, '0')
    const mi = String(input.getMinutes()).padStart(2, '0')
    const ss = String(input.getSeconds()).padStart(2, '0')
    return `${hh}:${mi}:${ss} ${dd}-${mm}-${yyyy}`
  }

  const str = String(input).trim()
  // Split by space or 'T'
  const [datePartRaw, timePartRaw] = str.replace('T', ' ').split(' ')
  if (!datePartRaw) return str
  const datePart = datePartRaw.split('.')[0] || datePartRaw
  const [yyyy, mm, dd] = datePart.split('-')
  if (!yyyy || !mm || !dd) return str

  // Time part may include fractional seconds
  let hh = '00', mi = '00', ss = '00'
  if (timePartRaw) {
    const timePart = timePartRaw.split('.')[0] // drop fraction
    const t = timePart.split(':')
    hh = String(t[0] || '00').padStart(2, '0')
    mi = String(t[1] || '00').padStart(2, '0')
    ss = String(t[2] || '00').padStart(2, '0')
  }

  return `${hh}:${mi}:${ss} ${String(dd).padStart(2, '0')}-${String(mm).padStart(2, '0')}-${yyyy}`
}

export default {
  formatDateYMDToDMY,
  formatDateTimeToTimeDMY,
}


