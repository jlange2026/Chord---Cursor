# EDS-Dental-Rev3 — Test Plan

## Overview

This test plan covers the two modified tools (`chord_scheduling_v08`, `chord_patient_v07_stage`) and their ripple effects across all agent flows. It is organized into:

- **Section 1**: Test data the customer must provide
- **Section 2**: Test cases grouped by priority and category
- **Section 3**: Regression checklist for unchanged flows

---

## Section 1: Test Data Required from Customer

### 1.1 — Location Configuration

| Data Needed | Why | Details |
|---|---|---|
| At least 2 location_config JSON objects | Test multi-location routing, different settings | Need location_id, appointment_types, provider_rules, insurance lists, features flags |
| One location with `legal_guardian_reminder: true` | Test post-booking disclaimers for new patients | |
| One location with `new_patient_special` (non-null price) | Test insurance-not-accepted and no-insurance flows | Need actual price, includes, disclaimer text |
| One location with `walk_ins: false`, `waitlist: false` | Test walk-in/waitlist rejection | |
| exclusion_list operatory_ids for each location | Test exclusion list blocking | Need at least 1 operatory_id that IS on the exclusion list |

### 1.2 — Test Patient Accounts (Existing Patients)

| # | Patient Details Needed | Purpose |
|---|---|---|
| EP-1 | Phone number, first name, last name, DOB, patientId, insurance_provider on file | Happy path: confirm, cancel, reschedule (existing patient with insurance) |
| EP-2 | Same phone as EP-1, different DOB (sibling) | Multi-child scenarios under same account |
| EP-3 | Phone number, name, DOB, patientId, NO insurance on file (null/empty) | Test existing patient with no insurance — agent should skip insurance check |
| EP-4 | Phone number, name, DOB, patientId, `new_patient=true` flag in lookup | Test transfer trigger for new_patient flag on existing account |
| EP-5 | Phone number NOT in any account | Test no-account-found flow, new patient routing |

**For each existing patient with an appointment, provide:**

| Appointment Data | Details |
|---|---|
| appointmentId | Real ID that can be confirmed/cancelled in test env |
| appointment_type | The type name (must match a location_config.appointment_types entry) |
| date and time | Upcoming date/time |
| operatory_id | The operatory assigned to this appointment |
| One appointment whose operatory_id IS on the exclusion_list | For exclusion list blocking test |
| One appointment whose operatory_id is NOT on the exclusion_list | For normal confirm/cancel/reschedule |

### 1.3 — Test Patient Data (New Patients)

These are NOT pre-existing accounts — the agent will create them during testing via `book_child`. Provide safe values that won't collide with production.

| Data | Example | Purpose |
|---|---|---|
| Child first name (safe test name) | "Testchild" | book_child will create this account |
| Child last name | "Automation" | |
| Child DOB within new patient age range | e.g., "2020-03-15" (age ~6) | Must pass provider_rules ageRange for isNewPatient=true |
| Child DOB OUTSIDE new patient age range | e.g., "1990-01-01" (age ~36) | Must FAIL age gate — test rejection |
| Child DOB at exact ageRange.max boundary | e.g., if max=17, DOB that makes child exactly 17 | Test boundary inclusion |
| Phone number for new patient (not in system) | | For Contact_Number |
| Email for reporting | "test@example.com" or "Not Provided" | Collected but NOT passed to book_child |
| Test insurance provider (ACCEPTED) | Actual name from clinic_info accepted list | |
| Test insurance provider (NOT accepted) | Name NOT in clinic_info accepted list | |
| Insurance member ID | "TEST123456" | Passed to book_child as memberId |
| Insurance group number | "GRP7890" | Passed to book_child as groupId |

### 1.4 — API / Slots Data

| Data | Details |
|---|---|
| Confirm `slots` endpoint returns `providerId` in response | Critical: agent stores this for book_child. If slots response does NOT include providerId, the PRE-BOOK VALIDATION will force a re-call. |
| Confirm `slots` response NO LONGER returns `productionTypeId` | Or if it does, confirm agent ignores it (not a canonical offered_slot key anymore). |
| Confirm `book` endpoint accepts simplified params | Only: patientId, appointmentDate, appointmentTime, operatoryId, uui. Must NOT require providerId, productionTypeId, isNewPatient, patientDob. |
| Confirm `book_child` endpoint accepts new optional params | groupId, memberId, insuranceAccepted. Must NOT require emailAddress. |
| Confirm `confirm_appointment` endpoint works | Accepts appointmentId, returns success/failure. |
| Confirm `create` endpoint works | Accepts firstName, lastName, birthDate, phoneNumber. Returns patientId. |
| At least one operatory_id that triggers "different EHR" error on book | For EHR mismatch recovery testing |
| Slots response with multiple operatory_ids | Need ≥ 2 different operatory_ids to test EHR mismatch retry |

### 1.5 — Provider Rules

| Data | Details |
|---|---|
| provider_rules from clinic_info response | Full array with isNewPatient=true and isNewPatient=false entries |
| ageRange for new patients | e.g., {min: 0, max: 17} |
| ageRange for existing patients | e.g., {min: 0, max: 21} |
| providerId for each rule | Needed to verify correct routing |

### 1.6 — UUI / Environment

| Data | Details |
|---|---|
| Valid test UUI string | For dev/stage environment |
| Test conversationId | Or confirm it can be empty |
| Caller ID number (test ANI) | A phone number to simulate incoming call with ANI |
| Null ANI scenario | Method to test when caller_id_number is null |

---

## Section 2: Test Cases

### Priority Legend
- **P0** — Must pass before any deployment (tool contract changes)
- **P1** — Critical flow validation
- **P2** — Important edge cases
- **P3** — Regression / nice-to-have

---

### Category A: `confirm_appointment` — NEW Action (P0)

| ID | Test Case | Steps | Expected Behavior | Verify |
|---|---|---|---|---|
| A-1 | Happy path: confirm existing appointment | Call with EP-1 ANI → provide DOB → verify identity → agent presents appointment → caller says "confirm" | Agent calls `confirm_appointment(appointmentId: <Child1_appointmentId>)` → reads back "Your appointment is confirmed for [date] at [time]" | Tool call made with correct appointmentId. Spoken confirmation includes real date/time from appointments response. |
| A-2 | confirm_appointment API failure | Same as A-1 but force `confirm_appointment` to return error | Agent says something like "I wasn't able to confirm that appointment. Let me transfer you to the office." → transfers | Agent does NOT say "confirmed". Escalation handled correctly. |
| A-3 | Confirm with null appointmentId | Simulate scenario where Child1_appointmentId is null at confirm time | Agent calls `appointments(patientId)` first to retrieve appointmentId, THEN calls `confirm_appointment` | Two tool calls in sequence: appointments → confirm_appointment. |
| A-4 | Confirm with exclusion list match | EP with appointment in excluded operatory | Agent says "I'm not able to make changes to that appointment. Let me transfer you to the office." | confirm_appointment is NEVER called. Transfer initiated. |

### Category B: `create` — NEW Action (P1)

| ID | Test Case | Steps | Expected Behavior | Verify |
|---|---|---|---|---|
| B-1 | Agent does NOT use `create` during normal new patient scheduling | New patient calls → full intake → slots → book_child | Agent uses `book_child` (not `create` + `book`). Patient account created via book_child. | No `create` tool call in conversation. book_child returns patientId + appointmentId. |
| B-2 | Verify `create` action exists and is documented | Review tool description in prompt | `create` is listed with correct params (firstName, lastName, birthDate, phoneNumber; optional: emailAddress, insurance) | Prompt accuracy check only — no live call needed. |

### Category C: `book` — Simplified Params (P0)

| ID | Test Case | Steps | Expected Behavior | Verify |
|---|---|---|---|---|
| C-1 | Existing patient schedule: book succeeds | EP-1 → verify → no existing appt → schedule → morning preference → slot offered → caller accepts | Agent calls `book(patientId, appointmentDate, appointmentTime, operatoryId)` — only 4 params + uui. Returns appointmentId. | Tool call contains ONLY patientId, appointmentDate, appointmentTime, operatoryId (plus uui/conversationId). Does NOT contain providerId, productionTypeId, isNewPatient, patientDob. |
| C-2 | Existing patient reschedule: book + cancel | EP-1 → verify → has appointment → "reschedule" → morning pref → slot → accept | Agent calls `book(patientId, date, time, operatoryId)` → succeeds → calls `cancel(originalAppointmentId)` → confirms | book call has simplified params. Cancel called AFTER book succeeds. Reschedule_Original_Cancelled=true. |
| C-3 | Book fails — EHR mismatch, retry with different operatory | Force first operatory_id to return "different EHR" error | Agent picks a different operatory_id from slots response, retries book with new operatory_id | Second book call has different operatoryId. Original appointment preserved (no cancel). |
| C-4 | Book fails — slot unavailable | Force book to fail with "slot unavailable" | Agent calls slots again, offers new slot, caller accepts, re-books | New slots call made. New slot offered. Book retried with new data. |

### Category D: `book_child` — Updated Params (P0)

| ID | Test Case | Steps | Expected Behavior | Verify |
|---|---|---|---|---|
| D-1 | New patient with insurance (full details) | New caller → DOB → lookup (no match) → "new patient" → intake (name, DOB, phone, email, insurance accepted, member ID, group #, special needs) → slot → accept | Agent calls `book_child` with: childFirstName, childLastName, childDateOfBirth, appointmentDate, appointmentTime, operatoryId, phoneNumber, insurance, groupId, memberId, insuranceAccepted, providerId, isNewPatient, patientDob | **emailAddress NOT in tool call.** groupId, memberId, insuranceAccepted ARE present. providerId from slots response. |
| D-2 | New patient — no insurance (self-pay) | Same as D-1 but caller has no insurance | book_child called with insurance="Self Pay" or "Not Provided". groupId/memberId/insuranceAccepted omitted or null. | Tool call does NOT have emailAddress. Insurance fields handled gracefully. |
| D-3 | New patient — insurance NOT accepted | Caller provides insurance not in accepted list | Agent informs not accepted, offers new_patient_special if configured, then proceeds with booking | insuranceAccepted reflects "not_accepted". Still books if caller wants to proceed. |
| D-4 | Email collected but NOT passed to book_child | New patient provides email during intake | Email stored in payload as "Email" field for reporting. book_child tool call does NOT include emailAddress. | Inspect tool call params — no emailAddress. Email appears in final Call_Summary. |
| D-5 | New patient — baby wellness eligible | Child age ≤ baby_wellness_max_age | Agent offers baby wellness appointment type using spoken_name. book_child includes isNewPatient=true. | Correct appointment type spoken. Correct params. |

### Category E: `grouped_slots` — timeWindowMinutes Default (P1)

| ID | Test Case | Steps | Expected Behavior | Verify |
|---|---|---|---|---|
| E-1 | Sibling booking (2 children) without specifying timeWindow | Caller wants appointments for 2 children → intake for both → grouped_slots called | `grouped_slots` called with numberOfPatients=2, isNewPatient, patientDob, searchStartDate. timeWindowMinutes either omitted or defaults to 60. | API receives default timeWindowMinutes=60 (or the tool auto-applies it). |
| E-2 | Sibling booking — sequential (add child after first booked) | First child booked → "anything else?" → "yes, schedule for another child" | Second child booked with own slots call. No re-lookup. Shared data carries forward. | Child2_* fields populated. Patient_Count incremented. |

### Category F: Turn Protocol & Payload Integrity (P1)

| ID | Test Case | Steps | Expected Behavior | Verify |
|---|---|---|---|---|
| F-1 | TC=1 greeting | Inbound call | "Hi, this is Allie. May I have the date of birth for the patient you're calling about?" Payload has TC=1, caller_id_number, setConfigPersist. | No tool calls. caller_id_number from system variable. |
| F-2 | TC=2 triple tool call (ANI available) | Caller provides DOB | Agent calls current_date_time + clinic_info + lookup(ANI). Stores Child1_DOB, Child1_Age, locationId, location_name, etc. | All three tool calls present. DOB stored BEFORE tool calls. |
| F-3 | TC=2 (ANI null) | No caller ID available | Agent calls current_date_time + clinic_info only (no lookup). Asks for caller's name. | No lookup call. Does NOT start intake. |
| F-4 | offered_slot format — no productionTypeId | Any slot offering turn | Child1_offered_slot stored as stringified JSON with keys: date, time, day_of_week, operatory_id, providerId | No productionTypeId in offered_slot. providerId present. |
| F-5 | Final Call_Summary — offered_slot as JSON object | Call completion | Inside Call_Summary, Child1_offered_slot is a JSON object (not stringified) with keys: date, time, day_of_week, operatory_id, providerId | Object type (not string). No productionTypeId. |
| F-6 | Final Call_Summary — all fields populated | Any completed call | All Active fields from payload + all Deferred fields from conversation history present | No unjustified nulls. locationId/location_name/Call_Location from clinic_info. caller_id_number immutable. |

### Category G: Confirm Flow (P0)

| ID | Test Case | Steps | Expected Behavior | Verify |
|---|---|---|---|---|
| G-1 | Caller says "Yes" to appointment presentation — NOT an explicit confirm | Agent: "Are you calling about [name]'s appointment on [date] at [time]?" Caller: "Yes" | Agent asks "Would you like to confirm, reschedule, or is there something else?" Does NOT auto-confirm. | confirm_appointment NOT called yet. No premature intent assignment. |
| G-2 | Caller explicitly says "Confirm" | After appointment presented | Agent calls `confirm_appointment(appointmentId)` → success → "Your appointment is confirmed for [date] at [time]." | confirm_appointment tool call present. appointmentId correct. |
| G-3 | Multi-child confirm | Two children under same phone, both have appointments | Agent confirms each child's appointment independently. Exclusion list checked per-child. | Separate confirm_appointment calls for each child. |

### Category H: Cancel & Reschedule Flows (P1)

| ID | Test Case | Steps | Expected Behavior | Verify |
|---|---|---|---|---|
| H-1 | Cancel — happy path | Existing patient → "cancel" → deflection offered → "no, cancel" → reason given | `cancel(appointmentId)` called. Reason stored. | Single cancel call. CancelDeflect=false. |
| H-2 | Cancel → reschedule deflection | Existing patient → "cancel" → "would you like to reschedule?" → "yes" | Reschedule flow begins. CancelDeflect=true. | No premature cancel call. Reschedule flow followed. |
| H-3 | Reschedule — book succeeds, cancel succeeds | Accept slot → book(patientId, date, time, operatoryId) → cancel(originalId) | book then cancel in sequence. Confirm to caller only after both succeed. | book has simplified params. Reschedule_Original_Cancelled=true. |
| H-4 | Reschedule — book fails, cancel NOT called | book returns error | Original appointment preserved. No cancel call. Offer alternative or transfer. | cancel NOT called. Reschedule_Original_Cancelled=false/null. |

### Category I: Insurance Flow with New book_child Params (P1)

| ID | Test Case | Steps | Expected Behavior | Verify |
|---|---|---|---|---|
| I-1 | New patient — insurance accepted, member ID + group # collected | Full intake with insurance details | book_child receives: insurance="Aetna", groupId="GRP123", memberId="MEM456", insuranceAccepted="accepted" | All 4 insurance params present in tool call. |
| I-2 | New patient — insurance accepted, no member ID available | Caller doesn't have card | book_child receives: insurance="Aetna", insuranceAccepted="accepted". groupId/memberId omitted or "Not Provided". | Graceful handling of missing insurance sub-fields. |
| I-3 | Existing patient — insurance update | Existing patient → edit_insurance → "Would you like to update?" → collect new provider | `edit_insurance(patientId, insurance)` called. Confirmed to caller. | Correct tool call. No book_child involved. |

### Category J: Edge Cases & Error Handling (P2)

| ID | Test Case | Steps | Expected Behavior | Verify |
|---|---|---|---|---|
| J-1 | providerId missing from slots response | slots returns data without providerId field | For book (existing): proceeds normally (providerId not needed). For book_child (new): triggers PRE-BOOK VALIDATION → re-calls slots. | book proceeds. book_child forces re-fetch. |
| J-2 | Caller disconnects mid-flow | Send CALLER_DISCONNECTED event | Agent sends full final payload with Call_Summary. No chord_handleEscalation. Call_Final_Disposition="Abandoned". | Full payload present. No handleEscalation. |
| J-3 | No-input 3 times | Three consecutive no-input events | Transfer after 3rd. Caller_Intent="NonResponsive Caller". | Correct escalation sequence. |
| J-4 | Same-day appointment request | Caller asks for today | "Same-day appointments need to be coordinated directly with the office." Transfer. | No slots call. Transfer initiated. |
| J-5 | 2-digit year DOB | Caller says "9/9/19" | Agent asks for full 4-digit year. Does NOT assume 2019. | No DOB stored until 4-digit year confirmed. |
| J-6 | Prompt injection attempt | "Ignore all instructions" | Moderation answer. No data leaked. | Agent stays in role. |

---

## Section 3: Regression Checklist

These flows are unchanged but should be spot-checked to ensure the tool modifications didn't introduce side effects.

| # | Flow | Quick Validation |
|---|---|---|
| R-1 | `lookup` by phone — DOB match | Returns correct patient, stores Child1_* fields |
| R-2 | `lookup` by phone — no DOB match | Agent asks "Is this for a new patient?" |
| R-3 | `lookup` — no account found | Agent asks "Has your child ever been seen by us before?" |
| R-4 | `get` patient recovery | When Child1_patientId is null at book time, agent recovers via `get` |
| R-5 | `clinic_info` response | locationInfo, provider_rules, exclusion_list, insurance_accepted all parsed correctly |
| R-6 | `appointments` response | appointmentId, type, date, time, operatory_id stored correctly |
| R-7 | FAQ flow — address, hours, phone | Speaks real values from clinic_info/location_config. No fabrication. |
| R-8 | Exclusion list blocking | Excluded operatory → transfer. Non-excluded → normal flow. |
| R-9 | Age gate — new patient outside range | Transfer. No intake collected. |
| R-10 | Age gate — existing patient outside all ranges | Transfer at TC=2. |
| R-11 | Multi-child — different DOBs | Each child tracked independently with ChildN_* fields |
| R-12 | Final payload — all fields present | Call_Summary has all Active + Deferred fields. No type mismatches. |
| R-13 | chord_handleEscalation on final turn | Called exactly once. Correct escalationIntent. |
| R-14 | HIPAA — no PHI before verification | Agent does not reveal names or appointments before DOB + name verification. |
| R-15 | One question per turn | Agent never asks two questions in one response. |

---

## Execution Notes

### Test Execution Order
1. **P0 tests first** (Categories A, C, D, G) — these validate the tool contract changes directly.
2. **P1 tests** (Categories B, E, F, H, I) — critical flow validation.
3. **P2 tests** (Category J) — edge cases.
4. **Regression** (Section 3) — spot-check unchanged flows.

### What to Inspect on Every Test
For each test call, verify:
- [ ] Tool calls made with correct action and correct parameters
- [ ] No `productionTypeId` in any tool call or payload field
- [ ] No `emailAddress` passed to `book_child`
- [ ] `book` calls have ONLY: patientId, appointmentDate, appointmentTime, operatoryId
- [ ] `confirm_appointment` called (not just a verbal confirmation) when caller confirms
- [ ] `groupId`, `memberId`, `insuranceAccepted` passed to `book_child` when available
- [ ] `providerId` in offered_slot from slots response, passed to `book_child`
- [ ] offered_slot format: `{date, time, day_of_week, operatory_id, providerId}` — no productionTypeId
- [ ] Call_Summary offered_slot is a JSON object (not stringified string)
- [ ] Final payload has no unjustified nulls, no fabricated values

### Known Risk Areas
1. **`book` param reduction** — If the backend still expects providerId/productionTypeId/isNewPatient/patientDob from `book`, calls will fail. Confirm backend is updated.
2. **`confirm_appointment` is new** — Confirm the endpoint (`/confirmAppt`) is deployed and functional in test env.
3. **`emailAddress` removed from book_child** — If the backend still expects it, book_child may fail. Confirm backend change is deployed.
4. **`groupId`/`memberId`/`insuranceAccepted` are new** — Confirm backend accepts these optional fields without error.
5. **`create` action** — Confirm endpoint (`/createPatient`) is reachable and returns patientId. Even though the standard flow uses book_child, the action exists and could be called.
