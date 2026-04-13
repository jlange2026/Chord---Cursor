#!/usr/bin/env python3
"""
Call Summary Statistics Report - March 2026
Analyzes specific Call_Summary payload columns for client reporting
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from collections import Counter

# Define the requested columns
REQUESTED_COLUMNS = [
    "screenPopData.payload.Call_Summary.ANIIsMatch",
    "screenPopData.payload.Call_Summary.Abandonment_Point",
    "screenPopData.payload.Call_Summary.Abandonment_Point.keyword",
    "screenPopData.payload.Call_Summary.AltANI",
    "screenPopData.payload.Call_Summary.AltANI.keyword",
    "screenPopData.payload.Call_Summary.AltANIIsMatch",
    "screenPopData.payload.Call_Summary.Call_Final_Disposition",
    "screenPopData.payload.Call_Summary.Call_Final_Disposition.keyword",
    "screenPopData.payload.Call_Summary.Call_Location",
    "screenPopData.payload.Call_Summary.Call_Location.keyword",
    "screenPopData.payload.Call_Summary.Caller_Email",
    "screenPopData.payload.Call_Summary.Caller_Email.keyword",
    "screenPopData.payload.Call_Summary.Caller_Identified",
    "screenPopData.payload.Call_Summary.Caller_Identified.keyword",
    "screenPopData.payload.Call_Summary.Caller_Intent",
    "screenPopData.payload.Call_Summary.Caller_Intent.keyword",
    "screenPopData.payload.Call_Summary.Caller_Name",
    "screenPopData.payload.Call_Summary.Caller_Name.keyword",
    "screenPopData.payload.Call_Summary.CancelDeflect",
    "screenPopData.payload.Call_Summary.Child1_Age",
    "screenPopData.payload.Call_Summary.Child1_Age.keyword",
    "screenPopData.payload.Call_Summary.Child1_Appointment_Details",
    "screenPopData.payload.Call_Summary.Child1_Appointment_Details.keyword",
    "screenPopData.payload.Call_Summary.Child1_Appointment_Type",
    "screenPopData.payload.Call_Summary.Child1_Appointment_Type.keyword",
    "screenPopData.payload.Call_Summary.Child1_Appt_Operatory_Id",
    "screenPopData.payload.Call_Summary.Child1_Appt_Operatory_Id.keyword",
    "screenPopData.payload.Call_Summary.Child1_DOB",
    "screenPopData.payload.Call_Summary.Child1_Final_Disposition",
    "screenPopData.payload.Call_Summary.Child1_Final_Disposition.keyword",
    "screenPopData.payload.Call_Summary.Child1_FirstName",
    "screenPopData.payload.Call_Summary.Child1_FirstName.keyword",
    "screenPopData.payload.Call_Summary.Child1_Intent",
    "screenPopData.payload.Call_Summary.Child1_Intent.keyword",
    "screenPopData.payload.Call_Summary.Child1_Intent_Complete",
    "screenPopData.payload.Call_Summary.Child1_Intent_Complete.keyword",
    "screenPopData.payload.Call_Summary.Child1_LastName",
    "screenPopData.payload.Call_Summary.Child1_LastName.keyword",
    "screenPopData.payload.Call_Summary.Child1_Reschedule_Original_AppointmentId",
    "screenPopData.payload.Call_Summary.Child1_Reschedule_Original_AppointmentId.keyword",
    "screenPopData.payload.Call_Summary.Child1_Reschedule_Original_Appointment_Type",
    "screenPopData.payload.Call_Summary.Child1_Reschedule_Original_Appointment_Type.keyword",
    "screenPopData.payload.Call_Summary.Child1_Reschedule_Original_Cancelled",
    "screenPopData.payload.Call_Summary.Child1_appointmentGUID",
    "screenPopData.payload.Call_Summary.Child1_appointmentGUID.keyword",
    "screenPopData.payload.Call_Summary.Child1_appointmentId",
    "screenPopData.payload.Call_Summary.Child1_appointmentId.keyword",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.appointmentTypeGUID",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.appointmentTypeGUID.keyword",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.date",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.day_of_week",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.day_of_week.keyword",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.minutes",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.operatory_id",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.operatory_id.keyword",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.productionTypeId",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.productionTypeId.keyword",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.providerId",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.providerId.keyword",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.scheduleColumnGUID",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.scheduleColumnGUID.keyword",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.scheduleViewGUID",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.scheduleViewGUID.keyword",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.time",
    "screenPopData.payload.Call_Summary.Child1_offered_slot.time.keyword",
    "screenPopData.payload.Call_Summary.Child1_operatory_id",
    "screenPopData.payload.Call_Summary.Child1_operatory_id.keyword",
    "screenPopData.payload.Call_Summary.Child1_patientGUID",
    "screenPopData.payload.Call_Summary.Child1_patientGUID.keyword",
    "screenPopData.payload.Call_Summary.Child1_patientId",
    "screenPopData.payload.Call_Summary.Child1_patientId.keyword",
    "screenPopData.payload.Call_Summary.Child2_Age",
    "screenPopData.payload.Call_Summary.Child2_Age.keyword",
    "screenPopData.payload.Call_Summary.Child2_Appointment_Details",
    "screenPopData.payload.Call_Summary.Child2_Appointment_Details.keyword",
    "screenPopData.payload.Call_Summary.Child2_Appointment_Type",
    "screenPopData.payload.Call_Summary.Child2_Appointment_Type.keyword",
    "screenPopData.payload.Call_Summary.Child2_Appt_Operatory_Id",
    "screenPopData.payload.Call_Summary.Child2_Appt_Operatory_Id.keyword",
    "screenPopData.payload.Call_Summary.Child2_DOB",
    "screenPopData.payload.Call_Summary.Child2_Final_Disposition",
    "screenPopData.payload.Call_Summary.Child2_Final_Disposition.keyword",
    "screenPopData.payload.Call_Summary.Child2_FirstName",
    "screenPopData.payload.Call_Summary.Child2_FirstName.keyword",
    "screenPopData.payload.Call_Summary.Child2_Intent",
    "screenPopData.payload.Call_Summary.Child2_Intent.keyword",
    "screenPopData.payload.Call_Summary.Child2_Intent_Complete",
    "screenPopData.payload.Call_Summary.Child2_Intent_Complete.keyword",
    "screenPopData.payload.Call_Summary.Child2_LastName",
    "screenPopData.payload.Call_Summary.Child2_LastName.keyword",
    "screenPopData.payload.Call_Summary.Child2_appointmentId",
    "screenPopData.payload.Call_Summary.Child2_appointmentId.keyword",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.appointmentTypeGUID",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.appointmentTypeGUID.keyword",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.date",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.day_of_week",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.day_of_week.keyword",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.operatory_id",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.operatory_id.keyword",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.productionTypeId",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.productionTypeId.keyword",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.providerId",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.providerId.keyword",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.scheduleColumnGUID",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.scheduleColumnGUID.keyword",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.scheduleViewGUID",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.scheduleViewGUID.keyword",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.time",
    "screenPopData.payload.Call_Summary.Child2_offered_slot.time.keyword",
    "screenPopData.payload.Call_Summary.Child2_patientId",
    "screenPopData.payload.Call_Summary.Child2_patientId.keyword",
    "screenPopData.payload.Call_Summary.Child2_special_needs",
    "screenPopData.payload.Call_Summary.Child2_special_needs.keyword",
    "screenPopData.payload.Call_Summary.Child3_Age",
    "screenPopData.payload.Call_Summary.Child3_Age.keyword",
    "screenPopData.payload.Call_Summary.Child3_DOB",
    "screenPopData.payload.Call_Summary.Child3_Final_Disposition",
    "screenPopData.payload.Call_Summary.Child3_Final_Disposition.keyword",
    "screenPopData.payload.Call_Summary.Child3_FirstName",
    "screenPopData.payload.Call_Summary.Child3_FirstName.keyword",
    "screenPopData.payload.Call_Summary.Child3_LastName",
    "screenPopData.payload.Call_Summary.Child3_LastName.keyword",
    "screenPopData.payload.Call_Summary.Child3_appointmentId",
    "screenPopData.payload.Call_Summary.Child3_appointmentId.keyword",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.date",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.day_of_week",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.day_of_week.keyword",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.operatory_id",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.operatory_id.keyword",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.productionTypeId",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.productionTypeId.keyword",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.providerId",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.providerId.keyword",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.time",
    "screenPopData.payload.Call_Summary.Child3_offered_slot.time.keyword",
    "screenPopData.payload.Call_Summary.Child3_special_needs",
    "screenPopData.payload.Call_Summary.Child3_special_needs.keyword",
    "screenPopData.payload.Call_Summary.Contact_Number",
    "screenPopData.payload.Call_Summary.Contact_Number.keyword",
    "screenPopData.payload.Call_Summary.Escalated_Business_Rule",
    "screenPopData.payload.Call_Summary.Escalated_Business_Rule.keyword",
    "screenPopData.payload.Call_Summary.Escalation_Intent",
    "screenPopData.payload.Call_Summary.Escalation_Intent.keyword",
    "screenPopData.payload.Call_Summary.Intent_Completed",
    "screenPopData.payload.Call_Summary.Intent_Completed.keyword",
    "screenPopData.payload.Call_Summary.Interaction_Summary",
    "screenPopData.payload.Call_Summary.Interaction_Summary.keyword",
    "screenPopData.payload.Call_Summary.IpSessionId",
    "screenPopData.payload.Call_Summary.IpSessionId.keyword",
    "screenPopData.payload.Call_Summary.Language",
    "screenPopData.payload.Call_Summary.Language.keyword",
    "screenPopData.payload.Call_Summary.Milestone",
    "screenPopData.payload.Call_Summary.Milestone.keyword",
    "screenPopData.payload.Call_Summary.Milestone_List",
    "screenPopData.payload.Call_Summary.Milestone_List.keyword",
    "screenPopData.payload.Call_Summary.PatientFound",
    "screenPopData.payload.Call_Summary.Patient_Count",
    "screenPopData.payload.Call_Summary.TC",
    "screenPopData.payload.Call_Summary.TC.keyword",
    "screenPopData.payload.Call_Summary.Transfer_Reason",
    "screenPopData.payload.Call_Summary.Transfer_Reason.keyword",
    "screenPopData.payload.Call_Summary.business_hours",
    "screenPopData.payload.Call_Summary.business_hours.keyword",
    "screenPopData.payload.Call_Summary.caller_firstName",
    "screenPopData.payload.Call_Summary.caller_firstName.keyword",
    "screenPopData.payload.Call_Summary.caller_id_number",
    "screenPopData.payload.Call_Summary.caller_id_number.keyword",
    "screenPopData.payload.Call_Summary.caller_intent",
    "screenPopData.payload.Call_Summary.caller_intent.keyword",
    "screenPopData.payload.Call_Summary.caller_lastName",
    "screenPopData.payload.Call_Summary.caller_lastName.keyword",
    "screenPopData.payload.Call_Summary.cancellationCodeId",
    "screenPopData.payload.Call_Summary.cancellationCodeId.keyword",
    "screenPopData.payload.Call_Summary.current_datetime",
    "screenPopData.payload.Call_Summary.guarantor_DOB",
    "screenPopData.payload.Call_Summary.guarantor_FirstName",
    "screenPopData.payload.Call_Summary.guarantor_FirstName.keyword",
    "screenPopData.payload.Call_Summary.guarantor_LastName",
    "screenPopData.payload.Call_Summary.guarantor_LastName.keyword",
    "screenPopData.payload.Call_Summary.guarantor_name",
    "screenPopData.payload.Call_Summary.guarantor_name.keyword",
    "screenPopData.payload.Call_Summary.insurance_group_number",
    "screenPopData.payload.Call_Summary.insurance_group_number.keyword",
    "screenPopData.payload.Call_Summary.insurance_member_id",
    "screenPopData.payload.Call_Summary.insurance_member_id.keyword",
    "screenPopData.payload.Call_Summary.insurance_provider",
    "screenPopData.payload.Call_Summary.insurance_provider.keyword",
    "screenPopData.payload.Call_Summary.insurance_status",
    "screenPopData.payload.Call_Summary.insurance_status.keyword",
    "screenPopData.payload.Call_Summary.live_agent_request_count",
    "screenPopData.payload.Call_Summary.locationGUID",
    "screenPopData.payload.Call_Summary.locationGUID.keyword",
    "screenPopData.payload.Call_Summary.locationId",
    "screenPopData.payload.Call_Summary.locationId.keyword",
    "screenPopData.payload.Call_Summary.locationSpecialty",
    "screenPopData.payload.Call_Summary.locationSpecialty.keyword",
    "screenPopData.payload.Call_Summary.location_name",
    "screenPopData.payload.Call_Summary.location_name.keyword",
    "screenPopData.payload.Call_Summary.new_patient",
    "screenPopData.payload.Call_Summary.new_patient.keyword",
    "screenPopData.payload.Call_Summary.no_input_count",
    "screenPopData.payload.Call_Summary.previousOrtho",
    "screenPopData.payload.Call_Summary.specialNeeds",
    "screenPopData.payload.Call_Summary.specialNeeds.keyword",
    "screenPopData.payload.Call_Summary.special_needs",
    "screenPopData.payload.Call_Summary.special_needs.keyword",
    # Additional payload columns
    "screenPopData.payload.Caller_Email",
    "screenPopData.payload.Caller_Email.keyword",
    "screenPopData.payload.Caller_Identified",
    "screenPopData.payload.Caller_Intent",
    "screenPopData.payload.Caller_Intent.keyword",
    "screenPopData.payload.Caller_Name",
    "screenPopData.payload.Caller_Name.keyword",
    "screenPopData.payload.Child1_Age",
    "screenPopData.payload.Child1_Age.keyword",
    "screenPopData.payload.Child1_Appointment_Details",
    "screenPopData.payload.Child1_Appointment_Details.keyword",
    "screenPopData.payload.Child1_Appointment_Type",
    "screenPopData.payload.Child1_Appointment_Type.keyword",
    "screenPopData.payload.Child1_Appt_Operatory_Id",
    "screenPopData.payload.Child1_Appt_Operatory_Id.keyword",
    "screenPopData.payload.Child1_DOB",
    "screenPopData.payload.Child1_FirstName",
    "screenPopData.payload.Child1_FirstName.keyword",
    "screenPopData.payload.Child1_Intent",
    "screenPopData.payload.Child1_Intent.keyword",
    "screenPopData.payload.Child1_Intent_Complete",
    "screenPopData.payload.Child1_Intent_Complete.keyword",
    "screenPopData.payload.Child1_LastName",
    "screenPopData.payload.Child1_LastName.keyword"
]

def load_data(csv_path):
    """Load CSV data with error handling"""
    print("Loading CSV data...")
    try:
        df = pd.read_csv(csv_path, low_memory=False)
        print(f"✅ Loaded {len(df):,} records with {len(df.columns):,} columns")
        return df
    except Exception as e:
        print(f"❌ Error loading CSV: {str(e)}")
        return None

def check_column_availability(df, requested_cols):
    """Check which requested columns exist in the dataset"""
    print("\n🔍 CHECKING COLUMN AVAILABILITY")
    print("=" * 60)
    
    available_cols = []
    missing_cols = []
    
    for col in requested_cols:
        if col in df.columns:
            available_cols.append(col)
        else:
            missing_cols.append(col)
    
    print(f"✅ Available columns: {len(available_cols):,}")
    print(f"❌ Missing columns: {len(missing_cols):,}")
    print(f"📊 Coverage: {(len(available_cols)/len(requested_cols)*100):.1f}%")
    
    return available_cols, missing_cols

def analyze_call_disposition(df, cols):
    """Analyze Call Final Disposition"""
    print("\n📋 CALL FINAL DISPOSITION ANALYSIS")
    print("=" * 60)
    
    disposition_col = 'screenPopData.payload.Call_Summary.Call_Final_Disposition'
    if disposition_col in cols:
        disposition_stats = df[disposition_col].value_counts(dropna=False)
        
        print("Call Final Disposition:")
        for disp, count in disposition_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {disp}: {count:,} calls ({percentage:.1f}%)")
        
        return disposition_stats.to_dict()
    else:
        print("❌ Call Final Disposition data not available")
        return {}

def analyze_caller_intent(df, cols):
    """Analyze Caller Intent patterns"""
    print("\n🎯 CALLER INTENT ANALYSIS")
    print("=" * 60)
    
    intent_col = 'screenPopData.payload.Call_Summary.Caller_Intent'
    if intent_col in cols:
        intent_stats = df[intent_col].value_counts(dropna=False)
        
        print("Caller Intent Distribution:")
        for intent, count in intent_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {intent}: {count:,} calls ({percentage:.1f}%)")
        
        # Intent completion analysis
        completion_col = 'screenPopData.payload.Call_Summary.Intent_Completed'
        if completion_col in cols:
            print("\nIntent Completion Analysis:")
            completion_stats = df[completion_col].value_counts(dropna=False)
            for comp, count in completion_stats.items():
                percentage = (count / len(df)) * 100
                print(f"  {comp}: {count:,} calls ({percentage:.1f}%)")
        
        return {
            'intent_distribution': intent_stats.to_dict(),
            'completion_stats': completion_stats.to_dict() if completion_col in cols else {}
        }
    else:
        print("❌ Caller Intent data not available")
        return {}

def analyze_patient_demographics(df, cols):
    """Analyze patient demographics and counts"""
    print("\n👥 PATIENT DEMOGRAPHICS ANALYSIS")
    print("=" * 60)
    
    # Patient count analysis
    patient_count_col = 'screenPopData.payload.Call_Summary.Patient_Count'
    if patient_count_col in cols:
        count_stats = df[patient_count_col].value_counts(dropna=False)
        
        print("Patient Count per Call:")
        for count, calls in count_stats.items():
            percentage = (calls / len(df)) * 100
            print(f"  {count} patients: {calls:,} calls ({percentage:.1f}%)")
    
    # New vs existing patient analysis
    new_patient_col = 'screenPopData.payload.Call_Summary.new_patient'
    if new_patient_col in cols:
        new_patient_stats = df[new_patient_col].value_counts(dropna=False)
        
        print("\nNew vs Existing Patient:")
        for status, count in new_patient_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {status}: {count:,} calls ({percentage:.1f}%)")
    
    # Patient found analysis
    patient_found_col = 'screenPopData.payload.Call_Summary.PatientFound'
    if patient_found_col in cols:
        found_stats = df[patient_found_col].value_counts(dropna=False)
        
        print("\nPatient Found in System:")
        for status, count in found_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {status}: {count:,} calls ({percentage:.1f}%)")
    
    return {
        'patient_count': count_stats.to_dict() if patient_count_col in cols else {},
        'new_patient': new_patient_stats.to_dict() if new_patient_col in cols else {},
        'patient_found': found_stats.to_dict() if patient_found_col in cols else {}
    }

def analyze_appointment_data(df, cols):
    """Analyze appointment-related data"""
    print("\n📅 APPOINTMENT ANALYSIS")
    print("=" * 60)
    
    # Child1 appointment analysis
    appt_type_col = 'screenPopData.payload.Call_Summary.Child1_Appointment_Type'
    if appt_type_col in cols:
        type_stats = df[appt_type_col].value_counts(dropna=False)
        
        print("Child1 Appointment Types:")
        for appt_type, count in type_stats.head(10).items():
            percentage = (count / len(df)) * 100
            print(f"  {appt_type}: {count:,} calls ({percentage:.1f}%)")
    
    # Offered slot day analysis
    day_col = 'screenPopData.payload.Call_Summary.Child1_offered_slot.day_of_week'
    if day_col in cols:
        day_stats = df[day_col].value_counts(dropna=False)
        
        print("\nOffered Slot Days:")
        for day, count in day_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {day}: {count:,} slots ({percentage:.1f}%)")
    
    return {
        'appointment_types': type_stats.to_dict() if appt_type_col in cols else {},
        'offered_days': day_stats.to_dict() if day_col in cols else {}
    }

def analyze_location_data(df, cols):
    """Analyze location-specific data"""
    print("\n🏥 LOCATION DATA ANALYSIS")
    print("=" * 60)
    
    # Location ID analysis
    location_id_col = 'screenPopData.payload.Call_Summary.locationId'
    if location_id_col in cols:
        location_stats = df[location_id_col].value_counts(dropna=False)
        
        print("Location Distribution:")
        for loc_id, count in location_stats.head(10).items():
            percentage = (count / len(df)) * 100
            print(f"  Location {loc_id}: {count:,} calls ({percentage:.1f}%)")
    
    # Location specialty analysis
    specialty_col = 'screenPopData.payload.Call_Summary.locationSpecialty'
    if specialty_col in cols:
        specialty_stats = df[specialty_col].value_counts(dropna=False)
        
        print("\nLocation Specialty:")
        for specialty, count in specialty_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {specialty}: {count:,} calls ({percentage:.1f}%)")
    
    return {
        'location_distribution': location_stats.to_dict() if location_id_col in cols else {},
        'specialty_distribution': specialty_stats.to_dict() if specialty_col in cols else {}
    }

def analyze_insurance_data(df, cols):
    """Analyze insurance-related data"""
    print("\n💳 INSURANCE ANALYSIS")
    print("=" * 60)
    
    # Insurance provider analysis
    provider_col = 'screenPopData.payload.Call_Summary.insurance_provider'
    if provider_col in cols:
        provider_stats = df[provider_col].value_counts(dropna=False)
        
        print("Insurance Providers:")
        for provider, count in provider_stats.head(10).items():
            percentage = (count / len(df)) * 100
            print(f"  {provider}: {count:,} calls ({percentage:.1f}%)")
    
    # Insurance status analysis
    status_col = 'screenPopData.payload.Call_Summary.insurance_status'
    if status_col in cols:
        status_stats = df[status_col].value_counts(dropna=False)
        
        print("\nInsurance Status:")
        for status, count in status_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {status}: {count:,} calls ({percentage:.1f}%)")
    
    return {
        'provider_distribution': provider_stats.to_dict() if provider_col in cols else {},
        'status_distribution': status_stats.to_dict() if status_col in cols else {}
    }

def analyze_call_metrics(df, cols):
    """Analyze call-specific metrics"""
    print("\n📞 CALL METRICS ANALYSIS")
    print("=" * 60)
    
    # Turn count analysis
    tc_col = 'screenPopData.payload.Call_Summary.TC'
    if tc_col in cols:
        tc_stats = df[tc_col].astype(str).value_counts(dropna=False)
        
        print("Turn Count Distribution:")
        for tc, count in tc_stats.head(10).items():
            percentage = (count / len(df)) * 100
            print(f"  {tc} turns: {count:,} calls ({percentage:.1f}%)")
        
        # Calculate average turn count
        tc_numeric = pd.to_numeric(df[tc_col], errors='coerce')
        avg_tc = tc_numeric.mean()
        print(f"\nAverage Turn Count: {avg_tc:.2f}")
    
    # Caller identified analysis
    identified_col = 'screenPopData.payload.Call_Summary.Caller_Identified'
    if identified_col in cols:
        identified_stats = df[identified_col].value_counts(dropna=False)
        
        print("\nCaller Identification Success:")
        for status, count in identified_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {status}: {count:,} calls ({percentage:.1f}%)")
    
    return {
        'turn_count_distribution': tc_stats.to_dict() if tc_col in cols else {},
        'avg_turn_count': avg_tc if tc_col in cols else None,
        'caller_identified': identified_stats.to_dict() if identified_col in cols else {}
    }

def generate_data_quality_report(df, available_cols):
    """Generate data quality report for available columns"""
    print("\n📊 DATA QUALITY REPORT")
    print("=" * 60)
    
    quality_report = {}
    
    for col in available_cols[:20]:  # Analyze first 20 columns for brevity
        total_records = len(df)
        null_count = df[col].isnull().sum()
        non_null_count = total_records - null_count
        completeness = (non_null_count / total_records) * 100
        
        quality_report[col] = {
            'total_records': total_records,
            'non_null_count': non_null_count,
            'null_count': null_count,
            'completeness_pct': completeness
        }
    
    # Print top 10 most complete fields
    sorted_quality = sorted(quality_report.items(), key=lambda x: x[1]['completeness_pct'], reverse=True)
    
    print("Top 10 Most Complete Fields:")
    for col, stats in sorted_quality[:10]:
        col_short = col.split('.')[-1]  # Show only the field name part
        print(f"  {col_short}: {stats['completeness_pct']:.1f}% complete ({stats['non_null_count']:,}/{stats['total_records']:,})")
    
    return quality_report

def main():
    """Main analysis function"""
    csv_path = "/Users/c1.jlange/Downloads/March workitem.csv"
    
    # Load data
    df = load_data(csv_path)
    if df is None:
        return
    
    # Check column availability
    available_cols, missing_cols = check_column_availability(df, REQUESTED_COLUMNS)
    
    if len(available_cols) == 0:
        print("❌ No requested columns found in dataset!")
        return
    
    # Perform analyses on available data
    analyses = {}
    
    try:
        analyses['disposition'] = analyze_call_disposition(df, available_cols)
        analyses['intent'] = analyze_caller_intent(df, available_cols)
        analyses['demographics'] = analyze_patient_demographics(df, available_cols)
        analyses['appointments'] = analyze_appointment_data(df, available_cols)
        analyses['locations'] = analyze_location_data(df, available_cols)
        analyses['insurance'] = analyze_insurance_data(df, available_cols)
        analyses['call_metrics'] = analyze_call_metrics(df, available_cols)
        
        # Data quality report
        quality_report = generate_data_quality_report(df, available_cols)
        
        # Generate summary
        print("\n" + "="*80)
        print("📋 CALL SUMMARY STATISTICS REPORT - MARCH 2026")
        print("="*80)
        
        print(f"""
🎯 DATASET SUMMARY:
   • Total Records: {len(df):,}
   • Requested Columns: {len(REQUESTED_COLUMNS):,}
   • Available Columns: {len(available_cols):,}
   • Data Coverage: {(len(available_cols)/len(REQUESTED_COLUMNS)*100):.1f}%
        """)
        
        # Save results
        results = {
            'dataset_summary': {
                'total_records': len(df),
                'requested_columns': len(REQUESTED_COLUMNS),
                'available_columns': len(available_cols),
                'missing_columns': len(missing_cols),
                'coverage_pct': (len(available_cols)/len(REQUESTED_COLUMNS)*100)
            },
            'available_columns': available_cols,
            'missing_columns': missing_cols,
            'analyses': analyses,
            'data_quality': quality_report,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save to JSON
        with open('/Users/c1.jlange/Documents/Cursor/Chord - Cursor/call_summary_statistics.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save missing columns to text file for easy review
        with open('/Users/c1.jlange/Documents/Cursor/Chord - Cursor/missing_columns.txt', 'w') as f:
            f.write("MISSING CALL SUMMARY COLUMNS\n")
            f.write("="*50 + "\n\n")
            for col in missing_cols:
                f.write(f"{col}\n")
        
        print("\n✅ Analysis complete!")
        print("📊 Results saved to: call_summary_statistics.json")
        print("📋 Missing columns list: missing_columns.txt")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()