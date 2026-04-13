/**
 * ============================================================================
 * SHARED AUTHENTICATION MODULE
 * ============================================================================
 * Centralized auth for Node-RED endpoints.
 * Reads credentials from environment variables — never hardcoded.
 * ============================================================================
 */

function getAuthHeader() {
  const username = process.env.NODERED_API_USER;
  const password = process.env.NODERED_API_PASS;

  if (username && password) {
    const credentials = Buffer.from(`${username}:${password}`).toString('base64');
    return `Basic ${credentials}`;
  }

  console.warn('[auth] NODERED_API_USER / NODERED_API_PASS not set — requests will be unauthenticated');
  return null;
}

module.exports = { getAuthHeader };
