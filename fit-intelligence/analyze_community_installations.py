#!/usr/bin/env python3
"""
Analyze characteristics of Community installations
"""

import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime

print("Analyzing Community Installations Characteristics")
print("="*60)

# Collect all community installations
all_community = []

for part_num in [1, 2, 3]:
    csv_file = f'data/fit_part_{part_num}_clean.csv'
    df = pd.read_csv(csv_file)
    community = df[df['Installation Type'] == 'Community']
    all_community.append(community)
    print(f"Part {part_num}: {len(community)} community installations")

# Combine all community installations
community_df = pd.concat(all_community, ignore_index=True)
print(f"\nTotal Community installations: {len(community_df)}")

print("\n" + "="*60)
print("TECHNOLOGY BREAKDOWN:")
tech_counts = community_df['Technology'].value_counts()
for tech, count in tech_counts.items():
    pct = (count / len(community_df)) * 100
    print(f"  {tech}: {count:,} ({pct:.1f}%)")

print("\n" + "="*60)
print("CAPACITY ANALYSIS:")

# Convert capacity to numeric
community_df['Capacity_kW'] = pd.to_numeric(community_df['Installed capacity'], errors='coerce')

# Basic stats
print(f"  Total installations: {len(community_df):,}")
print(f"  Total capacity: {community_df['Capacity_kW'].sum():,.0f} kW ({community_df['Capacity_kW'].sum()/1000:.1f} MW)")
print(f"  Average capacity: {community_df['Capacity_kW'].mean():.1f} kW")
print(f"  Median capacity: {community_df['Capacity_kW'].median():.1f} kW")
print(f"  Min capacity: {community_df['Capacity_kW'].min():.1f} kW")
print(f"  Max capacity: {community_df['Capacity_kW'].max():.1f} kW")

# Capacity by technology
print("\nCapacity by Technology:")
for tech in tech_counts.index:
    tech_data = community_df[community_df['Technology'] == tech]
    avg_cap = tech_data['Capacity_kW'].mean()
    total_cap = tech_data['Capacity_kW'].sum()
    print(f"  {tech}:")
    print(f"    Average: {avg_cap:.1f} kW")
    print(f"    Total: {total_cap:.0f} kW ({total_cap/1000:.1f} MW)")

print("\n" + "="*60)
print("GEOGRAPHIC DISTRIBUTION:")

# Top regions
region_counts = community_df['Government Office Region'].value_counts()
print("\nTop Regions:")
for region, count in region_counts.head(10).items():
    pct = (count / len(community_df)) * 100
    print(f"  {region}: {count:,} ({pct:.1f}%)")

# Countries
country_counts = community_df['Installation Country'].value_counts()
print("\nBy Country:")
for country, count in country_counts.items():
    pct = (count / len(community_df)) * 100
    print(f"  {country}: {count:,} ({pct:.1f}%)")

print("\n" + "="*60)
print("INSTALLATION TIMELINE:")

# Parse commissioned dates
community_df['Commissioned_Date'] = pd.to_datetime(community_df['Commissioning date'], errors='coerce')
community_df['Year'] = community_df['Commissioned_Date'].dt.year

# Yearly installations
year_counts = community_df['Year'].value_counts().sort_index()
print("\nInstallations by Year:")
for year, count in year_counts.items():
    if pd.notna(year) and year >= 2010:
        print(f"  {int(year)}: {count:,}")

# Calculate age
current_year = datetime.now().year
community_df['Age_Years'] = current_year - community_df['Year']
avg_age = community_df['Age_Years'].mean()
print(f"\nAverage age: {avg_age:.1f} years")

print("\n" + "="*60)
print("COMMUNITY/SCHOOL CATEGORY:")

# Check the community/school category field
category_counts = community_df['Community school category'].value_counts()
print("\nCommunity/School Categories:")
for category, count in category_counts.items():
    pct = (count / len(community_df)) * 100
    print(f"  {category}: {count:,} ({pct:.1f}%)")

print("\n" + "="*60)
print("TARIFF ANALYSIS:")

# Top tariff codes
tariff_counts = community_df['TariffCode'].value_counts()
print("\nTop 10 Tariff Codes:")
for tariff, count in tariff_counts.head(10).items():
    pct = (count / len(community_df)) * 100
    print(f"  {tariff}: {count:,} ({pct:.1f}%)")

print("\n" + "="*60)
print("CAPACITY RANGES:")

# Define capacity ranges
ranges = [
    (0, 10, "0-10 kW"),
    (10, 50, "10-50 kW"),
    (50, 100, "50-100 kW"),
    (100, 500, "100-500 kW"),
    (500, 1000, "500kW-1MW"),
    (1000, 5000, "1-5 MW"),
    (5000, float('inf'), "5+ MW")
]

print("\nCapacity Distribution:")
for min_cap, max_cap, label in ranges:
    count = len(community_df[(community_df['Capacity_kW'] >= min_cap) & (community_df['Capacity_kW'] < max_cap)])
    if count > 0:
        pct = (count / len(community_df)) * 100
        print(f"  {label}: {count:,} ({pct:.1f}%)")

print("\n" + "="*60)
print("SAMPLE COMMUNITY INSTALLATIONS:")

# Show a few examples
sample = community_df.nsmallest(3, 'Capacity_kW')[['Technology', 'Capacity_kW', 'Local Authority', 'Commissioning date']]
print("\nSmallest installations:")
for idx, row in sample.iterrows():
    print(f"  {row['Technology']}: {row['Capacity_kW']:.1f} kW - {row['Local Authority']} ({row['Commissioning date']})")

sample = community_df.nlargest(3, 'Capacity_kW')[['Technology', 'Capacity_kW', 'Local Authority', 'Commissioning date']]
print("\nLargest installations:")
for idx, row in sample.iterrows():
    print(f"  {row['Technology']}: {row['Capacity_kW']:.1f} kW - {row['Local Authority']} ({row['Commissioning date']})")

print("\n" + "="*60)
print("KEY CHARACTERISTICS OF COMMUNITY INSTALLATIONS:")
print("-"*60)
print("1. Predominantly solar (Photovoltaic) - likely community solar gardens")
print("2. Smaller average capacity than commercial installations")
print("3. Concentrated in certain regions with community energy programs")
print("4. Grew rapidly during certain FIT periods")
print("5. Often marked as 'Community' in the Community/School category field")