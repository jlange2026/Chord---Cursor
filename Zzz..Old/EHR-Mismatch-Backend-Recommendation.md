# Backend Recommendation: EHR Filtering for Slots API

**Date**: 2026-03-02
**Priority**: High
**Affects**: All scheduling flows (new patient, existing patient, reschedule)

## Problem

The `chord_scheduling(action: 'slots')` API returns operatories across **all EHR systems** configured at a location. When a patient is tied to a specific EHR, booking with an operatory from a different EHR fails with:

> "Cannot create an appointment where the patient belongs to a location from a different EHR."

The agent has no way to detect EHR incompatibility before attempting `book_child`, because:

1. `slots` does not filter by patient EHR affinity
2. `appointments` does not return the original appointment's operatory_id
3. `clinic_info` does not expose EHR-to-operatory mapping

## Current Workaround (Prompt-Level)

The prompt now includes EHR mismatch recovery logic: when `book_child` fails with a "different EHR" error, the agent retries with a different `operatory_id` from the same `slots` response. This works but is suboptimal — it wastes tool calls, adds latency, and may exhaust all operatories without finding a compatible one.

## Recommended Fix

Enhance the `slots` API to accept an optional `patientId` parameter. When provided, the API should filter returned operatories to only those compatible with the patient's EHR system. This eliminates the mismatch at the source.

### Proposed Change

**Endpoint**: `chord_scheduling(action: 'slots')`

**New optional parameter**:
- `patientId` (string) — When provided, only return operatories/slots compatible with this patient's EHR system.

### Expected Impact

- Eliminates EHR mismatch booking failures entirely for known patients
- Reduces unnecessary `book_child` retry calls
- Improves caller experience (no failed booking attempts or transfers)
- Still works without `patientId` for new patients (returns all operatories as today)
