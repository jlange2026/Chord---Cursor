#!/usr/bin/env python3
"""
Abandonment Point Analysis - March 2026
Analyzes where truly abandoned calls are dropping off in the call flow
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from collections import Counter

def load_data(csv_path):
    """Load CSV data"""
    print("Loading CSV data...")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"✅ Loaded {len(df):,} records")
    return df

def identify_true_abandonments(df):
    """Identify truly abandoned calls (excluding successful completions)"""
    print("\n🔍 IDENTIFYING TRUE ABANDONMENTS")
    print("=" * 60)
    
    # Key columns
    disposition_col = 'screenPopData.payload.Call_Summary.Call_Final_Disposition'
    milestone_col = 'screenPopData.payload.Call_Summary.Milestone'
    abandonment_point_col = 'screenPopData.payload.Call_Summary.Abandonment_Point'
    intent_completed_col = 'screenPopData.payload.Call_Summary.Intent_Completed'
    
    # Success indicators - these show the caller achieved their intent
    success_indicators = [
        'Appointment Confirmation',
        'Intent Complete', 
        'Intent Completed',
        'Appointment Confirmed',
        'Booking Complete',
        'Scheduling Complete'
    ]
    
    # Start with calls marked as abandoned
    abandoned_mask = (df[disposition_col] == 'Abandoned')
    
    # Check for success indicators
    milestone_success = df[milestone_col].fillna('').str.contains('|'.join(success_indicators), case=False, na=False)
    abandonment_success = df[abandonment_point_col].fillna('').str.contains('|'.join(success_indicators), case=False, na=False)
    intent_completed = (df[intent_completed_col].notna()) & (df[intent_completed_col] != '-') & (df[intent_completed_col] != '')
    
    # True abandonments = marked as abandoned BUT without success indicators
    true_abandoned_mask = abandoned_mask & ~(milestone_success | abandonment_success | intent_completed)
    
    print(f"Original 'Abandoned' calls: {abandoned_mask.sum():,}")
    print(f"Calls with success indicators: {(milestone_success | abandonment_success | intent_completed).sum():,}")
    print(f"TRUE abandoned calls: {true_abandoned_mask.sum():,}")
    
    return df[true_abandoned_mask]

def analyze_abandonment_points(true_abandoned_df):
    """Analyze where true abandonments are occurring"""
    print("\n📊 ABANDONMENT POINT ANALYSIS")
    print("=" * 60)
    
    abandonment_col = 'screenPopData.payload.Call_Summary.Abandonment_Point'
    
    if abandonment_col not in true_abandoned_df.columns:
        print("❌ Abandonment_Point column not found")
        return {}
    
    # Count abandonment points
    abandonment_stats = true_abandoned_df[abandonment_col].value_counts(dropna=False)
    
    print(f"Abandonment Point Distribution ({len(true_abandoned_df):,} true abandoned calls):")
    print("=" * 70)
    
    total_abandoned = len(true_abandoned_df)
    
    for point, count in abandonment_stats.items():
        percentage = (count / total_abandoned) * 100
        print(f"  {point}: {count:,} calls ({percentage:.1f}%)")
    
    return abandonment_stats.to_dict()

def analyze_milestone_at_abandonment(true_abandoned_df):
    """Analyze what milestone callers reached before abandoning"""
    print("\n📍 MILESTONE AT ABANDONMENT ANALYSIS")
    print("=" * 60)
    
    milestone_col = 'screenPopData.payload.Call_Summary.Milestone'
    
    if milestone_col not in true_abandoned_df.columns:
        print("❌ Milestone column not found")
        return {}
    
    milestone_stats = true_abandoned_df[milestone_col].value_counts(dropna=False)
    
    print(f"Last Milestone Before Abandonment ({len(true_abandoned_df):,} calls):")
    print("=" * 70)
    
    total_abandoned = len(true_abandoned_df)
    
    for milestone, count in milestone_stats.head(15).items():
        percentage = (count / total_abandoned) * 100
        print(f"  {milestone}: {count:,} calls ({percentage:.1f}%)")
    
    return milestone_stats.to_dict()

def analyze_abandonment_by_turn_count(true_abandoned_df):
    """Analyze abandonment patterns by conversation length"""
    print("\n🔄 ABANDONMENT BY TURN COUNT")
    print("=" * 60)
    
    tc_col = 'screenPopData.payload.Call_Summary.TC'
    
    if tc_col not in true_abandoned_df.columns:
        print("❌ Turn Count column not found")
        return {}
    
    # Convert to numeric and analyze
    true_abandoned_df_copy = true_abandoned_df.copy()
    true_abandoned_df_copy['TC_numeric'] = pd.to_numeric(true_abandoned_df_copy[tc_col], errors='coerce')
    
    # Remove NaN values
    tc_clean = true_abandoned_df_copy[true_abandoned_df_copy['TC_numeric'].notna()]
    
    if len(tc_clean) == 0:
        print("❌ No valid turn count data")
        return {}
    
    # Create turn count ranges
    tc_clean['TC_range'] = pd.cut(tc_clean['TC_numeric'], 
                                  bins=[0, 2, 4, 6, 8, 10, float('inf')], 
                                  labels=['1-2 turns', '3-4 turns', '5-6 turns', '7-8 turns', '9-10 turns', '11+ turns'],
                                  right=True)
    
    tc_range_stats = tc_clean['TC_range'].value_counts()
    
    print("Abandonment by Conversation Length:")
    print("=" * 40)
    
    for tc_range, count in tc_range_stats.items():
        percentage = (count / len(tc_clean)) * 100
        print(f"  {tc_range}: {count:,} calls ({percentage:.1f}%)")
    
    # Calculate statistics
    avg_tc = tc_clean['TC_numeric'].mean()
    median_tc = tc_clean['TC_numeric'].median()
    
    print(f"\nAverage turns before abandonment: {avg_tc:.2f}")
    print(f"Median turns before abandonment: {median_tc:.1f}")
    
    return {
        'range_distribution': tc_range_stats.to_dict(),
        'avg_turns': avg_tc,
        'median_turns': median_tc
    }

def analyze_abandonment_by_intent(true_abandoned_df):
    """Analyze abandonment patterns by caller intent"""
    print("\n🎯 ABANDONMENT BY CALLER INTENT")
    print("=" * 60)
    
    intent_col = 'screenPopData.payload.Call_Summary.Caller_Intent'
    
    if intent_col not in true_abandoned_df.columns:
        print("❌ Caller Intent column not found")
        return {}
    
    intent_stats = true_abandoned_df[intent_col].value_counts(dropna=False)
    
    print("Abandonment by Original Intent:")
    print("=" * 35)
    
    total_abandoned = len(true_abandoned_df)
    
    for intent, count in intent_stats.head(10).items():
        percentage = (count / total_abandoned) * 100
        print(f"  {intent}: {count:,} calls ({percentage:.1f}%)")
    
    return intent_stats.to_dict()

def analyze_early_vs_late_abandonment(true_abandoned_df):
    """Analyze early stage vs late stage abandonments"""
    print("\n⏱️ EARLY VS LATE ABANDONMENT ANALYSIS")
    print("=" * 60)
    
    tc_col = 'screenPopData.payload.Call_Summary.TC'
    abandonment_col = 'screenPopData.payload.Call_Summary.Abandonment_Point'
    
    # Convert turn count to numeric
    true_abandoned_df_copy = true_abandoned_df.copy()
    true_abandoned_df_copy['TC_numeric'] = pd.to_numeric(true_abandoned_df_copy[tc_col], errors='coerce')
    
    # Remove NaN values
    tc_clean = true_abandoned_df_copy[true_abandoned_df_copy['TC_numeric'].notna()]
    
    if len(tc_clean) == 0:
        print("❌ No valid turn count data")
        return {}
    
    # Define early vs late abandonment (threshold at 6 turns)
    early_threshold = 6
    
    early_abandonments = tc_clean[tc_clean['TC_numeric'] <= early_threshold]
    late_abandonments = tc_clean[tc_clean['TC_numeric'] > early_threshold]
    
    print(f"Early Abandonments (≤{early_threshold} turns): {len(early_abandonments):,} calls ({len(early_abandonments)/len(tc_clean)*100:.1f}%)")
    print(f"Late Abandonments (>{early_threshold} turns): {len(late_abandonments):,} calls ({len(late_abandonments)/len(tc_clean)*100:.1f}%)")
    
    print(f"\nEarly Abandonment Points:")
    if len(early_abandonments) > 0:
        early_points = early_abandonments[abandonment_col].value_counts()
        for point, count in early_points.head(8).items():
            percentage = (count / len(early_abandonments)) * 100
            print(f"  {point}: {count:,} ({percentage:.1f}%)")
    
    print(f"\nLate Abandonment Points:")
    if len(late_abandonments) > 0:
        late_points = late_abandonments[abandonment_col].value_counts()
        for point, count in late_points.head(8).items():
            percentage = (count / len(late_abandonments)) * 100
            print(f"  {point}: {count:,} ({percentage:.1f}%)")
    
    return {
        'early_count': len(early_abandonments),
        'late_count': len(late_abandonments),
        'early_points': early_points.to_dict() if len(early_abandonments) > 0 else {},
        'late_points': late_points.to_dict() if len(late_abandonments) > 0 else {}
    }

def generate_abandonment_insights(abandonment_stats, milestone_stats, tc_analysis):
    """Generate insights and recommendations based on abandonment analysis"""
    print("\n💡 ABANDONMENT INSIGHTS & RECOMMENDATIONS")
    print("=" * 60)
    
    # Top abandonment points
    if abandonment_stats:
        top_abandonment_point = max(abandonment_stats.items(), key=lambda x: x[1])
        print(f"🚨 TOP ABANDONMENT POINT: {top_abandonment_point[0]} ({top_abandonment_point[1]} calls)")
    
    # Early vs late abandonment insights
    if tc_analysis and 'avg_turns' in tc_analysis:
        avg_turns = tc_analysis['avg_turns']
        if avg_turns < 5:
            print(f"⚡ INSIGHT: Most abandonments occur early (avg {avg_turns:.1f} turns) - likely initial engagement issues")
        elif avg_turns > 8:
            print(f"⏳ INSIGHT: Most abandonments occur late (avg {avg_turns:.1f} turns) - likely process complexity issues")
        else:
            print(f"📊 INSIGHT: Abandonments distributed across call flow (avg {avg_turns:.1f} turns)")
    
    # Generate recommendations based on patterns
    recommendations = []
    
    if abandonment_stats:
        # Check for common abandonment patterns
        if any('Greeting' in point or 'Initial' in point for point in abandonment_stats.keys()):
            recommendations.append("🎯 Optimize initial greeting and menu options")
        
        if any('Verification' in point or 'DOB' in point for point in abandonment_stats.keys()):
            recommendations.append("📋 Streamline patient verification process")
        
        if any('Schedule' in point or 'Appointment' in point for point in abandonment_stats.keys()):
            recommendations.append("📅 Improve scheduling flow efficiency")
        
        if any('Transfer' in point or 'Hold' in point for point in abandonment_stats.keys()):
            recommendations.append("⏱️ Reduce hold times and transfer delays")
    
    print("\n🎯 RECOMMENDED ACTIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    if not recommendations:
        print("  • Analyze top abandonment points for specific optimization opportunities")
        print("  • Focus on early-stage engagement improvements")
        print("  • Review call flow complexity in high-abandonment areas")

def main():
    """Main analysis function"""
    csv_path = "/Users/c1.jlange/Downloads/March workitem.csv"
    
    try:
        # Load data
        df = load_data(csv_path)
        
        # Identify true abandonments
        true_abandoned_df = identify_true_abandonments(df)
        
        if len(true_abandoned_df) == 0:
            print("❌ No true abandoned calls found!")
            return
        
        # Analyze abandonment points
        abandonment_stats = analyze_abandonment_points(true_abandoned_df)
        
        # Analyze milestones at abandonment
        milestone_stats = analyze_milestone_at_abandonment(true_abandoned_df)
        
        # Analyze by turn count
        tc_analysis = analyze_abandonment_by_turn_count(true_abandoned_df)
        
        # Analyze by caller intent
        intent_analysis = analyze_abandonment_by_intent(true_abandoned_df)
        
        # Analyze early vs late abandonment
        early_late_analysis = analyze_early_vs_late_abandonment(true_abandoned_df)
        
        # Generate insights
        generate_abandonment_insights(abandonment_stats, milestone_stats, tc_analysis)
        
        print("\n" + "="*80)
        print("📋 ABANDONMENT POINT SUMMARY")
        print("="*80)
        
        # Save results
        results = {
            'analysis_type': 'abandonment_point_analysis',
            'total_true_abandonments': len(true_abandoned_df),
            'abandonment_points': abandonment_stats,
            'milestones_at_abandonment': milestone_stats,
            'turn_count_analysis': tc_analysis,
            'intent_analysis': intent_analysis,
            'early_late_analysis': early_late_analysis,
            'analysis_date': datetime.now().isoformat()
        }
        
        # Save to JSON
        with open('/Users/c1.jlange/Documents/Cursor/Chord - Cursor/abandonment_point_analysis.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✅ Analysis complete!")
        print(f"📊 Results saved to: abandonment_point_analysis.json")
        
        # Show key summary
        if abandonment_stats:
            top_3 = list(abandonment_stats.items())[:3]
            print(f"\n🎯 TOP 3 ABANDONMENT POINTS:")
            for point, count in top_3:
                percentage = (count / len(true_abandoned_df)) * 100
                print(f"   • {point}: {count:,} calls ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()