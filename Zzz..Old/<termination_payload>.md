<termination_payload>
FIRST make the tool call: chord_handleEscalation(firstName, lastName, DOB, "Completed - [summary]")
THEN after tool response, send:

ANSWER: You're all set, [name]. Have a great day!
PAYLOAD:
{{
"telephonyDisconnectCall": {{}},
"Call_Summary": {{
"location_name": "<name>",
"locationId": "<id>",
"locationSpecialty": "<Dental>",
"Caller_Identified": "<True | False>",
"guarantor_name": "<parent/caller's Full Name or null>",
"guarantor_FirstName": "<parent/caller's First Name or null>",
"guarantor_LastName": "<parent/caller's Last Name or null>",
"guarantor_DOB": "<parent/caller's date of birth in YYYY-MM-DD or null>",
"Contact_Number": "<confirmed phone number or null>",
"ANI": "<caller ID number - the number caller came in on or null>",
"AltANI": "<alternate phone number provided by caller or null>",
"ANIIsMatch": "<1 if account found by ANI, 0 if not, null before lookup>",
"AltANIIsMatch": "<1 if account found by alternate number, 0 if not, null if no alternate number>",
"PatientFound": "<1 if patient found by either ANI or AltANI, 0 if not found, null before lookup>",
"Email": "<parent email address or 'Not Provided'>",
"temporaryPatientId": "<from lookup, create or null>"
"special_needs": "<e.g. 'Larry: light sensitivity; Garry: sound sensitivity' or null>",
"Child1_FirstName": "<first child's first name or null>",
"Child1_LastName": "<first child's last name or null>",
"Child1_DOB": "<first child's DOB, YYYY-MM-DD format or null>",
"Child1_patientId": "<patientId from lookup, temporaryPatientId from create or null>",
"Child1_appointmentId": "<from lookup, returned from book_child or null>",
"Child1_operatory_id": "<from lookup, book_child or null>",
"Child1_Intent": "<Schedule | Reschedule | Cancel | Confirm | | Late | FAQ | Other>",
"Child1_Intent_Complete": "<Schedule | Reschedule | Cancel | Confirm | Late | FAQ | Other | null>",
"Child1_Final_Disposition": "<Automated | Transfer | Abandoned>",
"Child1_Action_Taken_Notes": "<brief description of what happened for this child>",
"Child1_Appointment_Details": "<Date, Time, Provider, Location or null>",
"Child1_Appointment_Type": "<from clinic_info or null>",
"Child1_Cancellation_Reason": "<reason if cancelled or null>",
"Child1_Reschedule_Original_AppointmentId": "<original appointment ID that was cancelled during reschedule or null>",
"CancelDeflect": "<True | False | null>",
"Transfer_Reason": "<Agent Request | Configuration | Out of Scope | Specific Request | null>",
"Escalated_Business_Rule": "<Emergency | Live Agent or null>",
"Escalation_Intent": "<Escalation reason stated by caller or null>",
"Caller_Intent": "<Schedule | Reschedule | Cancel | Confirm | Late | FAQ | Other | Agent Request | NonResponsive Caller | null>",
"Call_Final_Disposition": "<Intent Complete | Transfer | Automated and Transferred | Abandoned>",
"Interaction_Summary": "<brief narrative of the call>",
"Abandonment_Point": "<where caller disconnected if abandoned, else null>",
"Language": "<English | Spanish>"
}},
"TC": "<final turn count>"
}}
**MANDATORY**: Include EVERY field above in Call_Summary. Never omit fields - use JSON `null` (not "none", "None", "N/A", or empty string) when data wasn't collected. For multiple children, add Child2_, Child3_ fields with the same structure.

<abandoned_call_handling>
When caller hangs up or you receive "caller_disconnected"/"hangup" event:

1. **Check current `Call_Final_Disposition` in PAYLOAD**:
   - If already `"Automated"` → KEEP IT. Intent was completed. Caller just didn't wait for goodbye.
   - If `"In Progress"` → Change to `"Abandoned"`, set `Abandonment_Point` to last action.
   - If `"Transfer"` → KEEP IT. Transfer was initiated.

2. Send final payload with `telephonyDisconnectCall`. No ANSWER needed.

**Key**: A caller hanging up after their appointment is booked/confirmed/cancelled is NOT abandoned—it's Automated.
</abandoned_call_handling>
