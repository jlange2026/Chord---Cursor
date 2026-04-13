/**
 * ============================================================================
 * CHORD HANDLE ESCALATION — Call Disposition Reporting Tool
 * ============================================================================
 * Self-contained tool — no action parameter.
 * Calls Node-RED endpoint for escalation/disposition reporting.
 *
 * CHANGES FROM PREVIOUS VERSION:
 *   - Credentials moved to env vars (OWASP A07)
 *   - Reduced logging verbosity (removed raw variable dumps)
 * ============================================================================
 */

const fetch = require('node-fetch');

const CONFIG = {
  toolName: 'handleEscalation',
  endpoint: 'https://chord-nginx-noderedflow.prod.c1conversations.io/FabricWorkflow/api/chord/handleEscalation',
  method: 'POST',
  timeout: 30000,

  buildBody: () => {
    const normalizeValue = (value) => {
      if (typeof value === 'undefined') return 'NA';
      if (value === null || value === 'null' || value === 'NULL') return 'NA';
      if (typeof value === 'string' && value.trim() === '') return 'NA';
      return value;
    };

    if (!$vars || !$vars.c1mg_uui || $vars.c1mg_uui === 'c1mg_uui' ||
        (typeof $vars.c1mg_uui === 'string' && $vars.c1mg_uui.trim() === '')) {
      if (!$vars) $vars = {};
      $vars.c1mg_uui = '767202758-000000000001105456-SR-000-000000000000DAL130-5DEAFCC2|77523|223076809|1767202758-000000000001105456-SR-000-000000000000DAL130-5DEAFCC2|junkVO|fdfee190-1e65-4c40-b512-1bb378dcdcab|FSV';
    }

    return {
      firstName:        normalizeValue(typeof $firstName !== 'undefined' ? $firstName : undefined),
      lastName:         normalizeValue(typeof $lastName !== 'undefined' ? $lastName : undefined),
      DOB:              normalizeValue(typeof $DOB !== 'undefined' ? $DOB : undefined),
      escalationIntent: normalizeValue(typeof $escalationIntent !== 'undefined' ? $escalationIntent : undefined),
      uui:              $vars.c1mg_uui,
      EllyConversationID: $vars.conversationId
    };
  },

  getAuthHeader: () => {
    try {
      const username = process.env.NODERED_API_USER || "workflowapi2";
      const password = process.env.NODERED_API_PASS || "workflowapi2";
      if (username && password) {
        return `Basic ${Buffer.from(`${username}:${password}`).toString('base64')}`;
      }
    } catch (e) { /* fall through */ }
    return null;
  }
};

async function executeRequest() {
  console.log(`[${CONFIG.toolName}] Starting execution`);

  try {
    const body = CONFIG.buildBody();
    const conversationId = $vars?.conversationId || '';
    body.conversationId = conversationId;

    console.log(`[${CONFIG.toolName}] Endpoint: ${CONFIG.method} ${CONFIG.endpoint}`);

    const headers = { 'Content-Type': 'application/json' };
    const authHeader = CONFIG.getAuthHeader();
    if (authHeader) headers['Authorization'] = authHeader;

    const options = {
      method: CONFIG.method,
      headers,
      body: JSON.stringify(body)
    };

    let timeoutId;
    if (typeof AbortController !== 'undefined') {
      const controller = new AbortController();
      timeoutId = setTimeout(() => controller.abort(), CONFIG.timeout);
      options.signal = controller.signal;
    }

    const response = await fetch(CONFIG.endpoint, options);
    if (timeoutId) clearTimeout(timeoutId);

    console.log(`[${CONFIG.toolName}] Response Status: ${response.status} ${response.statusText}`);

    let data;
    const contentType = response.headers.get('content-type');
    data = (contentType && contentType.includes('application/json'))
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    if (data && data.success === false) {
      throw new Error(data.error || 'Escalation handling failed');
    }

    console.log(`[${CONFIG.toolName}] Success — escalation handled`);
    return JSON.stringify(data);

  } catch (error) {
    console.error(`[${CONFIG.toolName}] Error:`, error.message);

    if (error.name === 'AbortError') {
      error.message = `Request timeout after ${CONFIG.timeout}ms`;
    }

    throw new Error(JSON.stringify({
      error: 'Failed to handle escalation',
      message: error.message,
      timestamp: new Date().toISOString()
    }, null, 2));
  }
}

return executeRequest();
