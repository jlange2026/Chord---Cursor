# Chord Specialty Dental - Multi-Location Architecture Playbook

## Overview

This document defines the multi-location architecture for Chord Specialty Dental's IVA system. The architecture uses **2 prompts** (Dental + Ortho) that serve **all locations** by reading location-specific configuration from an enhanced `clinic_info` tool response.

**Core Principle**: Prompts contain **flow logic** (how to greet, verify, schedule, etc.). Location-specific data (names, hours, insurance, appointment types, routing) comes from **`clinic_info` configuration** resolved per-call via the UUI variable.

---

## Architecture

```
DENTAL PROMPT (all pediatric dental locations: PDA, CDH Pedo, DFC, etc.)
├── chord_patient        (action-based: lookup, create, appointments, clinic_info, edit_insurance, confirm_appointment)
├── chord_scheduling     (action-based: slots, grouped_slots, book_child, cancel)
└── chord_handleEscalation (standalone)

ORTHO PROMPT (all orthodontic locations: CDH Ortho, SO, etc.)
├── chord_ortho_patient         (action-based: clinic_info, create, lookup, appointments, ...)
├── schedule_appointment_ortho  (action-based: grouped_slots, book_child, cancel)
└── chord_handleEscalation      (standalone, shared)
```

---

## Enhanced `clinic_info` Response Specification

### Dental `clinic_info` Response

When `chord_patient(action:'clinic_info')` is called, the Node-RED backend resolves the location from the UUI and returns:

```json
{
  "location_name": "PDA Allegheny",
  "locationId": "77522",
  "brand": "PDA",
  "specialty": "Pediatric Dental",
  "address": "2301 East Allegheny Ave., Ste 201, Philadelphia, PA 19134",
  "phone": "215-282-8000",
  "fax": "215-427-1782",
  "transfer_number": "+12159674288",
  "parking": "There is free parking across the street on Tulip Street.",
  "website_instructions": "You can find more information at pediatric dental associates dot com, then go to locations, and select Allegheny Avenue.",
  "greeting": "Hi, this is Allie with Pediatric Dental Associates of Allegheny Avenue. May I have the date of birth for the patient you're calling about?",
  "business_hours": "Mon 7:00 AM-7:00 PM|Tue 7:00 AM-4:30 PM|Wed 7:00 AM-4:30 PM|Thu 7:00 AM-3:00 PM|Fri 7:00 AM-2:30 PM",
  "scheduling_block_minutes": 15,
  "new_patient_column": "NEW",
  "hygiene_column": "HYG",
  "new_patient_provId": "AI NEW",
  "recall_provId": "AI RECLL",
  "appointment_types": [
    {
      "type": "Pedo New Patient Exam/Cleaning",
      "patient_status": "new",
      "min_age": 0,
      "max_age": 15,
      "duration_minutes": 30,
      "reason_code": "Initial - NP Child NoX"
    },
    {
      "type": "Pedo Existing Patient Cleaning",
      "patient_status": "existing",
      "min_age": 0,
      "max_age": 17,
      "duration_minutes": 30,
      "reason_code": "Initial - RC Child NoX"
    },
    {
      "type": "Baby Wellness",
      "patient_status": "new",
      "min_age": 0,
      "max_age": 5,
      "duration_minutes": 30,
      "reason_code": "Initial - NP Child NoX",
      "column": "OWM",
      "provId": "AINEW"
    }
  ],
  "baby_wellness_enabled": true,
  "baby_wellness_max_age": 5,
  "max_new_patient_age": 15,
  "max_existing_patient_age": 17,
  "special_needs_max_per_day": null,
  "owm_scheduling_notes": "Schedule in OWM column for new and hygiene appointments.",
  "new_patient_special_price": "$99",
  "routing": {
    "scheduling": "handle",
    "billing": "transfer",
    "surgery": "transfer",
    "sedation": "transfer",
    "frenectomy": "not_applicable",
    "operating_room": "not_applicable",
    "extension_requests": "not_applicable"
  },
  "routing_keywords": {
    "billing": ["bill", "billing", "payment", "insurance claim", "balance", "statement", "charge"],
    "surgery": ["surgery", "surgery center", "surgical", "referral"],
    "sedation": ["sedation", "sedated", "put to sleep", "sedation appointment"]
  },
  "insurance_in_network": [
    "Aetna PPO", "Aetna DMO", "Amerihealth Admin thru DenteMax", "Ameritas",
    "Blue Cross/Blue Shield thru DenteMax", "Carefirst thru DenteMax", "Cigna",
    "Cigna DHMO", "Companion Life thru DenteMax", "Coresource thru Aetna",
    "Coventry Dental thru DenteMax", "Delta Dental", "Denex thru Aetna",
    "Dominion Dental thru DenteMax", "EBS thru DenteMax", "Fidelio",
    "GEHA thru Cigna", "Guardian", "Humana Dental thru DenteMax",
    "IMG thru DenteMax", "Kidz Partners Chip (Avesis)", "LEHB",
    "Lincoln Financial thru DBP/United Healthcare", "Lincoln Dental Connection thru DenteMax",
    "Lineco thru DenteMax", "Meritain thru DenteMax", "Metlife",
    "Premera BC/CS thru DenteMax", "Principal Life Insurance",
    "Reliance thru Ameritas", "Security Life thru DenteMax",
    "Teamsters H&W", "UMR thru DenteMax", "United Concordia",
    "United Concordia Plus/DHMO", "United Concordia Chip",
    "United Healthcare PPO", "UPMC Dental Advantage PPO"
  ],
  "insurance_notes": "This is a PDA Philadelphia location. Insurance list specific to this office.",
  "medicaid_plans_accepted": [
    "PA Access", "AmeriHealth", "Geisinger", "Health Partners",
    "Keystone First", "United Healthcare", "UPMC"
  ],
  "medicaid_plans_not_accepted": ["Aetna Better Health MA", "Highmark Wholecare/Gateway"],
  "dmo_policies": [
    {
      "carrier": "Aetna DMO",
      "max_age_no_referral": 6,
      "referral_required_age": 7,
      "notes": "Patients 7+ need referral. Payment at DMO rate upfront, refund if insurance pays. Not accepted in Delaware.",
      "accepted_at_location": true
    },
    {
      "carrier": "Cigna DHMO",
      "max_age_no_referral": 12,
      "referral_required_age": 13,
      "notes": "Patients 12 and younger seen without referral. Cannot be scheduled with General Dentist.",
      "accepted_at_location": true
    },
    {
      "carrier": "United Concordia DHMO",
      "max_age_no_referral": 6,
      "referral_required_age": 7,
      "notes": "KHPE exception. DHMO must have referral for every appointment for age 7+.",
      "accepted_at_location": true
    }
  ],
  "reduced_fee_plans": [
    "Aetna Reduced Fee", "Aetna Vital Savings",
    "Optum/United Health Allied (use UHC private fee schedule)", "Dental Save"
  ],
  "out_of_network_carriers": [
    "AFLAC", "Anthem BC/BS", "Careington", "DeltaCare USA",
    "DentaQuest", "Horizon Blue Cross (PA Only)"
  ],
  "legal_guardian_reminder": "A parent or legal guardian must be present at the first appointment. If the legal guardian is not the parent, physical court documentation must be with them at the time of the visit. New Patient Paperwork will be sent to the email on file as well as SMS. If you do not complete this prior to the appointment, you must arrive 20 to 30 minutes early to complete it in office."
}
```

### Ortho `clinic_info` Response

When `chord_ortho_patient(action:'clinic_info')` is called:

```json
{
  "location_name": "CDH Ortho Allegheny",
  "locationGUID": "1fef9297-7c8b-426b-b0d1-f2275136e48b",
  "brand": "CDH",
  "specialty": "Orthodontics",
  "address": "2301 East Allegheny Ave., Ste 202, Philadelphia, PA 19134",
  "phone": "267-529-0990",
  "fax": "267-529-0990",
  "transfer_number": "+18445651519",
  "parking": "Park in the parking lot across the building that reads Commonwealth Campus",
  "website_instructions": "You can find more details online by visiting childrens dental health dot com, then go to locations and select Philadelphia dash Allegheny.",
  "greeting": "Hi, my name is Allie with Children's Dental Health Orthodontics Allegheny, how may I help you today?",
  "business_hours": "Every other Mon 8:30 AM-4:30 PM|Tue 8:30 AM-4:30 PM|Wed 8:30 AM-4:30 PM|Thu 8:30 AM-4:30 PM|Fri 8:30 AM-4:30 PM",
  "default_provider_guid": "0f588ace-e0bf-44ba-b8ef-be8cbb63153b",
  "default_schedule_column_guid": "07687884-7e37-49aa-8028-d43b751c9034",
  "default_appointment_type_guid": "f6c20c35-9abb-47c2-981a-342996016705",
  "appointment_duration_minutes": 40,
  "min_patient_age": 7,
  "appointment_types": [
    {
      "type": "Ortho New Patient Consultation",
      "patient_status": "new",
      "min_age": 7,
      "duration_minutes": 40,
      "exception": "Under 7 with dentist referral"
    },
    {
      "type": "Observation",
      "patient_status": "existing",
      "description": "Follow-up consultations for Medicaid and self-pay patients"
    }
  ],
  "handled_intents": ["schedule_new_consult"],
  "transfer_intents": ["cancel", "reschedule", "confirm", "existing_patient", "billing", "emergency"],
  "insurance_list": [
    "Aetna Better Health", "CHIP", "AmeriHealth Caritas", "Capital BC Chip",
    "Gateway", "Geisinger CHIP", "Geisinger MA", "Health Partners",
    "Keystone First", "Kidz Partners", "PA Medicaid",
    "Aetna DMO", "Capital Blue Cross", "Cigna", "Delta Dental",
    "DentaMax", "Fidelio", "Guardian", "LEHB", "MetLife", "Principal",
    "Sunlife", "Teamsters/Mattucci And Associates",
    "United Concordia - Tricare/DoD", "United Concordia - PFT",
    "United Concordia", "United Health Care", "UPMC Dental Advantage PPO"
  ],
  "medicaid_age_note": "PA Medicaid only covers orthodontic treatment until the patient turns 21.",
  "new_patient_definition": "A New Patient is defined as someone who has not been seen by any of our brands before. Even if a child has not been seen in several years, they are NOT considered a new patient.",
  "legal_guardian_reminder": "A parent or legal guardian must be present at the first appointment. If the legal guardian is not the parent, physical court documentation must be with them at the time of the visit. New Patient Paperwork will be sent to the email on file as well as SMS. If the paperwork is not completed prior to the appointment, you must arrive twenty to thirty minutes early to complete it in office."
}
```

---

## How to Add a New Location

### Step 1: Determine Specialty
- **Pediatric Dental** → Uses the Dental prompt + dental tools
- **Orthodontics** → Uses the Ortho prompt + ortho tools
- **Both** → Gets two phone numbers, one routing to each prompt

### Step 2: Configure Node-RED
Add a new location entry in the Node-RED location resolver. This maps the UUI (which contains location identifiers from the phone routing) to the `clinic_info` response for that location.

**Required data to collect from the new location:**

| Field | Example | Notes |
|-------|---------|-------|
| Location name | "PDA Cherry Hill" | Brand + location |
| Brand | "PDA" | PDA, CDH, DFC, SO |
| Address | "123 Main St..." | Full address |
| Phone | "856-555-1234" | Office phone |
| Fax | "856-555-1235" | Office fax |
| Transfer number | "+18565551234" | Where to route live agent transfers |
| Parking | "Free parking in front..." | Parking instructions |
| Website instructions | "Visit our website at..." | Spoken directions |
| Hours of operation | "Mon-Fri 8a-5p" | Per-day hours |
| Scheduling block size | 10 or 15 minutes | Varies by location |
| Appointment types | See list | Which types this location offers |
| Baby Wellness enabled? | Yes/No | If yes, max age |
| Baby Wellness max age | 4 or 5 | Location-specific threshold |
| Special needs max/day | null or 3 | DFC has 3 max |
| In-network insurance list | See list | Per state/brand, may vary by office |
| Medicaid plans accepted | See list | Varies by office cluster within state |
| Medicaid plans NOT accepted | See list | Varies by office cluster within state |
| DMO/DHMO policies | See list | Age/referral rules per carrier |
| Reduced fee plans | See list | Brand-level |
| Out-of-network carriers | See list | Brand-level |
| Copay notes | See text | NJ HMO $5 copay, etc. |
| Routing table | See structure | Which intents to handle vs. transfer |
| Greeting text | "Thank you for choosing..." | Location-specific greeting |
| Legal guardian reminder | Standard text | Usually shared across brand |

### Step 3: Assign Phone Number
- Forward the location's overflow number to IntelePeer
- Configure DNIS → UUI mapping so the UUI identifies the new location
- Node-RED resolves UUI → locationId → clinic_info config

### Step 4: Test
1. Call the forwarded number
2. Verify `clinic_info` returns the correct location data
3. Verify greeting uses the correct location name
4. Verify appointment types are correct for the location
5. Verify insurance list is correct
6. Verify transfer routing works (billing, surgery, etc.)
7. Test: schedule, confirm, cancel, reschedule flows
8. Test: FAQ responses (hours, address, parking, fax)

### Step 5: Go Live
No prompt changes needed. The new location is live as soon as:
- Phone routing is configured (DNIS → UUI)
- Node-RED has the location config entry
- Scheduling system (Dentrix/Cloud 9) has the location set up

---

## What Changes When Adding a Location

### Adding a DENTAL Location

| Component | Changes? | What to do |
|-----------|----------|------------|
| Dental Prompt | **NO** | Nothing - reads config from clinic_info |
| chord_patient tool | **NO** | Nothing - passes UUI, Node-RED resolves |
| chord_scheduling tool | **NO** | Nothing - passes UUI, Node-RED resolves |
| **Node-RED /chord/getLocation** | **YES** | Add location entry with all config fields |
| **Phone routing (DNIS/UUI)** | **YES** | Map new number to UUI for this location |
| **Dentrix** | **YES** | Location must exist in Dentrix |

### Adding an ORTHO Location

| Component | Changes? | What to do |
|-----------|----------|------------|
| Ortho Prompt | **NO** | Nothing - reads config from clinic_info |
| **chord_ortho_patient tool** | **YES** | Add entry to `LOCATION_CONFIGS` table in tool code |
| schedule_appointment_ortho tool | **NO** | LLM passes GUIDs from grouped_slots response |
| Node-RED ortho endpoints | **NO** | No changes needed |
| chord_handleEscalation | **NO** | Nothing - passes UUI |
| **Phone routing (DNIS/UUI)** | **YES** | Map new number to UUI (must contain the locationGUID) |
| **Cloud 9** | **YES** | Location must exist in Cloud 9 |

**Key difference**: Dental uses Node-RED for location config resolution. Ortho uses a `LOCATION_CONFIGS` table in the Flowise tool code. Both approaches result in the prompt reading all config from the `clinic_info` response.

---

## What Changes When Adding a New Specialty

If Chord adds a new specialty (e.g., Oral Surgery):

1. **New prompt** - Create a prompt for the new specialty's specific flow
2. **New tools** (if different API) - Create tools for the new backend system
3. **Reuse tools** (if same API) - Use existing dental or ortho tools
4. **Node-RED** - Add endpoints for the new specialty if needed
5. **Phone routing** - New numbers route to the new prompt

The existing Dental and Ortho prompts are NOT affected.

---

## Tool Enhancement Summary

### Dental: `chord_patient` - Enhanced `clinic_info` Action

**Current**: Returns `location_name`, `locationId`, `address`, `business_hours`

**Enhanced**: Returns the full Dental clinic_info response (see spec above)

**Node-RED change**: The `/chord/getLocation` endpoint needs to resolve the UUI and return the full config object instead of just basic location data.

**Tool code change**: None needed - the tool already passes UUI and returns whatever Node-RED sends back.

### Ortho: `chord_ortho_patient` v14 - LOCATION_CONFIGS Table

**Current**: Returns basic location data with hardcoded `DEFAULT_LOCATION_GUID` for CDH Allegheny

**Enhanced** (`chord_ortho_patient_v14_multiloc`): Contains a `LOCATION_CONFIGS` table that maps locationGUID → full config. The `clinic_info` action enriches its API response with the matching config. Hardcoded defaults are KEPT as CDH Allegheny fallbacks.

**No Node-RED change needed.** All config resolution happens in the Flowise tool code.

**To add a new ortho location**: Add an entry to `LOCATION_CONFIGS` in the tool code with all required fields (office info, GUIDs, insurance, greeting, etc.).

### Ortho: `schedule_appointment_ortho` - No Change

**No changes needed.** The `grouped_slots` response already returns per-slot GUIDs. The LLM passes these exact values when calling `book_child`. The hardcoded `DEFAULT_SCHEDULE_COLUMN_GUID` remains as a CDH Allegheny safety fallback.

---

## Location Config Examples

### PDA Allegheny (Pediatric Dental)
- Baby Wellness: YES (max age 5)
- OWM column: YES
- Scheduling blocks: 15-min
- New patient column: NEW
- Routing: billing→transfer, surgery→transfer, sedation→transfer

### PDA West Philly (Pediatric Dental)
- Baby Wellness: YES (max age 4)
- OWM column: NO (schedule in HYG regardless of age)
- Scheduling blocks: 15-min
- New patient column: HYG
- Routing: billing→transfer, operating_room→transfer, frenectomy→transfer, extension→transfer

### CDH Allegheny (Orthodontics)
- New consults only (all other intents transfer)
- Min age: 7 (unless dentist referral)
- Appointment duration: 40 min
- Uses Cloud 9 / GUIDs

### DFC (Pediatric Dental)
- Baby Wellness: NO (not mentioned in GG)
- OWM: Not mentioned
- Special needs max: 3 per day
- Scheduling blocks: 10-min (assumed standard)

### CDH Pediatric Dental Locations (e.g., Springfield)
- Baby Wellness: NO (OWM no longer used by CDH)
- Standard 30-min appointments
- Springfield: 45-min hygiene for certain conditions

---

## Insurance Configuration Complexity

Insurance acceptance varies at **three levels**: State/Brand, Office Cluster, and Carrier-Specific Rules. The `clinic_info` config MUST capture all three levels per location.

### Level 1: State/Brand Variations

| State/Brand | Key Differences |
|-------------|----------------|
| **CDH PA (Pedo)** | Largest carrier list (~50+). Accepts Aetna DMO, Cigna DHMO, Capital BC (select locations only). PA Medicaid plans vary by office cluster. |
| **CDH DE** | **No Aetna DMO, No Cigna DHMO.** DE State Medicaid only (no PA or NJ Medicaid/CHIP). Smaller carrier list. |
| **DFC NJ (Pedo)** | NJ-specific carriers: Horizon NJ Health, Horizon BC/BS NJ, Empire BC/BS, Liberty Dental (not Lodi), Amerigroup, WellCare. Guardian DHMO has complex age-by-plan rules. HMO C/D $5 copay for operative visits. |
| **PDA PA** | Subset of CDH PA carriers. Shares Medicaid plan rules with CDH Philadelphia cluster. |

### Level 2: Office Cluster Medicaid Variations (CDH PA)

Different CDH PA offices accept different Medicaid plans:

| Office Cluster | Medicaid Plans Accepted | NOT Accepted |
|----------------|------------------------|--------------|
| Philadelphia, Aston, Bensalem, Exton, Limerick, Plymouth Meeting, Warrington | PA Access, AmeriHealth, Geisinger, Health Partners, Keystone First, UHC, UPMC | ABH MA, Highmark Wholecare/Gateway |
| Downingtown, West Grove | PA Access, AmeriHealth, Geisinger, Health Partners, **Highmark Wholecare/Gateway**, Keystone First, UHC, UPMC | ABH MA |
| Springfield | PA Access, Geisinger, Health Partners, Keystone First, UHC, UPMC | ABH MA, **AmeriHealth**, **Highmark Wholecare/Gateway** |
| Bethlehem, Easton, Harrisburg, Lancaster, Mechanicsburg, Trexlertown, Wyomissing, York | PA Access, AmeriHealth, Geisinger, Health Partners, **Highmark Wholecare/Gateway**, UPMC | ABH MA, **UHC**, **Keystone First** |

**Capital BC and Dominion Dental** (non-DenteMax) only at: Lancaster, Harrisburg, Mechanicsburg, York, Reading.

### Level 3: DMO/DHMO Carrier-Specific Rules

| Carrier | Rule | Applies To |
|---------|------|------------|
| **Aetna DMO** | Ages 6 and under: no referral needed. Ages 7+: referral required, pay DMO rate upfront, refund if insurance pays. Emergency for 7+: Aetna must give auth V# first. | All PA & NJ locations. **NOT accepted in Delaware.** |
| **Cigna DHMO** | Ages 12 and under: no referral needed. Cannot be scheduled with General Dentist (only credentialed pedo). | All locations where accepted. **NOT accepted in Delaware.** |
| **United Concordia DHMO** | Ages 7+: referral required for every appointment. KHPE exception. | CDH PA, PDA. |
| **Guardian DHMO (NJ/DFC)** | N series plans: under age 9 (8 and under). U series plans: under age 8 (7 and under). All other plans: under age 6 (5 and under). Referral required. | DFC NJ only. |
| **Horizon Dental Choice (NJ)** | Plans A,B,C,D,E,G,H,K,S: Horizon referral required. Total Care Plan F,J with Eastern Dental home office: Eastern Dental referral, claim to Eastern. | DFC NJ only. |
| **Liberty Dental Plans (NJ)** | Accepted at all NJ DFC locations **EXCEPT Lodi**. | DFC NJ (not Lodi). |

### Level 4: Reduced Fee / Discount Plans (Not Insurance)

These are NOT insurance — patients pay 100% at time of service at reduced rates:
- Aetna Reduced Fee / Aetna Vital Savings
- Optum/United Health Allied (use UHC private fee schedule)
- Dental Save (CDH PA only)

### Enhanced `clinic_info` Insurance Structure

To handle all this complexity, each location's `clinic_info` response should include:

```json
{
  "insurance_in_network": ["Aetna PPO", "Cigna", "Delta Dental", "..."],
  "insurance_notes": "CDH Springfield PA location. Capital BC and Dominion not accepted here (only Lancaster, Harrisburg, Mechanicsburg, York, Reading).",
  "medicaid_plans_accepted": ["PA Access", "Geisinger", "Health Partners", "Keystone First", "UHC", "UPMC"],
  "medicaid_plans_not_accepted": ["ABH MA", "AmeriHealth", "Highmark Wholecare/Gateway"],
  "dmo_policies": [
    {
      "carrier": "Aetna DMO",
      "accepted_at_location": true,
      "max_age_no_referral": 6,
      "referral_required_age": 7,
      "notes": "Pay DMO rate upfront if 7+. Emergency 7+: need Aetna auth V#."
    },
    {
      "carrier": "Cigna DHMO",
      "accepted_at_location": true,
      "max_age_no_referral": 12,
      "referral_required_age": 13,
      "notes": "Cannot schedule with General Dentist."
    }
  ],
  "reduced_fee_plans": ["Aetna Reduced Fee", "Aetna Vital Savings", "Optum/UH Allied"],
  "out_of_network_carriers": ["AFLAC", "Anthem BC/BS", "DeltaCare USA", "DentaQuest", "..."],
  "insurance_copay_notes": null
}
```

For NJ DFC, the config would include NJ-specific fields:
```json
{
  "insurance_copay_notes": "HMO C/D plans (Liberty, Horizon NJ Health, UHC Community Plan) have a $5.00 copay at operative/work appointments, collected at time of service. Not due for preventative.",
  "carrier_location_exceptions": [
    {"carrier": "Liberty Dental Plans", "exception": "Not accepted at Lodi location"}
  ]
}
```

### How the Prompt Uses Insurance Config

The prompt does NOT need to know the rules per state/brand. It simply:

1. **Caller says insurance name** → Agent silently checks `insurance_in_network` array
2. **If found** → "That's in our network. Please bring your card."
3. **If not found** → Check `medicaid_plans_accepted` and `medicaid_plans_not_accepted`
4. **If DMO/DHMO** → Check `dmo_policies` for age/referral rules, inform caller appropriately
5. **If not found anywhere** → "Unfortunately that's not in our network." Offer self-pay price.
6. **If reduced fee plan** → "That's a discount plan, not insurance. You'd pay [rate] at time of service."

All the complexity is in the CONFIG, not the PROMPT. Adding a new state (e.g., Maryland) or brand just means adding the correct insurance arrays to that location's config entry.
