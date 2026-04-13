#!/usr/bin/env python3
"""
Corrected Abandonment Analysis - March 2026
Recalculates call outcomes by identifying successful completions
that were incorrectly classified as abandoned calls
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

def load_data(csv_path):
    """Load CSV data"""
    print("Loading CSV data...")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"✅ Loaded {len(df):,} records")
    return df

def analyze_corrected_abandonment(df):
    """Analyze call outcomes with corrected abandonment logic"""
    print("\n🔍 CORRECTED ABANDONMENT ANALYSIS")
    print("=" * 60)
    
    # Key columns for analysis
    disposition_col = 'screenPopData.payload.Call_Summary.Call_Final_Disposition'
    milestone_col = 'screenPopData.payload.Call_Summary.Milestone'
    abandonment_point_col = 'screenPopData.payload.Call_Summary.Abandonment_Point'
    intent_completed_col = 'screenPopData.payload.Call_Summary.Intent_Completed'
    
    # Create a working copy
    df_analysis = df.copy()
    
    # Initialize corrected disposition
    df_analysis['Corrected_Disposition'] = df_analysis[disposition_col]
    
    # Success indicators - these show the caller achieved their intent
    success_indicators = [
        'Appointment Confirmation',
        'Intent Complete', 
        'Intent Completed',
        'Appointment Confirmed',
        'Booking Complete',
        'Scheduling Complete'
    ]
    
    print("Checking for success indicators in Milestone and Abandonment_Point...")
    
    # Find calls marked as abandoned but with success indicators
    abandoned_mask = (df_analysis[disposition_col] == 'Abandoned')
    
    # Check Milestone field for success indicators
    milestone_success = df_analysis[milestone_col].fillna('').str.contains('|'.join(success_indicators), case=False, na=False)
    
    # Check Abandonment_Point field for success indicators  
    abandonment_success = df_analysis[abandonment_point_col].fillna('').str.contains('|'.join(success_indicators), case=False, na=False)
    
    # Check Intent_Completed field for actual completion
    intent_completed = (df_analysis[intent_completed_col].notna()) & (df_analysis[intent_completed_col] != '-') & (df_analysis[intent_completed_col] != '')
    
    # Identify incorrectly classified abandonments
    successful_but_abandoned = abandoned_mask & (milestone_success | abandonment_success | intent_completed)
    
    print(f"\n📊 RESULTS:")
    print(f"Original 'Abandoned' calls: {abandoned_mask.sum():,}")
    print(f"Success indicators in Milestone: {milestone_success.sum():,}")
    print(f"Success indicators in Abandonment_Point: {abandonment_success.sum():,}")
    print(f"Completed intents: {intent_completed.sum():,}")
    print(f"Calls to reclassify from 'Abandoned' to 'Successful': {successful_but_abandoned.sum():,}")
    
    # Update corrected disposition
    df_analysis.loc[successful_but_abandoned, 'Corrected_Disposition'] = 'Intent Complete (Corrected)'
    
    return df_analysis, successful_but_abandoned

def compare_dispositions(df_analysis):
    """Compare original vs corrected dispositions"""
    print("\n📈 ORIGINAL vs CORRECTED DISPOSITION COMPARISON")
    print("=" * 70)
    
    # Original disposition stats
    original_stats = df_analysis['screenPopData.payload.Call_Summary.Call_Final_Disposition'].value_counts()
    
    # Corrected disposition stats  
    corrected_stats = df_analysis['Corrected_Disposition'].value_counts()
    
    print("ORIGINAL DISPOSITION:")
    for disp, count in original_stats.items():
        percentage = (count / len(df_analysis)) * 100
        print(f"  {disp}: {count:,} calls ({percentage:.1f}%)")
    
    print("\nCORRECTED DISPOSITION:")
    for disp, count in corrected_stats.items():
        percentage = (count / len(df_analysis)) * 100
        print(f"  {disp}: {count:,} calls ({percentage:.1f}%)")
    
    # Calculate improvement
    original_abandoned = original_stats.get('Abandoned', 0)
    corrected_abandoned = corrected_stats.get('Abandoned', 0)
    
    original_success = original_stats.get('Intent Complete', 0)
    corrected_success = corrected_stats.get('Intent Complete', 0) + corrected_stats.get('Intent Complete (Corrected)', 0)
    
    print(f"\n🎯 PERFORMANCE IMPROVEMENT:")
    print(f"Abandoned calls reduced: {original_abandoned:,} → {corrected_abandoned:,} (-{original_abandoned - corrected_abandoned:,})")
    print(f"Successful calls increased: {original_success:,} → {corrected_success:,} (+{corrected_success - original_success:,})")
    
    # Calculate rates
    original_abandon_rate = (original_abandoned / len(df_analysis)) * 100
    corrected_abandon_rate = (corrected_abandoned / len(df_analysis)) * 100
    
    original_success_rate = (original_success / len(df_analysis)) * 100
    corrected_success_rate = (corrected_success / len(df_analysis)) * 100
    
    print(f"\nAbandonment rate: {original_abandon_rate:.1f}% → {corrected_abandon_rate:.1f}% (-{original_abandon_rate - corrected_abandon_rate:.1f}%)")
    print(f"Success rate: {original_success_rate:.1f}% → {corrected_success_rate:.1f}% (+{corrected_success_rate - original_success_rate:.1f}%)")
    
    return {
        'original_stats': original_stats.to_dict(),
        'corrected_stats': corrected_stats.to_dict(),
        'improvement': {
            'abandoned_reduction': original_abandoned - corrected_abandoned,
            'success_increase': corrected_success - original_success,
            'abandon_rate_change': corrected_abandon_rate - original_abandon_rate,
            'success_rate_change': corrected_success_rate - original_success_rate
        }
    }

def analyze_reclassified_calls(df_analysis, successful_but_abandoned):
    """Analyze the characteristics of reclassified calls"""
    print("\n🔍 ANALYSIS OF RECLASSIFIED CALLS")
    print("=" * 60)
    
    if successful_but_abandoned.sum() == 0:
        print("No calls were reclassified.")
        return {}
    
    reclassified_calls = df_analysis[successful_but_abandoned]
    
    print(f"Total reclassified calls: {len(reclassified_calls):,}")
    
    # Analyze milestones of reclassified calls
    milestone_col = 'screenPopData.payload.Call_Summary.Milestone'
    if milestone_col in df_analysis.columns:
        milestone_stats = reclassified_calls[milestone_col].value_counts()
        print(f"\nMilestones in reclassified calls:")
        for milestone, count in milestone_stats.head(10).items():
            print(f"  {milestone}: {count:,}")
    
    # Analyze abandonment points of reclassified calls
    abandonment_col = 'screenPopData.payload.Call_Summary.Abandonment_Point'
    if abandonment_col in df_analysis.columns:
        abandonment_stats = reclassified_calls[abandonment_col].value_counts()
        print(f"\nAbandonment points in reclassified calls:")
        for point, count in abandonment_stats.head(10).items():
            print(f"  {point}: {count:,}")
    
    # Analyze intent completion of reclassified calls
    intent_col = 'screenPopData.payload.Call_Summary.Intent_Completed'
    if intent_col in df_analysis.columns:
        intent_stats = reclassified_calls[intent_col].value_counts()
        print(f"\nCompleted intents in reclassified calls:")
        for intent, count in intent_stats.items():
            if intent != '-' and pd.notna(intent):
                print(f"  {intent}: {count:,}")
    
    # Analyze caller intents of reclassified calls
    caller_intent_col = 'screenPopData.payload.Call_Summary.Caller_Intent'
    if caller_intent_col in df_analysis.columns:
        caller_intent_stats = reclassified_calls[caller_intent_col].value_counts()
        print(f"\nCaller intents in reclassified calls:")
        for intent, count in caller_intent_stats.head(10).items():
            if intent != '-' and pd.notna(intent):
                print(f"  {intent}: {count:,}")
    
    return {
        'total_reclassified': len(reclassified_calls),
        'milestone_breakdown': milestone_stats.to_dict() if milestone_col in df_analysis.columns else {},
        'abandonment_point_breakdown': abandonment_stats.to_dict() if abandonment_col in df_analysis.columns else {},
        'intent_completion_breakdown': intent_stats.to_dict() if intent_col in df_analysis.columns else {}
    }

def calculate_true_performance_metrics(df_analysis):
    """Calculate performance metrics with corrected data"""
    print("\n📊 TRUE PERFORMANCE METRICS")
    print("=" * 60)
    
    total_calls = len(df_analysis)
    
    # Corrected disposition counts
    corrected_stats = df_analysis['Corrected_Disposition'].value_counts()
    
    # Calculate key metrics
    true_abandoned = corrected_stats.get('Abandoned', 0)
    successful_complete = corrected_stats.get('Intent Complete', 0) + corrected_stats.get('Intent Complete (Corrected)', 0)
    transfers = corrected_stats.get('Transfer', 0)
    other = total_calls - true_abandoned - successful_complete - transfers
    
    print(f"📈 CORRECTED PERFORMANCE SUMMARY:")
    print(f"  Total Calls: {total_calls:,}")
    print(f"  ✅ Successful Completions: {successful_complete:,} ({(successful_complete/total_calls)*100:.1f}%)")
    print(f"  📞 Transfers (Manual): {transfers:,} ({(transfers/total_calls)*100:.1f}%)")
    print(f"  🚨 True Abandonments: {true_abandoned:,} ({(true_abandoned/total_calls)*100:.1f}%)")
    print(f"  ❓ Other/Incomplete: {other:,} ({(other/total_calls)*100:.1f}%)")
    
    # Calculate AI effectiveness
    ai_handled = successful_complete
    human_required = transfers
    total_resolved = ai_handled + human_required
    
    if total_resolved > 0:
        ai_effectiveness = (ai_handled / total_resolved) * 100
        print(f"\n🤖 AI EFFECTIVENESS:")
        print(f"  AI Resolved: {ai_handled:,}")
        print(f"  Human Required: {human_required:,}")
        print(f"  AI Effectiveness Rate: {ai_effectiveness:.1f}%")
    
    return {
        'total_calls': total_calls,
        'successful_completions': successful_complete,
        'transfers': transfers,
        'true_abandonments': true_abandoned,
        'success_rate': (successful_complete/total_calls)*100,
        'abandon_rate': (true_abandoned/total_calls)*100,
        'transfer_rate': (transfers/total_calls)*100,
        'ai_effectiveness': ai_effectiveness if total_resolved > 0 else 0
    }

def main():
    """Main analysis function"""
    csv_path = "/Users/c1.jlange/Downloads/March workitem.csv"
    
    try:
        # Load data
        df = load_data(csv_path)
        
        # Analyze corrected abandonment
        df_analysis, successful_but_abandoned = analyze_corrected_abandonment(df)
        
        # Compare original vs corrected dispositions
        comparison_results = compare_dispositions(df_analysis)
        
        # Analyze reclassified calls
        reclassified_analysis = analyze_reclassified_calls(df_analysis, successful_but_abandoned)
        
        # Calculate true performance metrics
        performance_metrics = calculate_true_performance_metrics(df_analysis)
        
        print("\n" + "="*80)
        print("🎯 CORRECTED CALL PERFORMANCE SUMMARY")
        print("="*80)
        
        # Save results
        results = {
            'analysis_type': 'corrected_abandonment_analysis',
            'dataset_info': {
                'total_records': len(df),
                'analysis_date': datetime.now().isoformat()
            },
            'comparison_results': comparison_results,
            'reclassified_analysis': reclassified_analysis,
            'performance_metrics': performance_metrics,
            'key_insights': {
                'calls_reclassified': successful_but_abandoned.sum(),
                'abandonment_reduction': comparison_results['improvement']['abandon_rate_change'],
                'success_increase': comparison_results['improvement']['success_rate_change']
            }
        }
        
        # Save to JSON
        with open('/Users/c1.jlange/Documents/Cursor/Chord - Cursor/corrected_call_analysis.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✅ Analysis complete!")
        print(f"📊 Results saved to: corrected_call_analysis.json")
        
        # Show final summary
        print(f"\n🏆 FINAL CORRECTED METRICS:")
        print(f"   • True Success Rate: {performance_metrics['success_rate']:.1f}%")
        print(f"   • True Abandonment Rate: {performance_metrics['abandon_rate']:.1f}%")
        print(f"   • Transfer Rate: {performance_metrics['transfer_rate']:.1f}%")
        print(f"   • AI Effectiveness: {performance_metrics['ai_effectiveness']:.1f}%")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()