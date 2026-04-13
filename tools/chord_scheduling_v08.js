/**
 * ============================================================================
 * CHORD SCHEDULING v08 — Unified Appointment Scheduling Tool
 * ============================================================================
 * Actions: slots, grouped_slots, book, book_child, cancel
 *
 * CHANGES FROM PREVIOUS VERSION:
 *   - Credentials moved to env vars (OWASP A07)
 *   - UUI resolution extracted to shared module
 *   - book_child: phoneNumber validation UNCOMMENTED (required)
 *   - book_child: providerId validation UNCOMMENTED (required)
 *   - book_child: productionTypeId added to buildBody
 *   - Shared helpers for null-check, error detection, param normalization
 * ============================================================================
 */

const fetch = require('node-fetch');

// ============================================================================
// SHARED MODULES — In Flowise, inline these or use Flowise's module system.
// For standalone Node.js, uncomment the require() lines below.
// ============================================================================
// const { resolveUui } = require('./shared/uui-resolver');
// const { getAuthHeader } = require('./shared/auth');
// const { isNullValue, normalizeParam, safeGetVar, checkForError } = require('./shared/helpers');

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
  if (data.error && !data.data && !data.id && !data.slots && !data.groups && !data.appointments) {
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

const DEFAULT_VALUES = {
  timeWindowMinutes: 60
};

const ACTIONS = {
  slots: {
    endpoint: `${BASE_URL}/getApptSlots-dev`,
    method: 'POST',
    buildBody: (params, uui) => ({
      uui: uui,
      isNewPatient: params.isNewPatient,
      patientDob: params.patientDob,
      searchStartDate: params.searchStartDate
    }),
    validate: (params) => {
      if (isNullValue(params.isNewPatient)) throw new Error("isNewPatient is required for 'slots' action");
      if (isNullValue(params.patientDob)) throw new Error("patientDob is required for 'slots' action");
    },
    successLog: (data) => `Found ${data.totalSlots || (data.slots ? data.slots.length : 0) || 0} available slots`
  },

  grouped_slots: {
    endpoint: `${BASE_URL}/getGroupedApptSlots-dev`,
    method: 'POST',
    buildBody: (params, uui) => ({
      uui: uui,
      numberOfAppointments: params.numberOfPatients,
      timeWindowMinutes: params.timeWindowMinutes,
      isNewPatient: params.isNewPatient,
      patientDob: params.patientDob,
      searchStartDate: params.searchStartDate
    }),
    validate: (params) => {
      if (isNullValue(params.numberOfPatients)) throw new Error("numberOfPatients is required for 'grouped_slots' action");
      if (isNullValue(params.isNewPatient)) throw new Error("isNewPatient is required for 'grouped_slots' action");
      if (isNullValue(params.patientDob)) throw new Error("patientDob is required for 'grouped_slots' action");
    },
    successLog: (data) => `Found ${data.totalGroups || (data.groups ? data.groups.length : 0) || 0} grouped slot options`
  },

  book: {
    endpoint: `${BASE_URL}/createAppt`,
    method: 'POST',
    buildBody: (params, uui) => ({
      uui: uui,
      patientId: params.patientId,
      apptTime: params.appointmentTime,
      operatoryId: params.operatoryId,
      apptDate: params.appointmentDate,
      productionTypeId: params.productionTypeId
    }),
    validate: (params) => {
      if (isNullValue(params.patientId)) throw new Error("patientId is required for 'book' action");
      if (isNullValue(params.appointmentDate)) throw new Error("appointmentDate is required for 'book' action");
      if (isNullValue(params.appointmentTime)) throw new Error("appointmentTime is required for 'book' action");
      if (isNullValue(params.operatoryId)) throw new Error("operatoryId is required for 'book' action");
    },
    successLog: () => 'Appointment booked successfully'
  },

  book_child: {
    endpoint: `${BASE_URL}/createChildAppt-dev`,
    method: 'POST',
    buildBody: (params, uui) => ({
      uui: uui,
      phoneNumber: params.phoneNumber,
      childFirstName: params.childFirstName,
      childLastName: params.childLastName,
      childDateOfBirth: params.childDateOfBirth,
      apptTime: params.appointmentTime,
      operatoryId: params.operatoryId,
      apptDate: params.appointmentDate,
      isNewPatient: params.isNewPatient,
      patientDob: params.patientDob,
      insurance: params.insurance,
      groupId: params.groupId,
      memberId: params.memberId,
      insuranceAccepted: params.insuranceAccepted,
      providerId: params.providerId,
      productionTypeId: params.productionTypeId
    }),
    validate: (params) => {
      if (isNullValue(params.phoneNumber)) throw new Error("phoneNumber is required for 'book_child' action — use the confirmed Contact_Number");
      if (isNullValue(params.childFirstName)) throw new Error("childFirstName is required for 'book_child' action");
      if (isNullValue(params.childLastName)) throw new Error("childLastName is required for 'book_child' action");
      if (isNullValue(params.childDateOfBirth)) throw new Error("childDateOfBirth is required for 'book_child' action");
      if (isNullValue(params.appointmentDate)) throw new Error("appointmentDate is required for 'book_child' action");
      if (isNullValue(params.appointmentTime)) throw new Error("appointmentTime is required for 'book_child' action");
      if (isNullValue(params.operatoryId)) throw new Error("operatoryId is required for 'book_child' action");
      if (isNullValue(params.providerId)) throw new Error("providerId is required for 'book_child' action — must come from slots response");
    },
    successLog: () => "Child's appointment booked successfully"
  },

  cancel: {
    endpoint: `${BASE_URL}/cancelAppt`,
    method: 'POST',
    buildBody: (params) => ({
      appointmentId: params.appointmentId
    }),
    validate: (params) => {
      if (isNullValue(params.appointmentId)) throw new Error("appointmentId is required for 'cancel' action");
    },
    successLog: () => 'Appointment cancelled successfully'
  }
};

// ============================================================================
// UUI RESOLUTION (inline — extract to shared module when possible)
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
          console.log(`[chord_scheduling] List Management match: loc=${locationId}, env=${env}, provider=${match.provider_id}`);
          return {
            provider_id: String(match.provider_id).trim(),
            location_id: String(match.location_id).trim(),
          };
        }
      }
    } catch (lmErr) {
      console.warn(`[chord_scheduling] List Management error: ${lmErr.message}`);
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
  const toolName = 'chord_scheduling';
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
    numberOfPatients:  normalizeParam(safeGetVar(() => typeof $numberOfPatients !== 'undefined' ? $numberOfPatients : undefined)),
    timeWindowMinutes: safeGetVar(() => {
      if (typeof $timeWindowMinutes !== 'undefined' && !isNullValue($timeWindowMinutes)) return $timeWindowMinutes;
      return DEFAULT_VALUES.timeWindowMinutes;
    }),
    patientId:         normalizeParam(safeGetVar(() => typeof $patientId !== 'undefined' ? $patientId : undefined)),
    phoneNumber:       normalizeParam(safeGetVar(() => typeof $phoneNumber !== 'undefined' ? $phoneNumber : undefined)),
    appointmentDate:   normalizeParam(safeGetVar(() => typeof $appointmentDate !== 'undefined' ? $appointmentDate : undefined)),
    appointmentTime:   normalizeParam(safeGetVar(() => typeof $appointmentTime !== 'undefined' ? $appointmentTime : undefined)),
    operatoryId:       normalizeParam(safeGetVar(() => typeof $operatoryId !== 'undefined' ? $operatoryId : undefined)),
    appointmentId:     normalizeParam(safeGetVar(() => typeof $appointmentId !== 'undefined' ? $appointmentId : undefined)),
    isNewPatient:      normalizeParam(safeGetVar(() => typeof $isNewPatient !== 'undefined' ? $isNewPatient : undefined)),
    patientDob:        normalizeParam(safeGetVar(() => typeof $patientDob !== 'undefined' ? $patientDob : undefined)),
    searchStartDate:   normalizeParam(safeGetVar(() => typeof $searchStartDate !== 'undefined' ? $searchStartDate : undefined)),
    childFirstName:    normalizeParam(safeGetVar(() => typeof $childFirstName !== 'undefined' ? $childFirstName : undefined)),
    childLastName:     normalizeParam(safeGetVar(() => typeof $childLastName !== 'undefined' ? $childLastName : undefined)),
    childDateOfBirth:  normalizeParam(safeGetVar(() => typeof $childDateOfBirth !== 'undefined' ? $childDateOfBirth : undefined)),
    insurance:         normalizeParam(safeGetVar(() => typeof $insurance !== 'undefined' ? $insurance : undefined)),
    groupId:           normalizeParam(safeGetVar(() => typeof $groupId !== 'undefined' ? $groupId : undefined)),
    memberId:          normalizeParam(safeGetVar(() => typeof $memberId !== 'undefined' ? $memberId : undefined)),
    insuranceAccepted: normalizeParam(safeGetVar(() => typeof $insuranceAccepted !== 'undefined' ? $insuranceAccepted : undefined)),
    providerId:        normalizeParam(safeGetVar(() => typeof $providerId !== 'undefined' ? $providerId : undefined)),
    productionTypeId:  normalizeParam(safeGetVar(() => typeof $productionTypeId !== 'undefined' ? $productionTypeId : undefined)),
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

    const successMsg = typeof config.successLog === 'function' ? config.successLog(responseData) : config.successLog;
    console.log(`[${toolName}] ${successMsg}`);

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
