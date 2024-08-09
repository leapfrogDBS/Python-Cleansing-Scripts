import csv
import mysql.connector

# Database connection details
db_config = {
    'user': 'root',
    'password': 'toor',
    'host': 'localhost',
    'database': 'wp_thelowdown',
    'raise_on_warnings': True,
}

# File paths
map_file_path = 'mapping.csv'
meta_file_path = 'meta.csv'

# Read the mapping CSV
def read_mapping_csv(file_path):
    mapping = {}
    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            prod_post_id = int(row['prod_post_id'])
            dev_post_id = int(row['dev_post_id'])
            mapping[prod_post_id] = dev_post_id
    return mapping

# Read the metadata CSV
def read_meta_csv(file_path):
    metadata = []
    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            metadata.append({
                'post_id': int(row['post_id']),
                'meta_key': row['meta_key'],
                'meta_value': row['meta_value']
            })
    return metadata

# Update metadata in the database
def update_meta_in_db(cursor, post_id, meta_key, meta_value):
    cursor.execute("SELECT meta_value FROM wp_postmeta WHERE post_id = %s AND meta_key = %s", (post_id, meta_key))
    result = cursor.fetchone()
    if result:
        if result[0] != meta_value:
            cursor.execute("UPDATE wp_postmeta SET meta_value = %s WHERE post_id = %s AND meta_key = %s", (meta_value, post_id, meta_key))
            print(f"Updated {meta_key} for post ID {post_id} to {meta_value}")
    else:
        cursor.execute("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, %s, %s)", (post_id, meta_key, meta_value))
        print(f"Inserted {meta_key} for post ID {post_id} with value {meta_value}")

# Main function
def main():
    # Connect to the database
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # Read the CSV files
    mapping = read_mapping_csv(map_file_path)
    metadata = read_meta_csv(meta_file_path)

    # Update metadata in the development database
    for meta in metadata:
        prod_post_id = meta['post_id']
        if prod_post_id in mapping:
            dev_post_id = mapping[prod_post_id]
            update_meta_in_db(cursor, dev_post_id, meta['meta_key'], meta['meta_value'])

    # Commit the changes and close the connection
    cnx.commit()
    cursor.close()
    cnx.close()

if __name__ == "__main__":
    main()
