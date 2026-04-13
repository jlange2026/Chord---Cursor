/**
 * ============================================================================
 * SHARED UUI RESOLVER MODULE
 * ============================================================================
 * Centralized UUI resolution logic used by chord_patient and chord_scheduling.
 * Eliminates duplication — a single fix here propagates to all tools.
 *
 * Fallback chain:
 *   1. IntelePeer List Management API (both list IDs, all environments)
 *   2. Hardcoded known-good location mappings (safety net)
 *   3. Fail only if ALL resolution attempts fail
 * ============================================================================
 */

const fetch = require('node-fetch');

const LIST_MGMT = {
  urls: [
    'https://atmosphere-api.intelepeer.com/rest/v1/my/list/69949aa979db076bf63de8b7',
    'https://atmosphere-api.intelepeer.com/rest/v1/my/list/68e96e2a468b4200022fa2e8'
  ],
  get token() {
    return process.env.LIST_MGMT_TOKEN || '';
  },
  environments: ['Dev', 'Prod', 'QA']
};

// Safety-net fallback — expand as new locations onboard.
// Prefer List Management API; this exists only for when the API is unreachable.
const KNOWN_LOCATIONS = {
  '4097':   { provider_id: '69008194',  location_id: '4097',   office: 'CDH Aston' },
  '24026':  { provider_id: '117329705', location_id: '24026',  office: 'CDH Bethlehem' },
  '4120':   { provider_id: '69008227',  location_id: '4120',   office: 'CDH Bensalem' },
  '4103':   { provider_id: '69008331',  location_id: '4103',   office: 'CDH Downingtown' },
  '4146':   { provider_id: '69008164',  location_id: '4146',   office: 'CDH Easton' },
  '326485': { provider_id: '400012598', location_id: '326485', office: 'CDH Exton' },
};

function extractLocationFromBrokenUui(brokenUui) {
  const parts = brokenUui.split('|');
  for (let i = 0; i < parts.length; i++) {
    if (/^\d{2,6}$/.test(parts[i].trim())) {
      return parts[i].trim();
    }
  }
  return null;
}

async function resolveFromListManagement(locationId) {
  for (const url of LIST_MGMT.urls) {
    try {
      const lmResp = await fetch(url, {
        method: 'GET',
        headers: { 'Authorization': LIST_MGMT.token },
        timeout: 5000
      });
      if (!lmResp.ok) continue;

      const lmData = await lmResp.json();
      const rows = lmData?.data?.data || lmData?.data || [];
      if (!Array.isArray(rows)) continue;

      for (const env of LIST_MGMT.environments) {
        const match = rows.find(row =>
          String(row.location_id || '').trim() === String(locationId).trim() &&
          String(row.environment || '').trim().toLowerCase() === env.toLowerCase()
        );
        if (match && match.provider_id && /^\d+$/.test(String(match.provider_id).trim())) {
          return {
            provider_id: String(match.provider_id).trim(),
            location_id: String(match.location_id).trim(),
            environment: env,
            source: 'list_management_api',
            did: match.DID || match.did || null,
            office: match.office_name || match.Location || null
          };
        }
      }
    } catch (lmErr) {
      console.warn(`[uui-resolver] List Management error for ${url}: ${lmErr.message}`);
    }
  }
  return null;
}

function reconstructUui(originalUui, resolvedLocationId, resolvedProviderId) {
  const parts = originalUui.split('|');
  let locationIdx = -1;
  let providerIdx = -1;

  for (let i = 0; i < parts.length; i++) {
    if (locationIdx === -1 &&
        (/^\d{2,6}$/.test(parts[i].trim()) ||
         parts[i].includes('$LIST_LOOKUP') ||
         parts[i].includes('$vars.'))) {
      locationIdx = i;
    } else if (locationIdx !== -1 && providerIdx === -1) {
      providerIdx = i;
      break;
    }
  }

  if (locationIdx !== -1) parts[locationIdx] = resolvedLocationId;
  if (providerIdx !== -1) parts[providerIdx] = resolvedProviderId;
  return parts.join('|');
}

/**
 * Resolves a potentially broken UUI into a valid one.
 * @param {string} uui - The raw UUI string
 * @param {string} toolName - Calling tool name (for logging)
 * @returns {Promise<string>} - Resolved UUI
 * @throws {Error} - If all resolution attempts fail
 */
async function resolveUui(uui, toolName) {
  const uuiNeedsResolution = uui.includes('$LIST_LOOKUP') || uui.includes('$vars.');
  let parts = uui.substring(10).split('|');
  let parsedLocationId = parts[1];
  let parsedProviderId = parts[2];
  const providerIsInvalid = !parsedProviderId || !/^\d+$/.test(parsedProviderId);

  if (!uuiNeedsResolution && !providerIsInvalid) {
    return uui;
  }

  console.warn(`[${toolName}] UUI needs resolution: hasVars=${uuiNeedsResolution}, invalidProvider=${providerIsInvalid}`);

  let resolvedLocation = (parsedLocationId && /^\d+$/.test(parsedLocationId))
    ? parsedLocationId
    : extractLocationFromBrokenUui(uui);

  let resolvedProvider = null;

  if (resolvedLocation) {
    const lmResult = await resolveFromListManagement(resolvedLocation);
    if (lmResult) {
      resolvedProvider = lmResult.provider_id;
      resolvedLocation = lmResult.location_id;
      console.log(`[${toolName}] Resolved via List Management: loc=${resolvedLocation}, provider=${resolvedProvider}`);
    }

    if (!resolvedProvider && KNOWN_LOCATIONS[resolvedLocation]) {
      const known = KNOWN_LOCATIONS[resolvedLocation];
      resolvedProvider = known.provider_id;
      resolvedLocation = known.location_id;
      console.log(`[${toolName}] Resolved via hardcoded fallback: ${known.office}`);
    }
  }

  if (resolvedLocation && resolvedProvider) {
    const resolved = reconstructUui(uui, resolvedLocation, resolvedProvider);
    console.log(`[${toolName}] UUI resolved successfully`);
    return resolved;
  }

  throw new Error(JSON.stringify({
    error: 'UUI resolution failed',
    message: 'All fallback resolution attempts failed.',
    errorType: 'ConfigurationError',
    location_extracted: resolvedLocation || 'NONE',
    timestamp: new Date().toISOString()
  }, null, 2));
}

module.exports = { resolveUui, KNOWN_LOCATIONS };
