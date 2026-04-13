# Tool Schema Changes — Summary of Modifications

## Environment Variables Required

Set these before deploying the updated tools:

| Variable | Description | Current Hardcoded Value |
|----------|-------------|------------------------|
| `NODERED_API_USER` | Node-RED Basic Auth username | `workflowapi2` |
| `NODERED_API_PASS` | Node-RED Basic Auth password | `workflowapi2` |
| `LIST_MGMT_TOKEN` | IntelePeer List Management API JWT | *(long JWT string)* |

> The tools fall back to the hardcoded values if env vars are not set, so deployment is non-breaking.

---

## chord_scheduling_v08 — Input Schema Changes

### New Parameters (add to Flowise schema)

| Property | Description | Type | Required |
|----------|-------------|------|----------|
| `productionTypeId` | Production type ID from slots response. Pass to `book` and `book_child` actions when available. | string | false |

### Changed Parameters

| Property | Old | New | Reason |
|----------|-----|-----|--------|
| `phoneNumber` | Optional for book_child | **Required for book_child** | Backend uses phoneNumber (not patientId) to resolve the parent account for child booking. Validation was previously commented out — now enforced. |
| `providerId` | Optional (validation commented out) | **Required for book_child** | Ensures correct provider routing per clinic_info provider_rules. Validation now enforced. |

### Full Updated Input Schema

| Property | Description | Type | Required |
|----------|-------------|------|----------|
| action | Operation: 'slots', 'grouped_slots', 'book', 'book_child', 'cancel' | string | **true** |
| numberOfPatients | Number of patients for grouped booking. Required for 'grouped_slots'. | number | false |
| timeWindowMinutes | Time window for grouped bookings (default 60). For 'grouped_slots'. | number | false |
| patientId | Patient ID. Required for 'book'. | string | false |
| phoneNumber | Parent phone number. **Required for 'book_child'.** | string | false |
| appointmentDate | Date YYYY-MM-DD. Required for 'book' and 'book_child'. | string | false |
| appointmentTime | Time. Required for 'book' and 'book_child'. | string | false |
| operatoryId | Operatory ID from slots. Required for 'book' and 'book_child'. | string | false |
| appointmentId | Appointment ID. Required for 'cancel'. | string | false |
| childFirstName | Child's first name. Required for 'book_child'. | string | false |
| childLastName | Child's last name. Required for 'book_child'. | string | false |
| childDateOfBirth | Child's DOB YYYY-MM-DD. Required for 'book_child'. | string | false |
| isNewPatient | New patient flag. Required for 'slots', 'grouped_slots', 'book', 'book_child'. | boolean | false |
| patientDob | Patient DOB YYYY-MM-DD. Required for 'slots', 'grouped_slots', 'book', 'book_child'. | string | false |
| searchStartDate | Search start YYYY-MM-DD. Required for 'slots', 'grouped_slots'. | string | false |
| insurance | Insurance provider name. Optional for 'book_child'. | string | false |
| groupId | Insurance group ID. Optional for 'book_child'. | string | false |
| memberId | Insurance member ID. Optional for 'book_child'. | string | false |
| insuranceAccepted | Whether insurance is accepted. Optional for 'book_child'. | string | false |
| providerId | Provider ID from slots response. **Required for 'book_child'.** | string | false |
| productionTypeId | **NEW.** Production type ID from slots response. Optional for 'book' and 'book_child'. | string | false |

---

## chord_patient_v07_stage — Input Schema Changes

### New Parameters (add to Flowise schema)

| Property | Description | Type | Required |
|----------|-------------|------|----------|
| `memberId` | Insurance member ID. Optional for 'edit_insurance' action. | string | false |
| `groupId` | Insurance group ID/number. Optional for 'edit_insurance' action. | string | false |

### Full Updated Input Schema

| Property | Description | Type | Required |
|----------|-------------|------|----------|
| action | Operation: 'lookup', 'get', 'create', 'appointments', 'clinic_info', 'edit_insurance', 'confirm_appointment' | string | **true** |
| phoneNumber | Patient phone number. Required for 'lookup' and 'create'. | string | false |
| patientId | Patient ID. Required for 'get', 'appointments', 'edit_insurance'. | string | false |
| firstName | Patient first name. Required for 'create'. | string | false |
| lastName | Patient last name. Required for 'create'. | string | false |
| birthDate | Patient DOB YYYY-MM-DD. Required for 'create'. | string | false |
| emailAddress | Patient email. Optional for 'create' (defaults to "Not Provided"). | string | false |
| insurance | Insurance provider name. Optional for 'create'. Required for 'edit_insurance'. | string | false |
| appointmentId | Appointment ID. Required for 'confirm_appointment'. | string | false |
| memberId | **NEW.** Insurance member ID. Optional for 'edit_insurance'. | string | false |
| groupId | **NEW.** Insurance group ID. Optional for 'edit_insurance'. | string | false |

---

## chord_handleEscalation — No Schema Changes

The input schema remains unchanged:

| Property | Description | Type | Required |
|----------|-------------|------|----------|
| firstName | Parent's first name | string | **true** |
| lastName | Parent's last name | string | **true** |
| DOB | Parent's date of birth | string | **true** |
| escalationIntent | Reason for escalation | string | **true** |

Only the JavaScript function was updated (credentials moved to env vars, reduced logging).

---

## Code-Level Changes Summary

### All Three Tools

| Change | Impact | Breaking? |
|--------|--------|-----------|
| Credentials use `process.env` with hardcoded fallback | Non-breaking — falls back to current values | No |
| Shared helper functions (isNullValue, normalizeParam, etc.) | Inlined for Flowise compatibility | No |

### chord_scheduling_v08

| Change | Impact | Breaking? |
|--------|--------|-----------|
| `phoneNumber` validation **uncommented** in `book_child` | Agent must now pass phoneNumber for book_child | **Yes — verify agent prompt sends phoneNumber** |
| `providerId` validation **uncommented** in `book_child` | Agent must pass providerId from slots response | **Yes — verify agent prompt passes providerId** |
| `productionTypeId` added to `book_child.buildBody` | Passes to backend if available; null if not | No |
| `productionTypeId` added to `book.buildBody` | Passes to backend if available; null if not | No |

### chord_patient_v07_stage

| Change | Impact | Breaking? |
|--------|--------|-----------|
| `memberId` added to `edit_insurance.buildBody` | Passes to backend if available | No |
| `groupId` added to `edit_insurance.buildBody` | Passes to backend if available | No |

### chord_handleEscalation

| Change | Impact | Breaking? |
|--------|--------|-----------|
| Reduced verbose logging (no raw variable dumps) | Cleaner logs | No |

---

## Backend Verification Needed

Before deploying, confirm with your Node-RED / backend team:

1. **Does `createChildAppt-dev` accept `productionTypeId`?** If yes, the new code passes it. If no, the backend will ignore the extra field (usually safe with Node-RED).

2. **Does `editPatientInsurance` accept `memberId` and `groupId`?** Same as above — confirm the backend handles these fields.

3. **Does `createChildAppt-dev` require `phoneNumber`?** The code already sends it (was in `buildBody` but validation was commented out). Uncommenting validation just ensures the agent always provides it.

---

## File Structure

```
tools/
├── chord_scheduling_v08.js       ← Updated (copy JS into Flowise tool)
├── chord_patient_v07_stage.js    ← Updated (copy JS into Flowise tool)
├── chord_handleEscalation.js     ← Updated (copy JS into Flowise tool)
├── shared/
│   ├── uui-resolver.js           ← Reference module (for future extraction)
│   ├── auth.js                   ← Reference module (for future extraction)
│   └── helpers.js                ← Reference module (for future extraction)
└── SCHEMA-CHANGES.md             ← This file
```

> **Note**: The `shared/` modules are reference implementations. Since Flowise tools run as self-contained scripts, the shared code is **inlined** in each tool file. When you move to a proper Node.js service, extract the shared code into importable modules.
