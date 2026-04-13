#!/usr/bin/env python3
"""
March 2026 Call Data Analysis Script
Processes Kibana CSV export to generate comprehensive call summary metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import re
from collections import Counter

def load_and_clean_data(csv_path):
    """Load CSV data and perform initial cleaning"""
    print("Loading CSV data...")
    df = pd.read_csv(csv_path, low_memory=False)
    
    print(f"Total records loaded: {len(df)}")
    print(f"Columns available: {len(df.columns)}")
    
    # Convert createdTime to datetime - handle Kibana format "Mar 31, 2026 @ 20:03:56.136"
    def parse_kibana_date(date_str):
        if pd.isna(date_str):
            return pd.NaT
        try:
            # Remove @ symbol and parse
            clean_date = date_str.replace(' @ ', ' ')
            return pd.to_datetime(clean_date, format='%b %d, %Y %H:%M:%S.%f')
        except:
            try:
                return pd.to_datetime(clean_date)
            except:
                return pd.NaT
    
    df['createdTime'] = df['createdTime'].apply(parse_kibana_date)
    
    # Convert duration to numeric (seconds)
    df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
    
    return df

def analyze_call_volume(df):
    """Analyze call volume patterns"""
    print("\n📊 CALL VOLUME ANALYSIS")
    print("=" * 50)
    
    # Basic stats
    total_calls = len(df)
    print(f"Total Calls: {total_calls:,}")
    
    # Date range
    start_date = df['createdTime'].min()
    end_date = df['createdTime'].max()
    print(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Daily distribution
    df['date'] = df['createdTime'].dt.date
    daily_calls = df.groupby('date').size()
    
    print(f"Average Calls per Day: {daily_calls.mean():.1f}")
    print(f"Peak Day: {daily_calls.idxmax()} ({daily_calls.max()} calls)")
    print(f"Lowest Day: {daily_calls.idxmin()} ({daily_calls.min()} calls)")
    
    # Hourly patterns
    df['hour'] = df['createdTime'].dt.hour
    hourly_calls = df.groupby('hour').size()
    
    print(f"Peak Hour: {hourly_calls.idxmax()}:00 ({hourly_calls.max()} calls)")
    print(f"Lowest Hour: {hourly_calls.idxmin()}:00 ({hourly_calls.min()} calls)")
    
    # Weekly patterns
    df['weekday'] = df['createdTime'].dt.day_name()
    weekly_calls = df.groupby('weekday').size()
    
    print("\nWeekly Distribution:")
    for day, count in weekly_calls.items():
        print(f"  {day}: {count:,} calls")
    
    return {
        'total_calls': total_calls,
        'daily_average': daily_calls.mean(),
        'peak_day': (daily_calls.idxmax(), daily_calls.max()),
        'lowest_day': (daily_calls.idxmin(), daily_calls.min()),
        'peak_hour': (hourly_calls.idxmax(), hourly_calls.max()),
        'weekly_distribution': weekly_calls.to_dict()
    }

def analyze_agent_performance(df):
    """Analyze AI agent vs human assistance patterns"""
    print("\n🤖 AGENT PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    # Agent assistance breakdown
    agent_stats = df['agentAssisted'].value_counts()
    
    print("Agent Assistance Breakdown:")
    for status, count in agent_stats.items():
        percentage = (count / len(df)) * 100
        print(f"  {status}: {count:,} calls ({percentage:.1f}%)")
    
    # Current state analysis
    state_stats = df['currentState'].value_counts()
    
    print("\nCall State Distribution:")
    for state, count in state_stats.items():
        percentage = (count / len(df)) * 100
        print(f"  {state}: {count:,} calls ({percentage:.1f}%)")
    
    return {
        'agent_assisted': agent_stats.to_dict(),
        'call_states': state_stats.to_dict()
    }

def analyze_call_duration(df):
    """Analyze call duration patterns"""
    print("\n⏱️ CALL DURATION ANALYSIS")
    print("=" * 50)
    
    # Clean duration data (remove nulls)
    valid_durations = df[df['duration'].notna()]['duration']
    
    # Convert to minutes for readability
    duration_minutes = valid_durations / 60
    
    print(f"Calls with duration data: {len(valid_durations):,}")
    print(f"Average Duration: {duration_minutes.mean():.2f} minutes")
    print(f"Median Duration: {duration_minutes.median():.2f} minutes")
    print(f"Longest Call: {duration_minutes.max():.2f} minutes")
    print(f"Shortest Call: {valid_durations.min():.1f} seconds")
    
    # Duration ranges
    bins = [0, 60, 180, 300, 600, float('inf')]
    labels = ['0-1 min', '1-3 min', '3-5 min', '5-10 min', '10+ min']
    df_temp = df[df['duration'].notna()].copy()
    df_temp['duration_range'] = pd.cut(df_temp['duration'], bins=bins, labels=labels, right=False)
    
    duration_dist = df_temp['duration_range'].value_counts()
    
    print("\nDuration Distribution:")
    for range_name, count in duration_dist.items():
        percentage = (count / len(df_temp)) * 100
        print(f"  {range_name}: {count:,} calls ({percentage:.1f}%)")
    
    return {
        'total_with_duration': len(valid_durations),
        'avg_minutes': duration_minutes.mean(),
        'median_minutes': duration_minutes.median(),
        'max_minutes': duration_minutes.max(),
        'min_seconds': valid_durations.min(),
        'duration_distribution': duration_dist.to_dict()
    }

def analyze_locations(df):
    """Analyze location-based performance"""
    print("\n🏥 LOCATION ANALYSIS")
    print("=" * 50)
    
    # Extract location data from UUI field
    uui_pattern = r'\|(\d+)\|'
    
    if 'screenPopData.passthroughSIPHeaders.uui' in df.columns:
        df['location_id'] = df['screenPopData.passthroughSIPHeaders.uui'].str.extract(uui_pattern)
        
        location_stats = df['location_id'].value_counts()
        
        print("Location Performance:")
        for location, count in location_stats.head(10).items():
            percentage = (count / len(df)) * 100
            
            # Calculate average duration for this location
            location_durations = df[
                (df['location_id'] == location) & 
                (df['duration'].notna())
            ]['duration']
            
            avg_duration = location_durations.mean() / 60 if len(location_durations) > 0 else 0
            
            print(f"  Location {location}: {count:,} calls ({percentage:.1f}%) - Avg Duration: {avg_duration:.2f} min")
        
        return location_stats.to_dict()
    else:
        print("Location data not available in current format")
        return {}

def analyze_caller_patterns(df):
    """Analyze caller behavior patterns"""
    print("\n📱 CALLER BEHAVIOR ANALYSIS")
    print("=" * 50)
    
    caller_col = 'screenPopData.passthroughSIPHeaders.variable_caller_id_number'
    
    if caller_col in df.columns:
        # Clean caller ID data
        df_clean = df[df[caller_col].notna()].copy()
        
        unique_callers = df_clean[caller_col].nunique()
        total_calls_with_callerid = len(df_clean)
        
        print(f"Unique Callers: {unique_callers:,}")
        print(f"Calls with Caller ID: {total_calls_with_callerid:,}")
        
        # Repeat caller analysis
        caller_frequency = df_clean[caller_col].value_counts()
        repeat_callers = caller_frequency[caller_frequency > 1]
        
        print(f"Repeat Callers: {len(repeat_callers):,}")
        print(f"Single-call Callers: {len(caller_frequency[caller_frequency == 1]):,}")
        
        if len(repeat_callers) > 0:
            print(f"Most Frequent Caller: {repeat_callers.iloc[0]} calls")
            print(f"Average Calls per Repeat Caller: {repeat_callers.mean():.1f}")
        
        return {
            'unique_callers': unique_callers,
            'repeat_callers': len(repeat_callers),
            'single_call_callers': len(caller_frequency[caller_frequency == 1])
        }
    else:
        print("Caller ID data not available")
        return {}

def generate_weekly_breakdown(df):
    """Generate weekly call breakdown"""
    print("\n📅 WEEKLY BREAKDOWN")
    print("=" * 50)
    
    df['week'] = df['createdTime'].dt.isocalendar().week
    df['week_start'] = df['createdTime'].dt.to_period('W').dt.start_time
    
    weekly_stats = df.groupby('week_start').agg({
        'conversationId': 'count',
        'duration': ['mean', 'count']
    }).round(2)
    
    weekly_stats.columns = ['Total_Calls', 'Avg_Duration_Sec', 'Calls_With_Duration']
    
    print("Weekly Performance:")
    for week_start, row in weekly_stats.iterrows():
        week_end = week_start + timedelta(days=6)
        avg_duration_min = row['Avg_Duration_Sec'] / 60 if pd.notna(row['Avg_Duration_Sec']) else 0
        print(f"  {week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}: {int(row['Total_Calls'])} calls, Avg Duration: {avg_duration_min:.2f} min")
    
    return weekly_stats

def main():
    """Main analysis function"""
    csv_path = "/Users/c1.jlange/Downloads/March workitem.csv"
    
    try:
        # Load data
        df = load_and_clean_data(csv_path)
        
        # Run all analyses
        volume_stats = analyze_call_volume(df)
        agent_stats = analyze_agent_performance(df)
        duration_stats = analyze_call_duration(df)
        location_stats = analyze_locations(df)
        caller_stats = analyze_caller_patterns(df)
        weekly_stats = generate_weekly_breakdown(df)
        
        # Generate summary report
        print("\n" + "="*60)
        print("📋 MARCH 2026 CALL SUMMARY REPORT")
        print("="*60)
        
        print(f"""
🎯 KEY METRICS:
   • Total Calls: {volume_stats['total_calls']:,}
   • Daily Average: {volume_stats['daily_average']:.1f}
   • Peak Day: {volume_stats['peak_day'][0]} ({volume_stats['peak_day'][1]} calls)
   • Peak Hour: {volume_stats['peak_hour'][0]}:00 ({volume_stats['peak_hour'][1]} calls)
   • Average Duration: {duration_stats['avg_minutes']:.2f} minutes
        """)
        
        # Save results to JSON for report integration
        results = {
            'volume_stats': volume_stats,
            'agent_stats': agent_stats,
            'duration_stats': duration_stats,
            'location_stats': location_stats,
            'caller_stats': caller_stats,
            'generated_at': datetime.now().isoformat()
        }
        
        with open('/Users/c1.jlange/Documents/Cursor/Chord - Cursor/march_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print("\n✅ Analysis complete! Results saved to march_analysis_results.json")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find CSV file at {csv_path}")
        print("Please verify the file path is correct.")
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        print("Please check the data format and try again.")

if __name__ == "__main__":
    main()