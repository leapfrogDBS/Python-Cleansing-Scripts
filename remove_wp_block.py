import mysql.connector
import re

def load_patterns_from_file(file_path):
    """
    Load patterns from a file, stripping any surrounding whitespace from each line.
    """
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def remove_content_blocks():
    try:
        # Load patterns from the file
        patterns_to_remove = load_patterns_from_file('patterns.txt')
        print("Patterns loaded from file:")
        for pattern in patterns_to_remove:
            print(pattern)
        
        # Connect to the database
        conn = mysql.connector.connect(
            host='localhost',
            user='wp_thelowdown_user',
            password='eyGfJR8hp7UvyY19',
            database='wp_thelowdown'
        )
        cursor = conn.cursor()

        # Fetch all posts
        cursor.execute("""
            SELECT ID, post_title, post_content
            FROM wp_posts
            WHERE post_status = 'publish'
            AND post_type = 'post'
        """)
        posts = cursor.fetchall()
        
        print(f"Found {len(posts)} posts to process.")

        for post_id, post_title, post_content in posts:
            print(f"Processing post: {post_id} - {post_title}")
            updated_content = post_content
            # Remove each pattern using regex
            for pattern in patterns_to_remove:
                print(f"Applying pattern: {pattern}")
                updated_content = re.sub(pattern, '', updated_content, flags=re.DOTALL)
                if updated_content != post_content:
                    print(f"Pattern matched in post {post_id}")

            if updated_content != post_content:
                # Update the post content in the database
                cursor.execute("UPDATE wp_posts SET post_content = %s WHERE ID = %s", (updated_content, post_id))
                print(f"Updated post {post_id}")

        # Commit the changes
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Run the function
remove_content_blocks()
