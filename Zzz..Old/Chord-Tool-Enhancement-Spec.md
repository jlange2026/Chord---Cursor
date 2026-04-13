# Chord Tool Enhancement Specification

## Overview

### Dental Tools (chord_patient, chord_scheduling)
**No tool code changes needed.** Dental tools already pass UUI to Node-RED, which resolves the location and returns location-specific data. To support new dental locations, enhance the Node-RED `/chord/getLocation` response to return richer config data (appointment types, insurance, routing, etc.). The Flowise tool code is untouched.

### Ortho Tools (chord_ortho_patient, schedule_appointment_ortho)
**Ortho does NOT use Node-RED for location resolution.** The approach is different:
- `chord_ortho_patient` gets a **LOCATION_CONFIGS table** in its code that maps UUI → full location config
- The `clinic_info` action enriches its response with this config so the prompt has everything it needs
- `schedule_appointment_ortho` is **unchanged** — the LLM passes GUIDs from the `clinic_info` response, and the existing hardcoded defaults serve as CDH Allegheny fallbacks
- **To add a new ortho location**: Add an entry to `LOCATION_CONFIGS` in the ortho patient tool

### Shared Tool (chord_handleEscalation)
**No changes needed.** Already location-agnostic.

---

## Dental Tool Changes

### chord_patient (chord_patient_v06_dev)

**Code changes needed: NONE**

The tool already:
- Passes `uui` to all endpoints including `clinic_info`
- Returns whatever JSON Node-RED sends back
- Has no hardcoded location data (locationId comes from response)

**Node-RED change**: The `/chord/getLocation` endpoint needs to return the enhanced config object (see Playbook for full spec). Currently returns basic fields; needs to add: `brand`, `appointment_types`, `baby_wellness_enabled`, `baby_wellness_max_age`, `max_new_patient_age`, `max_existing_patient_age`, `routing`, `routing_keywords`, `insurance_in_network`, `medicaid_plans_accepted`, `medicaid_plans_not_accepted`, `dmo_policies`, `fax`, `transfer_number`, `parking`, `website_instructions`, `greeting`, `new_patient_special_price`, `legal_guardian_reminder`, `special_needs_max_per_day`.

### chord_scheduling (chord_scheduling_v07_dev)

**Code changes needed: NONE**

Already fully location-agnostic. Passes UUI to all endpoints.

---

## Ortho Tool Changes

### chord_ortho_patient → v14 (`chord_ortho_patient_v14_multiloc-CustomTool.json`)

**Code changes: SMALL — add LOCATION_CONFIGS table, enrich clinic_info response**

The existing DEFAULT_LOCATION_GUID and DEFAULT_PROVIDER_GUID are **kept** as CDH Allegheny fallbacks. No existing behavior is broken.

**What's added:**

1. A `LOCATION_CONFIGS` object that maps locationGUID → full config (office info, GUIDs, insurance, age rules, greeting, etc.)
2. A `resolveLocationConfig(uui)` function that checks the UUI for a known locationGUID
3. In the `clinic_info` action handler: after getting the API response, merge the location config into the response

**How it works:**
```
LLM calls clinic_info
  → Tool sends request to getLocation API (same as before)
  → Tool receives basic location data from API
  → Tool looks up LOCATION_CONFIGS using UUI
  → Tool merges config into response (GUIDs, insurance, hours, greeting, etc.)
  → LLM receives enriched response with everything the prompt needs
```

**To add a new ortho location:** Add an entry to `LOCATION_CONFIGS`:
```javascript
'new-guid-here': {
    location_name: 'SO Springfield',
    locationGUID: 'new-guid-here',
    brand: 'SO',
    specialty: 'Orthodontics',
    address: '...',
    phone: '...',
    default_provider_guid: '...',
    default_schedule_column_guid: '...',
    // ... all other config fields
}
```

### schedule_appointment_ortho

**Code changes needed: NONE**

The scheduling tool stays as-is because:
- `grouped_slots` already returns `scheduleViewGUID` and `scheduleColumnGUID` per slot
- The LLM passes these exact values from the response when calling `book_child`
- The hardcoded `DEFAULT_SCHEDULE_COLUMN_GUID` only fires as a safety fallback if the LLM omits it
- For CDH Allegheny, the fallback is correct; for other locations, the LLM will always pass the value from `grouped_slots`

---

## chord_handleEscalation

**Code changes needed: NONE**

Already location-agnostic.

---

## Summary of Changes

| Component | Change Type | Effort | Description |
|-----------|------------|--------|-------------|
| **chord_patient** (Dental) | None | None | Node-RED handles everything |
| **chord_scheduling** (Dental) | None | None | Already location-agnostic |
| **chord_ortho_patient** (Ortho) | Add LOCATION_CONFIGS | Small | Config table + enrich clinic_info response |
| **schedule_appointment_ortho** (Ortho) | None | None | LLM passes GUIDs from grouped_slots |
| **chord_handleEscalation** | None | None | Already location-agnostic |
| **Node-RED /chord/getLocation** (Dental) | Enhanced response | Medium | Return full dental config per location |
| **Node-RED ortho endpoints** | None | None | No changes needed |

---

## Testing Checklist

### Per Location
- [ ] `clinic_info` returns correct location name, address, hours
- [ ] `clinic_info` returns correct appointment types for the location
- [ ] `clinic_info` returns correct insurance list for the location
- [ ] `clinic_info` returns correct GUIDs (ortho: from LOCATION_CONFIGS)
- [ ] Greeting uses correct location name
- [ ] Insurance verification uses correct list
- [ ] FAQ responses use correct location data
- [ ] Booking succeeds with correct location identifiers

### Cross-Location
- [ ] Two calls to different locations simultaneously return correct configs
- [ ] UUI correctly identifies each location
- [ ] No cross-contamination between location configs
