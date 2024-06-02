from flask import Flask
from flask import abort, redirect, render_template, request, url_for
from flask_caching import Cache, CachedResponse

from datetime import datetime
from db import connection

# Configure Application variables.
config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

# Initialize Flask instance.
app = Flask(__name__, template_folder="templates")

app.config.from_mapping(config)

cache = Cache(app)

# Template filter to format timestamps as human-readable dates
@app.template_filter('date_time')
def date_time(timestamp):
    datetime_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    return datetime_obj.strftime('%A, %B %d, %Y %I:%M %p')


@app.route('/')
@cache.cached(timeout=60, forced_update=True)
def index():
    try:
        # Create a cursor
        cursor = connection.cursor()

        # Execute SQL Statement to fetch all users sorted by creation date.
        cursor.execute("SELECT * FROM users ORDER BY created DESC")

        # Fetch all user data.
        users = cursor.fetchall()
        
        # Close the cursor.
        cursor.close()

        return render_template('index.html', users=users)
    except Exception as e:
        print(e)
        return abort(500)


@app.route('/create_user', methods=["GET", "POST"])
def create_user():

    if request.method == "POST":
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        about = request.form['about']

        sql_query = """INSERT INTO users 
                (username, fullname, email, about, created) VALUES (?, ?, ?, ?, ?)
                """
        try:
            # Create a cursor
            cursor = connection.cursor()

            # Execute SQL Statement to insert a new user.
            cursor.execute(
                sql_query, 
                (username, fullname, email, about, datetime.now())
            )

            # Commit the changes to the database
            connection.commit()
            
            return redirect(url_for('index'))
        except Exception as e:
            print(e)

    return render_template('create_user.html')


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if user_id:
        try:
            # Create a cursor
            cursor = connection.cursor()

            # Execute SQL Statement to fetch a user by ID
            cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

            user = cursor.fetchone()

            if user:
                # Executing delete SQL statement.
                cursor.execute(f"DELETE FROM users WHERE id = {user_id}")

                # Commit the changes to the database
                connection.commit()
            
            return redirect(url_for('index'))
        except Exception as e:
            print(e)

    return abort(404)


def main():
    try:
        # SQL query for creating user table if not exists.
        sql_query = """CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        fullname TEXT NOT NULL,
                        email TEXT NOT NULL,
                        about TEXT NOT NULL,
                        created TEXT NOT NULL
                    );"""

        # Creating a cursor.
        cursor = connection.cursor()

        # Execute SQL Statement to create the user table.
        cursor.execute(sql_query)

        # Commit the changes to the database.
        connection.commit()

        # Run the application.
        app.run()

    except Exception as e:
        print(e)
        return abort(500)
        

if __name__ == "__main__":
    main()
