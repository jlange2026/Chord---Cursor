/**
 * ============================================================================
 * SHARED HELPER FUNCTIONS
 * ============================================================================
 * Null-value detection, error checking, and parameter normalization
 * used across all Chord tools.
 * ============================================================================
 */

/**
 * Flowise uses "***" as a sentinel for null values since it cannot
 * reliably pass null through schema validation.
 */
function isNullValue(value) {
  return value === null ||
    value === undefined ||
    value === '' ||
    value === '***' ||
    value === 'NULL' ||
    value === 'null' ||
    (typeof value === 'string' && value.trim() === '');
}

function normalizeParam(value) {
  if (typeof value === 'undefined') return null;
  if (isNullValue(value)) return null;
  return value;
}

function safeGetVar(getter) {
  try { return getter(); }
  catch { return undefined; }
}

/**
 * Detects error patterns returned by Node-RED / Denticon backend.
 * Returns error message string if error detected, null otherwise.
 */
function checkForError(data) {
  if (!data || typeof data !== 'object') return null;

  if (data.success === false) {
    return data.error || data.message || 'Operation failed';
  }

  if (data.code === false) {
    return Array.isArray(data.error) ? data.error.join(', ') : (data.error || data.message || 'API returned error');
  }

  if (typeof data === 'string' && data.toLowerCase().includes('failed')) {
    return data;
  }

  if (data.error && !data.data && !data.id && !data.slots && !data.groups && !data.appointments) {
    return Array.isArray(data.error) ? data.error.join(', ') : data.error;
  }

  return null;
}

module.exports = { isNullValue, normalizeParam, safeGetVar, checkForError };
