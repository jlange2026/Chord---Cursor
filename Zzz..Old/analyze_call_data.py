#!/usr/bin/env python3
"""
Comprehensive Call Data Analysis
Analyzes call disposition, intents, and properly classifies abandoned vs completed calls
"""

import csv
import json
from collections import defaultdict, Counter
from datetime import datetime

def parse_json_field(field_value):
    """Safely parse JSON fields"""
    if not field_value or field_value == '{}':
        return {}
    try:
        return json.loads(field_value)
    except json.JSONDecodeError:
        return {}

def analyze_calls(csv_file):
    """Analyze call data and generate comprehensive report"""
    
    # Initialize counters
    total_calls = 0
    intents = Counter()
    final_dispositions = Counter()
    escalation_reasons = Counter()
    
    # Track abandoned vs completed
    truly_abandoned = []
    intent_complete_with_abandonment_point = []
    intent_complete_no_abandonment = []
    transfers = []
    in_progress_abandoned = []
    
    # Intent-specific tracking
    intent_outcomes = defaultdict(lambda: {'complete': 0, 'abandoned': 0, 'transfer': 0})
    
    # Cancellation tracking
    cancellations = []
    reschedules = []
    saved_cancels = []  # Cancels that turned into reschedules
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_calls += 1
            
            # Parse the Call_Summary JSON
            call_summary = parse_json_field(row.get('screenPopData.payload.Call_Summary', '{}'))
            
            # Extract key fields
            session_id = row.get('intelepeerSessionId', '')
            conversation_id = row.get('ConversationId', '')
            ani = row.get('ANI', '')
            call_creation = row.get('callCreationDateGMT', '')
            duration = row.get('IVADuration', '0')
            
            final_disposition = call_summary.get('Call_Final_Disposition', 'Unknown')
            abandonment_point = call_summary.get('Abandonment_Point')
            
            # Child1 fields
            child1_intent = call_summary.get('Child1_Intent', 'None')
            child1_final_disposition = call_summary.get('Child1_Final_Disposition', 'Unknown')
            child1_intent_complete = call_summary.get('Child1_Intent_Complete')
            
            # Escalation
            escalated_rule = call_summary.get('Escalated_Business_Rule')
            escalation_intent = call_summary.get('Escalation_Intent')
            
            caller_name = call_summary.get('Caller_Name', 'Unknown')
            location = call_summary.get('Call_Location', 'Unknown')
            
            # Track intents
            if child1_intent and child1_intent != 'None':
                intents[child1_intent] += 1
            
            # Track final dispositions
            final_dispositions[final_disposition] += 1
            
            # Track escalations
            if escalated_rule:
                escalation_reasons[escalated_rule] += 1
            
            # Determine TRUE classification
            has_abandonment_point = abandonment_point is not None and abandonment_point != ''
            
            call_record = {
                'session_id': session_id,
                'conversation_id': conversation_id,
                'ani': ani,
                'caller_name': caller_name,
                'location': location,
                'creation_time': call_creation,
                'duration': duration,
                'intent': child1_intent,
                'final_disposition': final_disposition,
                'child1_disposition': child1_final_disposition,
                'abandonment_point': abandonment_point,
                'escalated_rule': escalated_rule,
                'escalation_intent': escalation_intent
            }
            
            # CRITICAL CLASSIFICATION LOGIC
            # A call should be considered "Intent Complete" if:
            # 1. Call_Final_Disposition is "Intent Complete" OR
            # 2. Child1_Final_Disposition is "Intent Complete" OR
            # 3. Child1_Intent_Complete is populated with a valid intent
            
            is_intent_complete = (
                final_disposition == 'Intent Complete' or
                child1_final_disposition == 'Intent Complete' or
                (child1_intent_complete and child1_intent_complete != '')
            )
            
            if final_disposition == 'Transfer' or child1_final_disposition == 'Transfer':
                transfers.append(call_record)
                if child1_intent:
                    intent_outcomes[child1_intent]['transfer'] += 1
                    
            elif is_intent_complete:
                # Intent was completed
                if has_abandonment_point:
                    # Caller hung up after intent was complete (NOT truly abandoned)
                    intent_complete_with_abandonment_point.append(call_record)
                else:
                    # Normal completion
                    intent_complete_no_abandonment.append(call_record)
                
                if child1_intent:
                    intent_outcomes[child1_intent]['complete'] += 1
                    
            elif has_abandonment_point:
                # Truly abandoned - caller hung up before completing intent
                truly_abandoned.append(call_record)
                if child1_intent:
                    intent_outcomes[child1_intent]['abandoned'] += 1
                    
            else:
                # In Progress or other unclear state
                in_progress_abandoned.append(call_record)
                if child1_intent:
                    intent_outcomes[child1_intent]['abandoned'] += 1
            
            # Track specific intents
            if child1_intent == 'Cancel':
                if is_intent_complete:
                    cancellations.append(call_record)
            elif child1_intent == 'Reschedule':
                reschedules.append(call_record)
                # Check if this was a saved cancel
                if call_summary.get('Child1_Reschedule_Original_AppointmentId'):
                    saved_cancels.append(call_record)
    
    return {
        'total_calls': total_calls,
        'intents': intents,
        'final_dispositions': final_dispositions,
        'escalation_reasons': escalation_reasons,
        'intent_outcomes': dict(intent_outcomes),
        'truly_abandoned': truly_abandoned,
        'intent_complete_with_abandonment_point': intent_complete_with_abandonment_point,
        'intent_complete_no_abandonment': intent_complete_no_abandonment,
        'transfers': transfers,
        'in_progress_abandoned': in_progress_abandoned,
        'cancellations': cancellations,
        'reschedules': reschedules,
        'saved_cancels': saved_cancels
    }

def generate_report(analysis):
    """Generate comprehensive text report"""
    
    report = []
    report.append("=" * 80)
    report.append("CALL CENTER ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary Statistics
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 80)
    report.append(f"Total Calls Analyzed: {analysis['total_calls']}")
    report.append("")
    
    # CRITICAL FINDING
    misclassified_count = len(analysis['intent_complete_with_abandonment_point'])
    truly_abandoned_count = len(analysis['truly_abandoned'])
    
    report.append("CRITICAL FINDING - Call Classification Issue:")
    report.append("-" * 80)
    report.append(f"Calls with Intent Complete but Abandonment Point Set: {misclassified_count}")
    report.append(f"  → These are being INCORRECTLY classified as 'abandoned'")
    report.append(f"  → These should be classified as 'Intent Complete'")
    report.append(f"  → The caller hung up AFTER their need was fulfilled")
    report.append("")
    report.append(f"Truly Abandoned Calls (Intent NOT Complete): {truly_abandoned_count}")
    report.append(f"  → These are correctly classified as abandoned")
    report.append("")
    
    # Corrected metrics
    total_intent_complete = len(analysis['intent_complete_no_abandonment']) + misclassified_count
    report.append(f"CORRECTED METRICS:")
    report.append(f"  Total Intent Complete: {total_intent_complete}")
    report.append(f"  Total Transfers: {len(analysis['transfers'])}")
    report.append(f"  Total Truly Abandoned: {truly_abandoned_count}")
    report.append(f"  Total In Progress/Other: {len(analysis['in_progress_abandoned'])}")
    report.append("")
    
    # Intent Breakdown
    report.append("INTENT ANALYSIS")
    report.append("-" * 80)
    for intent, count in analysis['intents'].most_common():
        report.append(f"{intent}: {count} calls")
        if intent in analysis['intent_outcomes']:
            outcomes = analysis['intent_outcomes'][intent]
            report.append(f"  ├─ Completed: {outcomes['complete']}")
            report.append(f"  ├─ Transferred: {outcomes['transfer']}")
            report.append(f"  └─ Abandoned: {outcomes['abandoned']}")
    report.append("")
    
    # Key Metrics
    report.append("KEY PERFORMANCE METRICS")
    report.append("-" * 80)
    
    # Cancellations
    report.append(f"Total Cancellations Completed: {len(analysis['cancellations'])}")
    report.append(f"Total Reschedules Completed: {len(analysis['reschedules'])}")
    report.append(f"Saved Cancels (Cancel → Reschedule): {len(analysis['saved_cancels'])}")
    
    if analysis['cancellations']:
        save_rate = (len(analysis['saved_cancels']) / len(analysis['cancellations'])) * 100
        report.append(f"Cancel Save Rate: {save_rate:.1f}%")
    report.append("")
    
    # Escalations
    report.append("ESCALATION ANALYSIS")
    report.append("-" * 80)
    report.append(f"Total Transfers: {len(analysis['transfers'])}")
    for reason, count in analysis['escalation_reasons'].most_common():
        report.append(f"  {reason}: {count} calls")
    report.append("")
    
    # Final Disposition Breakdown
    report.append("FINAL DISPOSITION (AS RECORDED IN DATA)")
    report.append("-" * 80)
    for disposition, count in analysis['final_dispositions'].most_common():
        report.append(f"{disposition}: {count} calls")
    report.append("")
    
    # Detailed Examples
    report.append("EXAMPLES OF MISCLASSIFIED CALLS")
    report.append("-" * 80)
    report.append("Sample calls marked with Abandonment Point but Intent Complete:")
    report.append("")
    
    for i, call in enumerate(analysis['intent_complete_with_abandonment_point'][:5], 1):
        report.append(f"Example {i}:")
        report.append(f"  Session: {call['session_id']}")
        report.append(f"  Caller: {call['caller_name']}")
        report.append(f"  Intent: {call['intent']}")
        report.append(f"  Disposition: {call['final_disposition']} / {call['child1_disposition']}")
        report.append(f"  Abandonment Point: {call['abandonment_point']}")
        report.append(f"  → Classification: Should be 'Intent Complete', NOT 'Abandoned'")
        report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)

def export_misclassified_calls(analysis, output_file):
    """Export misclassified calls to CSV for further review"""
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['session_id', 'conversation_id', 'ani', 'caller_name', 'location', 
                     'creation_time', 'duration', 'intent', 'final_disposition', 
                     'child1_disposition', 'abandonment_point', 'escalated_rule', 
                     'escalation_intent', 'correct_classification']
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Export misclassified calls
        for call in analysis['intent_complete_with_abandonment_point']:
            call_copy = call.copy()
            call_copy['correct_classification'] = 'Intent Complete (NOT Abandoned)'
            writer.writerow(call_copy)

if __name__ == '__main__':
    print("Analyzing call data...")
    
    # Analyze the data
    analysis = analyze_calls('Data_2026-01-21-dental.prod.csv')
    
    # Generate report
    report = generate_report(analysis)
    
    # Print to console
    print(report)
    
    # Save to file
    with open('Call_Analysis_Report.txt', 'w') as f:
        f.write(report)
    print("\n✓ Full report saved to: Call_Analysis_Report.txt")
    
    # Export misclassified calls
    export_misclassified_calls(analysis, 'Misclassified_Calls.csv')
    print("✓ Misclassified calls exported to: Misclassified_Calls.csv")
    
    # Generate JSON summary for programmatic access
    summary = {
        'total_calls': analysis['total_calls'],
        'corrected_metrics': {
            'intent_complete': len(analysis['intent_complete_no_abandonment']) + len(analysis['intent_complete_with_abandonment_point']),
            'truly_abandoned': len(analysis['truly_abandoned']),
            'transfers': len(analysis['transfers']),
            'in_progress': len(analysis['in_progress_abandoned'])
        },
        'misclassification_issue': {
            'calls_affected': len(analysis['intent_complete_with_abandonment_point']),
            'description': 'Calls with Intent Complete but marked with Abandonment Point'
        },
        'intent_breakdown': dict(analysis['intents']),
        'intent_outcomes': analysis['intent_outcomes']
    }
    
    with open('Call_Analysis_Summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print("✓ JSON summary saved to: Call_Analysis_Summary.json")
    
    print("\nAnalysis complete!")
