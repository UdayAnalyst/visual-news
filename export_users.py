#!/usr/bin/env python3
"""
Simple script to export user data from users.json to CSV format
Run this locally to get your user data immediately
"""

import json
import csv
from datetime import datetime
import os

def export_users_to_csv():
    """Export user data to CSV file"""
    try:
        # Load users data
        if not os.path.exists('users.json'):
            print("❌ users.json file not found!")
            return
        
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        if not users:
            print("❌ No user data found!")
            return
        
        # Prepare data for CSV
        csv_data = []
        for user_id, user_data in users.items():
            csv_data.append({
                'User ID': user_id,
                'Name': user_data.get('name', 'N/A'),
                'Phone': user_data.get('phone', 'N/A'),
                'Email': user_data.get('email', 'N/A'),
                'Created At': user_data.get('created_at', 'N/A'),
                'Preferences': ', '.join(user_data.get('preferences', [])) if user_data.get('preferences') else 'None',
                'Liked Topics Count': len(user_data.get('liked_topics', {})),
                'Passed Topics Count': len(user_data.get('passed_topics', {})),
                'Total Engagements': len(user_data.get('liked_topics', {})) + len(user_data.get('passed_topics', {}))
            })
        
        # Create CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"visual_news_users_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['User ID', 'Name', 'Phone', 'Email', 'Created At', 'Preferences', 'Liked Topics Count', 'Passed Topics Count', 'Total Engagements']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"✅ User data exported successfully to: {filename}")
        print(f"📊 Total users exported: {len(csv_data)}")
        
        # Display summary
        print("\n📋 User Summary:")
        for i, user in enumerate(csv_data, 1):
            print(f"{i}. {user['Name']} ({user['Phone']}) - {user['Preferences']}")
            
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

if __name__ == "__main__":
    print("🚀 Visual News - User Data Export")
    print("=" * 40)
    export_users_to_csv()
