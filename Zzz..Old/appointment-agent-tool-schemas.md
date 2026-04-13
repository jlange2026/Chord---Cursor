# Patient Appointment Agent — Tool Schemas

These schemas define the 4 tools available to the agent. They are registered as tool definitions in your platform's tool/function-calling configuration — NOT embedded in the system prompt.

---

## Tool 1: `patient`

Manages patient identification and registration.

### Schema

```json
{
  "name": "patient",
  "description": "Look up, search, or register patients. Use phone_lookup at call start, search when phone doesn't match, create for new patients.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["phone_lookup", "search", "create"],
        "description": "The operation to perform."
      },
      "phone_number": {
        "type": "string",
        "description": "Patient phone in E.164 format. Required for phone_lookup and create."
      },
      "first_name": {
        "type": "string",
        "description": "Patient first name. Required for search and create."
      },
      "last_name": {
        "type": "string",
        "description": "Patient last name. Required for search and create."
      },
      "date_of_birth": {
        "type": "string",
        "description": "YYYY-MM-DD format. Required for search and create."
      },
      "email": {
        "type": "string",
        "description": "Patient email. Optional, for create only."
      },
      "insurance_provider": {
        "type": "string",
        "description": "Insurance company name. Optional, for create only."
      },
      "site_id": {
        "type": "string",
        "description": "Site identifier. Always required."
      }
    },
    "required": ["action", "site_id"]
  }
}
```

### Return Schemas

**phone_lookup / search — found:**
```json
{
  "found": true,
  "patient_id": "PAT-12345",
  "first_name": "Sarah",
  "last_name": "Connor",
  "dob": "1982-07-15",
  "phone": "+15551234567",
  "status": "active"
}
```

**phone_lookup / search — not found:**
```json
{
  "found": false
}
```

**create:**
```json
{
  "patient_id": "PAT-67890",
  "status": "created"
}
```

---

## Tool 2: `appointment`

Manages all appointment operations: availability search, booking, retrieval, rescheduling, cancellation, and confirmation.

### Schema

```json
{
  "name": "appointment",
  "description": "Manage appointments. Actions: get_available_slots (search openings), book (create appointment), get_existing (retrieve patient appointments), reschedule, cancel, confirm.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["get_available_slots", "book", "get_existing", "reschedule", "cancel", "confirm"],
        "description": "The operation to perform."
      },
      "site_id": {
        "type": "string",
        "description": "Site identifier. Required for get_available_slots, book, get_existing."
      },
      "patient_id": {
        "type": "string",
        "description": "Patient identifier. Required for book, get_existing."
      },
      "appointment_id": {
        "type": "string",
        "description": "Appointment identifier. Required for reschedule, cancel, confirm."
      },
      "appointment_type": {
        "type": "string",
        "description": "Type of appointment. Required for get_available_slots, book."
      },
      "provider_id": {
        "type": "string",
        "description": "Provider identifier. Optional for get_available_slots. Required for book."
      },
      "preferred_date": {
        "type": "string",
        "description": "YYYY-MM-DD. Optional hint for get_available_slots."
      },
      "date_range_start": {
        "type": "string",
        "description": "YYYY-MM-DD. Required for get_available_slots."
      },
      "date_range_end": {
        "type": "string",
        "description": "YYYY-MM-DD. Required for get_available_slots."
      },
      "date": {
        "type": "string",
        "description": "YYYY-MM-DD. Required for book."
      },
      "time": {
        "type": "string",
        "description": "HH:MM 24-hour format. Required for book."
      },
      "reason_for_visit": {
        "type": "string",
        "description": "Brief visit reason. Required for book."
      },
      "new_date": {
        "type": "string",
        "description": "YYYY-MM-DD. Required for reschedule."
      },
      "new_time": {
        "type": "string",
        "description": "HH:MM 24-hour format. Required for reschedule."
      },
      "new_provider_id": {
        "type": "string",
        "description": "New provider. Optional for reschedule."
      },
      "cancellation_reason": {
        "type": "string",
        "description": "Reason for cancellation. Optional for cancel."
      },
      "status_filter": {
        "type": "string",
        "enum": ["upcoming", "past", "all"],
        "description": "Filter for get_existing. Defaults to upcoming."
      }
    },
    "required": ["action"]
  }
}
```

### Return Schemas

**get_available_slots:**
```json
{
  "slots": [
    {
      "date": "2026-03-10",
      "time": "09:00",
      "provider_id": "PROV-001",
      "provider_name": "Dr. Smith",
      "duration_minutes": 30
    }
  ]
}
```

**book:**
```json
{
  "appointment_id": "APT-11111",
  "date": "2026-03-10",
  "time": "09:00",
  "provider_name": "Dr. Smith",
  "appointment_type": "Annual Physical",
  "status": "booked"
}
```

**get_existing:**
```json
{
  "appointments": [
    {
      "appointment_id": "APT-22222",
      "date": "2026-03-12",
      "time": "10:00",
      "provider_name": "Dr. Garcia",
      "appointment_type": "Follow-Up",
      "status": "scheduled"
    }
  ]
}
```

**reschedule:**
```json
{
  "appointment_id": "APT-22222",
  "date": "2026-03-15",
  "time": "14:00",
  "provider_name": "Dr. Garcia",
  "status": "rescheduled"
}
```

**cancel:**
```json
{
  "appointment_id": "APT-22222",
  "status": "cancelled"
}
```

**confirm:**
```json
{
  "appointment_id": "APT-22222",
  "status": "confirmed"
}
```

---

## Tool 3: `site`

Retrieves site-specific configuration and FAQ data from list management.

### Schema

```json
{
  "name": "site",
  "description": "Retrieve site configuration and FAQ data from list management using the dialed number. Called automatically at call start.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["get_info"],
        "description": "The operation to perform."
      },
      "dnis": {
        "type": "string",
        "description": "The dialed number (DNIS) in E.164 format."
      }
    },
    "required": ["action", "dnis"]
  }
}
```

### Return Schema

```json
{
  "siteId": "SITE-001",
  "siteName": "Springfield Family Practice",
  "siteAddress": "123 Main St, Springfield, IL 62701",
  "sitePhone": "+12175551234",
  "siteTimezone": "America/Chicago",
  "hoursMonFri": "8:00 AM - 5:00 PM",
  "hoursSat": "9:00 AM - 12:00 PM",
  "hoursSun": "Closed",
  "providers": "Dr. Smith, Dr. Johnson, NP Williams",
  "appointmentTypes": "Annual Physical, Sick Visit, Follow-Up, New Patient Visit, Wellness Check",
  "insuranceAccepted": "Blue Cross, Aetna, UnitedHealthcare, Medicare, Medicaid",
  "cancellationPolicy": "Please cancel at least 24 hours in advance to avoid a $25 fee.",
  "newPatientAccepting": true,
  "specialInstructions": "New patients must arrive 15 minutes early with photo ID and insurance card.",
  "maxScheduleDaysOut": 90,
  "transferNumber": "+12175559999",
  "faq_parking": "Free parking is available in the lot behind the building.",
  "faq_telehealth": "Yes, we offer telehealth appointments for follow-ups and non-emergency visits.",
  "faq_lab_results": "Lab results are typically available within 3-5 business days via the patient portal.",
  "faq_prescription_refills": "Please request refills through the patient portal or call during business hours.",
  "faq_new_patient_docs": "New patients should bring photo ID, insurance card, and a list of current medications.",
  "faq_after_hours": "For after-hours emergencies, please call 911 or visit the nearest emergency room.",
  "faq_forms": "Patient forms are available on our website or at the front desk upon arrival."
}
```

---

## Tool 4: `transfer`

Transfers the live call to a human agent at the practice.

### Schema

```json
{
  "name": "transfer",
  "description": "Transfer the call to a live agent. Use when the caller requests a person, the request is out of scope, or after 2+ failed attempts. Trigger silently — do not send a spoken response when transferring.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["transfer_call"],
        "description": "The operation to perform."
      },
      "transfer_number": {
        "type": "string",
        "description": "The phone number to transfer to."
      },
      "reason": {
        "type": "string",
        "description": "Brief reason for the transfer (logged, not spoken to caller)."
      },
      "site_id": {
        "type": "string",
        "description": "Site identifier."
      },
      "patient_id": {
        "type": "string",
        "description": "Patient ID if verified. Optional."
      }
    },
    "required": ["action", "transfer_number", "reason", "site_id"]
  }
}
```

### Return Schema

```json
{
  "status": "transferring"
}
```

---

## Variable Reference

### System Variables (Auto-Populated by Platform)

| Variable | Source | Description |
|---|---|---|
| `{{callerId}}` | SIP/Telephony | Incoming caller's phone number |
| `{{dnis}}` | SIP/Telephony | Number the caller dialed |
| `{{agentName}}` | Configuration | Virtual assistant display name |

### Site Variables (From List Management — populated at call start)

| Variable | Description |
|---|---|
| `{{siteId}}` | Unique site identifier |
| `{{siteName}}` | Practice/location name |
| `{{siteAddress}}` | Full street address |
| `{{sitePhone}}` | Main phone number |
| `{{siteTimezone}}` | IANA timezone (e.g., America/Chicago) |
| `{{hoursMonFri}}` | Weekday operating hours |
| `{{hoursSat}}` | Saturday hours |
| `{{hoursSun}}` | Sunday hours |
| `{{providers}}` | Comma-separated provider names |
| `{{appointmentTypes}}` | Comma-separated appointment types |
| `{{insuranceAccepted}}` | Comma-separated insurance providers |
| `{{cancellationPolicy}}` | Cancellation policy text |
| `{{newPatientAccepting}}` | true/false — accepting new patients |
| `{{specialInstructions}}` | First-visit instructions |
| `{{maxScheduleDaysOut}}` | Maximum days out for scheduling |
| `{{transferNumber}}` | Transfer destination number |
| `{{faq_*}}` | Site-specific FAQ answers (parking, telehealth, lab results, etc.) |

### Session Variables (Set During Call Flow)

| Variable | Set By | Description |
|---|---|---|
| `{{patientId}}` | `patient` tool | Identified patient ID |
| `{{patientFirstName}}` | `patient` tool | Patient first name |
| `{{patientLastName}}` | `patient` tool | Patient last name |
| `{{patientDOB}}` | `patient` tool | Patient date of birth |
| `{{isVerified}}` | Verification step | Identity confirmed (true/false) |
| `{{appointmentId}}` | `appointment` tool | Current appointment ID |
| `{{appointmentDate}}` | `appointment` tool | Appointment date |
| `{{appointmentTime}}` | `appointment` tool | Appointment time |
| `{{appointmentType}}` | Caller / tool | Appointment type |
| `{{providerName}}` | `appointment` tool | Provider name |
| `{{providerId}}` | `appointment` tool | Provider ID |
| `{{reasonForVisit}}` | Caller | Visit reason |
