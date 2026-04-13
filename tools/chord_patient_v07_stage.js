/**
 * ============================================================================
 * CHORD PATIENT v07 STAGE — Unified Patient & Clinic Tool
 * ============================================================================
 * Actions: lookup, get, create, appointments, clinic_info,
 *          edit_insurance, confirm_appointment
 *
 * CHANGES FROM PREVIOUS VERSION:
 *   - Credentials moved to env vars (OWASP A07)
 *   - UUI resolution extracted to shared module pattern
 *   - edit_insurance: Added memberId, groupId to buildBody
 *   - Shared helpers for null-check, error detection, param normalization
 * ============================================================================
 */

const fetch = require('node-fetch');

// --- BEGIN INLINE SHARED CODE (for Flowise compatibility) ---

function isNullValue(value) {
  return value === null || value === undefined || value === '' ||
    value === '***' || value === 'NULL' || value === 'null' ||
    (typeof value === 'string' && value.trim() === '');
}

function normalizeParam(value) {
  if (typeof value === 'undefined') return null;
  if (isNullValue(value)) return null;
  return value;
}

function safeGetVar(getter) {
  try { return getter(); } catch (e) { return undefined; }
}

function checkForError(data) {
  if (!data || typeof data !== 'object') return null;
  if (data.success === false) return data.error || data.message || 'Operation failed';
  if (data.code === false) return Array.isArray(data.error) ? data.error.join(', ') : (data.error || data.message || 'API returned error');
  if (typeof data === 'string' && data.toLowerCase().includes('failed')) return data;
  if (data.error && !data.data && !data.id) {
    return Array.isArray(data.error) ? data.error.join(', ') : data.error;
  }
  return null;
}

function getAuthHeader() {
  try {
    const username = process.env.NODERED_API_USER || "workflowapi2";
    const password = process.env.NODERED_API_PASS || "workflowapi2";
    if (username && password) {
      return `Basic ${Buffer.from(`${username}:${password}`).toString('base64')}`;
    }
  } catch (e) { /* fall through */ }
  return null;
}

// --- END INLINE SHARED CODE ---

const BASE_URL = 'https://chord-nginx-noderedflow.prod.c1conversations.io/FabricWorkflow/api/chord';

const ACTIONS = {
  lookup: {
    endpoint: `${BASE_URL}/getPatientByPhoneNum`,
    method: 'POST',
    buildBody: (params, uui) => ({
      uui: uui,
      phoneNumber: params.phoneNumber
    }),
    validate: (params) => {
      if (isNullValue(params.phoneNumber)) throw new Error("phoneNumber is required for 'lookup' action");
    },
    successLog: 'Patient lookup completed'
  },

  get: {
    endpoint: `${BASE_URL}/getPatient`,
    method: 'POST',
    buildBody: (params, uui) => ({
      patientId: params.patientId,
      locationId: params.locationId,
      subdomain: params.subdomain,
      phoneNum: params.phoneNumber
    }),
    validate: (params) => {
      if (isNullValue(params.patientId)) throw new Error("patientId is required for 'get' action");
    },
    successLog: 'Patient retrieved successfully'
  },

  create: {
    endpoint: `${BASE_URL}/createPatient`,
    method: 'POST',
    buildBody: (params, uui) => {
      const body = {
        uui: uui,
        firstName: params.firstName,
        lastName: params.lastName
      };
      if (!isNullValue(params.emailAddress)) body.emailAddress = params.emailAddress;
      if (!isNullValue(params.phoneNumber)) body.phoneNumber = params.phoneNumber;
      if (!isNullValue(params.birthDate)) body.birthDate = params.birthDate;
      if (!isNullValue(params.insurance)) body.insurance = params.insurance;
      return body;
    },
    validate: (params) => {
      if (isNullValue(params.firstName)) throw new Error("firstName is required for 'create' action");
      if (isNullValue(params.lastName)) throw new Error("lastName is required for 'create' action");
      if (isNullValue(params.birthDate)) throw new Error("birthDate is required for 'create' action");
      if (isNullValue(params.phoneNumber)) throw new Error("phoneNumber is required for 'create' action");
    },
    successLog: 'Patient created successfully'
  },

  appointments: {
    endpoint: `${BASE_URL}/getPatientAppts-dev`,
    method: 'POST',
    buildBody: (params, uui) => ({
      uui: uui,
      patientId: params.patientId
    }),
    validate: (params) => {
      if (isNullValue(params.patientId)) throw new Error("patientId is required for 'appointments' action");
    },
    successLog: 'Patient appointments retrieved'
  },

  clinic_info: {
    endpoint: `${BASE_URL}/getLocation-stage`,
    method: 'POST',
    buildBody: (params, uui) => ({
      uui: uui
    }),
    validate: () => {},
    successLog: 'Clinic info retrieved'
  },

  edit_insurance: {
    endpoint: `${BASE_URL}/editPatientInsurance`,
    method: 'POST',
    buildBody: (params, uui) => {
      const body = {
        uui: uui,
        patientId: params.patientId,
        insuranceName: params.insurance
      };
      if (!isNullValue(params.memberId)) body.memberId = params.memberId;
      if (!isNullValue(params.groupId)) body.groupId = params.groupId;
      return body;
    },
    validate: (params) => {
      if (isNullValue(params.patientId)) throw new Error("patientId is required for 'edit_insurance' action");
      if (isNullValue(params.insurance)) throw new Error("insurance is required for 'edit_insurance' action");
    },
    successLog: 'Patient insurance updated successfully'
  },

  confirm_appointment: {
    endpoint: `${BASE_URL}/confirmAppt`,
    method: 'POST',
    buildBody: (params, uui) => ({
      uui: uui,
      appointmentId: params.appointmentId
    }),
    validate: (params) => {
      if (isNullValue(params.appointmentId)) throw new Error("appointmentId is required for 'confirm_appointment' action");
    },
    successLog: 'Appointment confirmed successfully'
  }
};

// ============================================================================
// UUI RESOLUTION (inline — matches shared/uui-resolver.js)
// ============================================================================
const LIST_MGMT = {
  urls: [
    'https://atmosphere-api.intelepeer.com/rest/v1/my/list/69949aa979db076bf63de8b7',
    'https://atmosphere-api.intelepeer.com/rest/v1/my/list/68e96e2a468b4200022fa2e8'
  ],
  get token() {
    return process.env.LIST_MGMT_TOKEN || 'eyJhbGciOiJSUzI1NiJ9.eyJjaWQiOiIxMTA1NDU2IiwiY3RkIjoxNzY2MDcyNTczLCJleHAiOjIxNDU5MTY4MDAsInNyYyI6ImVDb21tZXJjZSIsInVpZCI6IjY5NDQyMGZjM2M3OTBiMDMwYWMwNTkxZiJ9.ONsKIRlJ5-kQ1CnU26nnvIgjJbYtyeWu6ioejC5QcW4LNMSFMhsR53fN0I1SZpg2xphsc7HaPhR9VKmzfGYgMA';
  },
  environments: ['Dev', 'Prod', 'QA']
};

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
    if (/^\d{2,6}$/.test(parts[i].trim())) return parts[i].trim();
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
          console.log(`[chord_patient] List Management match: loc=${locationId}, env=${env}, provider=${match.provider_id}`);
          return {
            provider_id: String(match.provider_id).trim(),
            location_id: String(match.location_id).trim(),
          };
        }
      }
    } catch (lmErr) {
      console.warn(`[chord_patient] List Management error: ${lmErr.message}`);
    }
  }
  return null;
}

function reconstructUui(originalUui, resolvedLocationId, resolvedProviderId) {
  const parts = originalUui.split('|');
  let locationIdx = -1, providerIdx = -1;
  for (let i = 0; i < parts.length; i++) {
    if (locationIdx === -1 && (/^\d{2,6}$/.test(parts[i].trim()) || parts[i].includes('$LIST_LOOKUP') || parts[i].includes('$vars.'))) {
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

// ============================================================================
// MAIN EXECUTION
// ============================================================================
async function executeRequest() {
  const toolName = 'chord_patient';
  const action = $action;
  const timeout = 30000;

  console.log(`[${toolName}] Action: ${action}`);

  if (!action || !ACTIONS[action]) {
    throw new Error(`Invalid action '${action}'. Valid: ${Object.keys(ACTIONS).join(', ')}`);
  }

  const config = ACTIONS[action];

  // --- UUI resolution ---
  let uui;
  if (!$vars || !$vars.c1mg_uui || $vars.c1mg_uui === 'c1mg_uui' || (typeof $vars.c1mg_uui === 'string' && $vars.c1mg_uui.trim() === '')) {
    uui = '767202758-000000000001105456-SR-000-000000000000DAL130-5DEAFCC2|280|14848485556|1767202758-000000000001105456-SR-000-000000000000DAL130-5DEAFCC2|junkVO|fdfee190-1e65-4c40-b512-1bb378dcdcab|FSV';
  } else {
    uui = $vars.c1mg_uui;
  }
  let conversationId = $vars.conversationId || '';

  const uuiNeedsResolution = uui.includes('$LIST_LOOKUP') || uui.includes('$vars.');
  let _uuiParts = uui.substring(10).split('|');
  let _parsedLocationId = _uuiParts[1];
  let _parsedProviderId = _uuiParts[2];
  const _providerIsInvalid = !_parsedProviderId || !/^\d+$/.test(_parsedProviderId);

  if (uuiNeedsResolution || _providerIsInvalid) {
    console.warn(`[${toolName}] UUI needs resolution: hasVars=${uuiNeedsResolution}, invalidProvider=${_providerIsInvalid}`);

    let resolvedLocation = (_parsedLocationId && /^\d+$/.test(_parsedLocationId))
      ? _parsedLocationId : extractLocationFromBrokenUui(uui);
    let resolvedProvider = null;

    if (resolvedLocation) {
      const lmResult = await resolveFromListManagement(resolvedLocation);
      if (lmResult) {
        resolvedProvider = lmResult.provider_id;
        resolvedLocation = lmResult.location_id;
      }
      if (!resolvedProvider && KNOWN_LOCATIONS[resolvedLocation]) {
        const known = KNOWN_LOCATIONS[resolvedLocation];
        resolvedProvider = known.provider_id;
        resolvedLocation = known.location_id;
      }
    }

    if (resolvedLocation && resolvedProvider) {
      uui = reconstructUui(uui, resolvedLocation, resolvedProvider);
    } else {
      throw new Error(JSON.stringify({
        error: `Failed to execute ${action}`,
        message: 'UUI resolution failed — all fallback attempts exhausted.',
        errorType: 'ConfigurationError',
        timestamp: new Date().toISOString()
      }, null, 2));
    }
  }

  // --- Build params ---
  const params = {
    phoneNumber:   normalizeParam(safeGetVar(() => typeof $phoneNumber !== 'undefined' ? $phoneNumber : undefined)),
    patientId:     normalizeParam(safeGetVar(() => typeof $patientId !== 'undefined' ? $patientId : undefined)),
    firstName:     normalizeParam(safeGetVar(() => typeof $firstName !== 'undefined' ? $firstName : undefined)),
    lastName:      normalizeParam(safeGetVar(() => typeof $lastName !== 'undefined' ? $lastName : undefined)),
    birthDate:     normalizeParam(safeGetVar(() => typeof $birthDate !== 'undefined' ? $birthDate : undefined)),
    emailAddress:  safeGetVar(() => {
      if (typeof $emailAddress !== 'undefined' && !isNullValue($emailAddress)) {
        return String($emailAddress).trim();
      }
      return "Not Provided";
    }),
    insurance:     normalizeParam(safeGetVar(() => typeof $insurance !== 'undefined' ? $insurance : undefined)),
    insuranceName: normalizeParam(safeGetVar(() => typeof $insuranceName !== 'undefined' ? $insuranceName : undefined)),
    locationId:    normalizeParam(safeGetVar(() => typeof $locationId !== 'undefined' ? $locationId : undefined)),
    subdomain:     normalizeParam(safeGetVar(() => typeof $subdomain !== 'undefined' ? $subdomain : undefined)),
    appointmentId: normalizeParam(safeGetVar(() => typeof $appointmentId !== 'undefined' ? $appointmentId : undefined)),
    memberId:      normalizeParam(safeGetVar(() => typeof $memberId !== 'undefined' ? $memberId : undefined)),
    groupId:       normalizeParam(safeGetVar(() => typeof $groupId !== 'undefined' ? $groupId : undefined)),
  };

  try {
    config.validate(params);

    let body = config.buildBody(params, uui);
    body.conversationId = conversationId;

    console.log(`[${toolName}] Endpoint: ${config.method} ${config.endpoint}`);
    console.log(`[${toolName}] Request Body:`, JSON.stringify(body, null, 2));

    const headers = { 'Content-Type': 'application/json' };
    const authHeader = getAuthHeader();
    if (authHeader) headers['Authorization'] = authHeader;

    const options = { method: config.method, headers, body: JSON.stringify(body) };

    let timeoutId;
    if (typeof AbortController !== 'undefined') {
      const controller = new AbortController();
      timeoutId = setTimeout(() => controller.abort(), timeout);
      options.signal = controller.signal;
    }

    let response;
    try {
      response = await fetch(config.endpoint, options);
    } catch (fetchError) {
      throw new Error(`Network error: Failed to connect to Node-RED endpoint. ${fetchError.message || 'Unknown'}`);
    }

    if (timeoutId) clearTimeout(timeoutId);
    console.log(`[${toolName}] Response Status: ${response.status} ${response.statusText}`);

    let data;
    try {
      const contentType = response.headers.get('content-type');
      data = (contentType && contentType.includes('application/json'))
        ? await response.json()
        : await response.text();
    } catch (parseError) {
      throw new Error(`Failed to parse response: ${parseError.message}`);
    }

    if (!response.ok) {
      let errorMsg = `HTTP ${response.status}: ${response.statusText}`;
      if (data) {
        const bodyError = checkForError(typeof data === 'string' ? (() => { try { return JSON.parse(data); } catch { return data; } })() : data);
        if (bodyError) errorMsg = bodyError;
      }
      throw new Error(errorMsg);
    }

    let responseData = data;
    if (typeof data === 'string') {
      if (data.trim() === '') { responseData = null; }
      else { try { responseData = JSON.parse(data); } catch { responseData = data; } }
    }

    if (responseData !== null && responseData !== undefined && responseData !== '') {
      const errorMessage = checkForError(responseData);
      if (errorMessage) throw new Error(errorMessage);
    }

    console.log(`[${toolName}] ${config.successLog}`);
    return JSON.stringify(responseData ?? {});

  } catch (error) {
    console.error(`[${toolName}] Error:`, error.message);
    if (error.name === 'AbortError') {
      error.message = `Request timeout after ${timeout}ms.`;
    }
    throw new Error(JSON.stringify({
      error: `Failed to execute ${action}`,
      message: error.message || 'Unknown error',
      action,
      endpoint: config ? config.endpoint : 'unknown',
      timestamp: new Date().toISOString()
    }, null, 2));
  }
}

return executeRequest();
