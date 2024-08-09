import pymysql
import pandas as pd
import re

# Database connection details
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'toor',
    'database': 'ld_production',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# SQL query to find the required data
query = """
SELECT 
    pm.post_id,
    p.post_title,
    pm.meta_value
FROM 
    wp_y8447ukn8m_postmeta pm
JOIN 
    wp_y8447ukn8m_posts p ON pm.post_id = p.ID
WHERE 
    pm.meta_key = '_elementor_data' 
    AND p.post_status = 'publish'
    AND p.post_type = 'post';
"""

def extract_author_from_meta(meta_value):
    """Extract the author information from the meta_value."""
    match = re.search(r'written by <a [^>]*>([^<]*)</a>', meta_value)
    if match:
        return match.group(1)
    return None

def main():
    # Connect to the database
    connection = pymysql.connect(**db_config)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
        
        # Process the results
        data = []
        for row in results:
            author = extract_author_from_meta(row['meta_value'])
            if author:
                data.append({
                    'post_id': row['post_id'],
                    'post_title': row['post_title'],
                    'author': author
                })
        
        # Convert to a pandas DataFrame
        df = pd.DataFrame(data)
        
        # Debugging: Print the extracted data
        if df.empty:
            print("No matching data found.")
        else:
            print(df)
        
        # Save to a CSV file (optional)
        df.to_csv('author_data.csv', index=False)
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()
