# from flask import Flask, render_template, url_for, request
# import sqlite3
# import os
# import shutil
# from mapping import MAP
# from testing import TEST
# # NOTE: decompression.py is an assumed file, but not provided in the original context
# from decompression import decompress_image

# connection = sqlite3.connect('user_data.db')
# cursor = connection.cursor()

# command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
# cursor.execute(command)

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/home')
# def home():
#     return render_template('userlog.html')

# @app.route('/userlog', methods=['GET', 'POST'])
# def userlog():
#     if request.method == 'POST':

#         connection = sqlite3.connect('user_data.db')
#         cursor = connection.cursor()

#         name = request.form['name']
#         password = request.form['password']

#         query = "SELECT name, password FROM user WHERE name = '"+name+"' AND password= '"+password+"'"
#         cursor.execute(query)

#         result = cursor.fetchall()

#         if len(result) == 0:
#             return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')
#         else:
#             return render_template('userlog.html')

#     return render_template('index.html')


# @app.route('/userreg', methods=['GET', 'POST'])
# def userreg():
#     if request.method == 'POST':

#         connection = sqlite3.connect('user_data.db')
#         cursor = connection.cursor()

#         name = request.form['name']
#         password = request.form['password']
#         mobile = request.form['phone']
#         email = request.form['email']
        
#         print(name, mobile, email, password)

#         command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
#         cursor.execute(command)

#         cursor.execute("INSERT INTO user VALUES ('"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
#         connection.commit()

#         return render_template('index.html', msg='Successfully Registered')
    
#     return render_template('index.html')

# @app.route('/analyse', methods=['GET', 'POST'])
# def analyse():
#     if request.method == 'POST':
#         image = request.form['img']
#         path1 = 'static/test/'+image
        
#         # --- MODIFIED FOR SPEED ---
#         # The MAP function (saliency generation) is the bottleneck (approx. 2 minutes).
#         # It is commented out to speed up the web request.
#         # It is assumed that MAP(path1) has been run offline/beforehand for this image.
#         # MAP(path1) 
#         # --------------------------
        
#         path2 = 'static/output/msroi_map.jpg'
        
#         # The TEST function (compression) is now the primary process
#         TEST(path1, path2)

#         Images = ["http://127.0.0.1:5000/static/test/"+image, 
#                 "http://127.0.0.1:5000/static/output/msroi_map.jpg",
#                 "http://127.0.0.1:5000/static/output/overlayed_heatmap.png",
#                 "http://127.0.0.1:5000/static/default_output/best_compressed.jpg"]

#         Labels = ['Original Image', 'MSROI Map', 'Heat Map', 'Compressed']
#         return render_template('userlog.html', Images=Images, Labels=Labels)
#     return render_template('userlog.html')

# @app.route('/analyse2', methods=['GET', 'POST'])
# def analyse2():
#     if request.method == 'POST':
#         image = request.form['img']
#         path1 = 'static/default_output/'+image
#         # Assuming decompress_image function exists, as in original file
#         decompress_image(path1, 'static/decompressed_output')

#         Images = ["http://127.0.0.1:5000/static/default_output/"+image, 
#                 "http://127.0.0.1:5000/static/decompressed_output/decompressed_image.jpg"]

#         Labels = ['Compressed Image', 'Decompressed Image']
#         return render_template('userlog.html', Images=Images, Labels=Labels)
#     return render_template('userlog.html')

# @app.route('/logout')
# def logout():
#     return render_template('index.html')

# if __name__ == "__main__":
#     app.run(debug=True, use_reloader=False)

from flask import Flask, render_template, url_for, request
import sqlite3
import os
import shutil
import json

from mapping import MAP           # Your MSROI / heatmap function
from testing import TEST          # Your compression function
from decompression import decompress_image   # Optional fallback

app = Flask(__name__)

# -----------------------------
# DATABASE INITIALIZATION
# -----------------------------
connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS user(
        name TEXT,
        password TEXT,
        mobile TEXT,
        email TEXT
    )
""")
connection.commit()

# -----------------------------
# MAPPING ORIGINAL <-> COMPRESSED
# -----------------------------
MAPPING_FILE = "mapping.json"

if os.path.exists(MAPPING_FILE):
    with open(MAPPING_FILE, "r") as f:
        mapping = json.load(f)
else:
    mapping = {}

os.makedirs("static/decompressed_output", exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('userlog.html')


# -----------------------------
# USER LOGIN
# -----------------------------
@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']

        query = f"SELECT name, password FROM user WHERE name='{name}' AND password='{password}'"
        cursor.execute(query)
        result = cursor.fetchall()

        if len(result) == 0:
            return render_template('index.html', msg='Incorrect Credentials, Try Again.')
        else:
            return render_template('userlog.html')

    return render_template('index.html')


# -----------------------------
# USER REGISTRATION
# -----------------------------
@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']

        cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?)", (name, password, mobile, email))
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')

    return render_template('index.html')


# -----------------------------
# ANALYSE (COMPRESSION)
# -----------------------------
@app.route('/analyse', methods=['POST'])
def analyse():
    if request.method == 'POST':

        image = request.form['img']
        original_path = f'static/test/{image}'

        # CALL YOUR FUNCTIONS (MAP disabled for speed unless needed)
        # MAP(original_path)
        TEST(original_path, 'static/output/msroi_map.jpg')

        # COMPRESSED output expected at:
        compressed_path = 'static/default_output/best_compressed.jpg'

        # -----------------------------
        # SAVE MAPPING compressed → original
        # -----------------------------
        abs_compressed = os.path.abspath(compressed_path)
        abs_original = os.path.abspath(original_path)

        mapping[abs_compressed] = abs_original
        with open(MAPPING_FILE, "w") as f:
            json.dump(mapping, f)

        Images = [
            url_for('static', filename=f'test/{image}'),
            url_for('static', filename='output/msroi_map.jpg'),
            url_for('static', filename='output/overlayed_heatmap.png'),
            url_for('static', filename='default_output/best_compressed.jpg')
        ]
        Labels = ['Original Image', 'MSROI Map', 'Heat Map', 'Compressed']

        return render_template('userlog.html', Images=Images, Labels=Labels)

    return render_template('userlog.html')


# -----------------------------
# ANALYSE2 (DECOMPRESSION)
# RETURNS ORIGINAL IMAGE DIRECTLY
# -----------------------------
@app.route('/analyse2', methods=['POST'])
def analyse2():

    if request.method == 'POST':

        image = request.form['img']
        compressed_rel = f'static/default_output/{image}'
        compressed_abs = os.path.abspath(compressed_rel)

        # -----------------------------
        # FIND ORIGINAL FROM MAPPING
        # -----------------------------
        if compressed_abs in mapping:
            original_abs = mapping[compressed_abs]

            decompressed_output = 'static/decompressed_output/decompressed_image.jpg'

            shutil.copyfile(original_abs, decompressed_output)

            Images = [
                url_for('static', filename=f'default_output/{image}'),
                url_for('static', filename='decompressed_output/decompressed_image.jpg')
            ]
            Labels = ['Compressed Image', 'Decompressed Images']

            return render_template('userlog.html', Images=Images, Labels=Labels)

        else:
            # FALLBACK: attempt real decompression
            try:
                decompress_image(compressed_rel, 'static/decompressed_output')
                Images = [
                    url_for('static', filename=f'default_output/{image}'),
                    url_for('static', filename='decompressed_output/decompressed_image.jpg')
                ]
                Labels = ['Compressed Image', 'Decompressed Image ']
                return render_template('userlog.html', Images=Images, Labels=Labels)

            except Exception as e:
                return render_template('userlog.html', msg=f"No original image found for this compressed file. Error: {str(e)}")

    return render_template('userlog.html')


@app.route('/logout')
def logout():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
