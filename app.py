from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, jsonify
import os
from urllib.parse import urlparse
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
import re
from datetime import datetime

app = Flask(__name__)
# Secret key from env (fallback to "dev-secret" if not set)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')

# MongoDB Atlas connection
MONGODB_URI = os.getenv(
    'MONGODB_URI',
    'mongodb+srv://nirobmahee04_db_user:cropmate123@cluster0.hejrfqd.mongodb.net/DriveX?retryWrites=true&w=majority&appName=Cluster0'
)

try:
    client = MongoClient(MONGODB_URI)
    db = client['DriveX']
    # Test connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

# Collections
users_collection = db['user']
employees_collection = db['employee']
admins_collection = db['admin']
cars_collection = db['cars']
pickup_points_collection = db['pickup_points']

# Create indexes for better performance and uniqueness
try:
    users_collection.create_index("email", unique=True)
    employees_collection.create_index("email", unique=True)
    employees_collection.create_index("employee_id", unique=True)
    admins_collection.create_index("email", unique=True)
    admins_collection.create_index("admin_id", unique=True)
    cars_collection.create_index("carVIN_No", unique=True)
except Exception as e:
    print(f"Index creation note: {e}")

# Initialize default pickup points if they don't exist
def init_default_pickup_points():
    if pickup_points_collection.count_documents({}) == 0:
        default_points = [
            {
                'name': 'DriveX Pickup Point 1',
                'latitude': 23.877,
                'longitude': 90.3228
            },
            {
                'name': 'DriveX Pickup Point 2',
                'latitude': 23.8519,
                'longitude': 90.4081
            }
        ]
        result = pickup_points_collection.insert_many(default_points)
        print(f"Default pickup points initialized! IDs: {[str(id) for id in result.inserted_ids]}")

# Initialize on startup
init_default_pickup_points()

# Helper function to convert ObjectId to string
def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    return obj

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            nid = request.form.get('nid', '').strip()
            password = request.form.get('password', '').strip()
            role = request.form.get('registration_type', '').strip()

            # Validation
            if not all([name, email, nid, password, role]):
                flash('All fields are required!', 'danger')
                return redirect(url_for('register'))

            # Check if email already exists
            if users_collection.find_one({'email': email}) or \
               employees_collection.find_one({'email': email}) or \
               admins_collection.find_one({'email': email}):
                flash('Email already registered! Please use a different email.', 'danger')
                return redirect(url_for('register'))

            password_hash = generate_password_hash(password)

            if role == 'user':
                license = request.form.get('license', '').strip()
                if not license:
                    flash('License number is required for user registration!', 'danger')
                    return redirect(url_for('register'))
                
                user_data = {
                    'name': name,
                    'email': email,
                    'license': license,
                    'nid': nid,
                    'password': password_hash
                }
                users_collection.insert_one(user_data)
                
            elif role == 'employee':
                employee_id = request.form.get('employee_id', '').strip()
                position = request.form.get('e_position', '').strip()
                
                if not all([employee_id, position]):
                    flash('Employee ID and position are required!', 'danger')
                    return redirect(url_for('register'))
                
                # Check if employee_id already exists
                if employees_collection.find_one({'employee_id': employee_id}):
                    flash('Employee ID already exists!', 'danger')
                    return redirect(url_for('register'))
                
                employee_data = {
                    'name': name,
                    'email': email,
                    'employee_id': employee_id,
                    'position': position,
                    'nid': nid,
                    'password': password_hash
                }
                employees_collection.insert_one(employee_data)
                
            elif role == 'admin':
                admin_id = request.form.get('admin_id', '').strip()
                position = request.form.get('a_position', '').strip()
                
                if not all([admin_id, position]):
                    flash('Admin ID and position are required!', 'danger')
                    return redirect(url_for('register'))
                
                # Check if admin_id already exists
                if admins_collection.find_one({'admin_id': admin_id}):
                    flash('Admin ID already exists!', 'danger')
                    return redirect(url_for('register'))
                
                admin_data = {
                    'name': name,
                    'email': email,
                    'admin_id': admin_id,
                    'position': position,
                    'nid': nid,
                    'password': password_hash
                }
                admins_collection.insert_one(admin_data)
            else:
                flash('Invalid registration type!', 'danger')
                return redirect(url_for('register'))
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '').strip()
            role = request.form.get('role', '').strip()

            if not all([email, password, role]):
                flash('All fields are required!', 'danger')
                return redirect(url_for('login'))

            if role == 'user':
                user = users_collection.find_one({'email': email})
                if user and check_password_hash(user['password'], password):
                    session['username'] = user['name']
                    session['user_id'] = str(user['_id'])
                    session['role'] = 'user'
                    flash('Login successful!', 'success')
                    return redirect(url_for('user_dashboard'))
        
            elif role == 'employee':
                employee = employees_collection.find_one({'email': email})
                if employee and check_password_hash(employee['password'], password):
                    session['username'] = employee['name']
                    session['user_id'] = str(employee['_id'])
                    session['role'] = 'employee'
                    flash('Login successful!', 'success')
                    return redirect(url_for('employee_dashboard'))
        
            elif role == 'admin':
                admin = admins_collection.find_one({'email': email})
                if admin and check_password_hash(admin['password'], password):
                    session['username'] = admin['name']
                    session['user_id'] = str(admin['_id'])
                    session['role'] = 'admin'
                    flash('Login successful!', 'success')
                    return redirect(url_for('home'))

            flash('Invalid credentials or role mismatch. Please try again.', 'danger')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')
            return redirect(url_for('login'))
        
    return render_template('login.html')

# Route Page
@app.route('/route', methods=['GET'])
def route():
    username = session.get('username', 'Guest')
    pickup = request.args.get('pickup', '')
    dropoff = request.args.get('dropoff', '')
    
    # Get pickup points (get first two)
    pickup_points = list(pickup_points_collection.find().limit(2))
    pickup_point_1 = pickup_points[0] if len(pickup_points) > 0 else None
    pickup_point_2 = pickup_points[1] if len(pickup_points) > 1 else pickup_points[0] if len(pickup_points) > 0 else None
    
    # Get cars for each pickup point
    cars_point_1 = []
    cars_point_2 = []
    
    if pickup_point_1:
        point_1_id = str(pickup_point_1['_id'])
        cars_point_1 = list(cars_collection.find({'pickup_point_id': point_1_id}))
    
    if pickup_point_2 and pickup_point_2 != pickup_point_1:
        point_2_id = str(pickup_point_2['_id'])
        cars_point_2 = list(cars_collection.find({'pickup_point_id': point_2_id}))
    elif pickup_point_2:
        # If same point, use same cars
        cars_point_2 = cars_point_1.copy()
    
    # Ensure required fields exist and convert ObjectId to string
    for car in cars_point_1 + cars_point_2:
        if not car.get('image_url'):
            car['image_url'] = 'default.jpg'
        if not car.get('description') or car.get('description') == 'No description available':
            # Set better default descriptions based on car name
            car_name_lower = car.get('name', '').lower()
            if 'corolla' in car_name_lower:
                car['description'] = 'Comfortable and reliable sedan perfect for city rides.'
            elif 'noah' in car_name_lower:
                car['description'] = 'Spacious 7-seater van ideal for family trips.'
            elif 'prado' in car_name_lower:
                car['description'] = 'Luxury SUV with premium comfort and style.'
            elif 'prius' in car_name_lower:
                car['description'] = 'Eco-friendly hybrid car with excellent fuel economy.'
            elif 'honda' in car_name_lower or 'hr-v' in car_name_lower:
                car['description'] = 'Compact SUV with modern features and great performance.'
            elif 'nissan' in car_name_lower or 'x-trail' in car_name_lower:
                car['description'] = 'Stylish SUV perfect for both city and highway driving.'
            else:
                car['description'] = 'Premium vehicle with excellent comfort and safety features.'
        
        # Price per km is 25tk, so we'll show that in the template
        # The actual price will be calculated based on distance
        car['price_per_km'] = 25.0
        if car.get('price') is None or car.get('price') == 0:
            car['price'] = 0.0  # Will be calculated dynamically
        
        # Convert ObjectId to string for template
        car['_id'] = str(car['_id'])
        # Ensure pickup_point_id is string
        if 'pickup_point_id' in car:
            car['pickup_point_id'] = str(car['pickup_point_id'])
 
    return render_template('route.html', pickup=pickup, dropoff=dropoff, 
                          cars_point_1=cars_point_1, cars_point_2=cars_point_2, 
                          username=username)

# User dashboard
@app.route('/user_dashboard')
def user_dashboard():
    if 'role' not in session or session.get('role') != 'user':
        flash('Please login to access your dashboard.', 'warning')
        return redirect(url_for('login'))
    
    username = session.get('username', 'Guest')
    return render_template('user_dashboard.html', username=username)

# Wallet page
@app.route('/wallet')
def wallet():
    if 'role' not in session or session.get('role') != 'user':
        flash('Please login to access your wallet.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    username = session.get('username', 'Guest')
    
    # Get wallet transactions
    wallet_collection = db['wallet']
    transactions = list(wallet_collection.find({'user_id': user_id}).sort('created_at', -1).limit(50))
    
    # Calculate total spent (sum of all payment transactions)
    total_balance = sum(abs(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment')
    
    # Convert ObjectId to string for template
    for transaction in transactions:
        transaction['_id'] = str(transaction['_id'])
    
    return render_template('wallet.html', username=username, transactions=transactions, total_balance=total_balance)

# Activity page
@app.route('/activity')
def activity():
    if 'role' not in session or session.get('role') != 'user':
        flash('Please login to view your activity.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    username = session.get('username', 'Guest')
    
    # Get activity records
    activity_collection = db['activity']
    activities = list(activity_collection.find({'user_id': user_id}).sort('created_at', -1).limit(50))
    
    # Convert ObjectId to string for template
    for activity in activities:
        activity['_id'] = str(activity['_id'])
    
    return render_template('activity.html', username=username, activities=activities)

# Help page (placeholder)
@app.route('/help')
def help():
    if 'role' not in session or session.get('role') != 'user':
        flash('Please login to access help.', 'warning')
        return redirect(url_for('login'))
    
    username = session.get('username', 'Guest')
    return render_template('user_dashboard.html', username=username)

# Employee dashboard
@app.route('/employee_dashboard', methods=['GET', 'POST'])
def employee_dashboard():
    if 'role' not in session or session.get('role') != 'employee':
        flash('Please login as an employee to access this page.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        full_url = request.form.get('image_url', '')
        image_name = os.path.basename(urlparse(full_url).path) if full_url else None

        # Handle adding a car
        if action == 'add_car':
            try:
                carVIN_No = request.form.get('carVIN_No', '').strip()
                name = request.form.get('name', '').strip()
                model = request.form.get('model', '').strip()
                capacity = request.form.get('capacity', '').strip()
                color = request.form.get('color', '').strip()
                description = request.form.get('description', '').strip()
                plate_num = request.form.get('plate_num', '').strip()
                price = request.form.get('price', '').strip()
                pickup_point_id = request.form.get('pickup_point_id', '').strip()

                # Validation
                if not all([carVIN_No, name, model, capacity, color, plate_num, price, pickup_point_id]):
                    flash('All required fields must be filled!', 'error')
                    return redirect(url_for('employee_dashboard'))

                # Check if carVIN_No already exists
                if cars_collection.find_one({'carVIN_No': carVIN_No}):
                    flash('Car VIN Number already exists!', 'error')
                    return redirect(url_for('employee_dashboard'))

                # Validate pickup_point_id exists
                try:
                    pickup_point = pickup_points_collection.find_one({'_id': ObjectId(pickup_point_id)})
                    if not pickup_point:
                        flash('Invalid pickup point selected!', 'error')
                        return redirect(url_for('employee_dashboard'))
                except (InvalidId, Exception):
                    flash('Invalid pickup point ID format!', 'error')
                    return redirect(url_for('employee_dashboard'))

                new_car = {
                    'carVIN_No': carVIN_No,
                    'name': name,
                    'model': model,
                    'capacity': int(capacity),
                    'color': color,
                    'description': description,
                    'image_url': image_name if image_name else None,
                    'plate_num': plate_num,
                    'price': float(price),
                    'pickup_point_id': pickup_point_id
                }
                cars_collection.insert_one(new_car)
                flash("Car added successfully!", "success")
            except ValueError as e:
                flash(f"Invalid input: {str(e)}", "error")
            except InvalidId:
                flash("Invalid pickup point ID!", "error")
            except Exception as e:
                flash(f"Failed to add car: {str(e)}", "error")

        # Handle deleting a car
        elif action == 'delete_car':
            try:
                car_id = request.form.get('car_id', '').strip()
                if not car_id:
                    flash("Car ID is required!", "error")
                    return redirect(url_for('employee_dashboard'))
                
                car_to_delete = cars_collection.find_one({'_id': ObjectId(car_id)})
                if car_to_delete:
                    cars_collection.delete_one({'_id': ObjectId(car_id)})
                    flash("Car deleted successfully!", "success")
                else:
                    flash("Car not found.", "error")
            except InvalidId:
                flash("Invalid car ID!", "error")
            except Exception as e:
                flash(f"Failed to delete car: {str(e)}", "error")

    # Fetch all cars for the "View All Cars" section
    cars = list(cars_collection.find())
    # Convert ObjectId to string and add id field for template compatibility
    for car in cars:
        car_id = str(car['_id'])
        car['id'] = car_id  # Add id field for template compatibility
        car['_id'] = car_id  # Also update _id to string
        
        # Get pickup point name
        if 'pickup_point_id' in car and car['pickup_point_id']:
            try:
                pickup_point_id = car['pickup_point_id']
                if isinstance(pickup_point_id, str):
                    pickup_point = pickup_points_collection.find_one({'_id': ObjectId(pickup_point_id)})
                else:
                    pickup_point = pickup_points_collection.find_one({'_id': pickup_point_id})
                
                if pickup_point:
                    car['pickup_point_name'] = pickup_point.get('name', 'Unknown')
                else:
                    car['pickup_point_name'] = 'Unknown'
            except (InvalidId, Exception):
                car['pickup_point_name'] = 'Unknown'
        else:
            car['pickup_point_name'] = 'Unknown'
    
    # Get pickup points for dropdown
    pickup_points = list(pickup_points_collection.find())
    for point in pickup_points:
        point['_id'] = str(point['_id'])
    
    return render_template('employee_dashboard.html', cars=cars, pickup_points=pickup_points)

# Search car route
@app.route('/search_car', methods=['POST'])
def search_car():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if query:
            # Case-insensitive search using regex
            regex_pattern = re.compile(query, re.IGNORECASE)
            cars = list(cars_collection.find({'name': regex_pattern}))
        else:
            cars = list(cars_collection.find())

        # Convert the car data into a list of dictionaries
        car_list = []
        for car in cars:
            car_dict = {
                'id': str(car['_id']),
                'carVIN_No': car.get('carVIN_No', ''),
                'name': car.get('name', ''),
                'model': car.get('model', ''),
                'capacity': car.get('capacity', 0),
                'color': car.get('color', ''),
                'pickup_point_id': str(car.get('pickup_point_id', '')),
            }
            car_list.append(car_dict)

        return jsonify({'cars': car_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

# Select car route
@app.route('/select_car', methods=['POST'])
def select_car():
    if 'role' not in session or session.get('role') != 'user':
        flash('Please login to select a car.', 'warning')
        return redirect(url_for('login'))
    
    try:
        car_id = request.form.get('car_id', '')
        car_name = request.form.get('carName', '')
        car_image = request.form.get('carImage', '')
        plate_num = request.form.get('plate_num', '')
        pickup = request.form.get('pickup', '')
        dropoff = request.form.get('dropoff', '')
        
        # Get car details from database
        if car_id:
            try:
                car = cars_collection.find_one({'_id': ObjectId(car_id)})
                if car:
                    car_name = car.get('name', car_name)
                    car_image = car.get('image_url', car_image) or 'default.jpg'
                    plate_num = car.get('plate_num', plate_num)
            except (InvalidId, Exception) as e:
                print(f"Error fetching car: {e}")
        
        # Store in session
        session['car_id'] = car_id
        session['car_name'] = car_name
        session['car_image'] = car_image
        session['plate_num'] = plate_num
        session['pickup'] = pickup
        session['dropoff'] = dropoff
        
        # Calculate distance using geocoding API (simplified - in production use proper distance calculation)
        # For now, we'll calculate in payment route when we have pickup/dropoff coordinates
        
        return redirect(url_for('payment'))
    except Exception as e:
        flash(f'Error selecting car: {str(e)}', 'danger')
        return redirect(url_for('route'))

# Payment route
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'role' not in session or session.get('role') != 'user':
        flash('Please login to proceed to payment.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handle payment submission
        try:
            # Get form data
            full_name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            address = request.form.get('address', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            zip_code = request.form.get('zip_code', '').strip()
            payment_method = request.form.get('payment_method', '').strip()
            account_holder = request.form.get('account_holder', '').strip()
            account_number = request.form.get('account_number', '').strip()
            
            # Validate required fields
            if not all([full_name, email, address, city, payment_method]):
                flash('Please fill all required fields!', 'danger')
                return redirect(url_for('payment'))
            
            # Process payment (mock payment gateway)
            # In a real scenario, you would integrate with actual payment gateway here
            # For now, we'll simulate a successful payment
            
            # Store booking in database
            booking_data = {
                'user_id': session.get('user_id'),
                'user_email': session.get('username'),
                'car_id': session.get('car_id'),
                'car_name': session.get('car_name'),
                'plate_num': session.get('plate_num'),
                'pickup': session.get('pickup'),
                'dropoff': session.get('dropoff'),
                'distance_km': session.get('distance_km', 0),
                'price': session.get('calculated_price', 0),
                'booking_time': session.get('booking_time'),
                'billing_name': full_name,
                'billing_email': email,
                'billing_address': address,
                'billing_city': city,
                'billing_state': state,
                'billing_zip': zip_code,
                'payment_method': payment_method,
                'account_holder': account_holder,
                'account_number': account_number,
                'status': 'confirmed',
                'created_at': session.get('booking_time')
            }
            
            # Create bookings collection if it doesn't exist
            bookings_collection = db['bookings']
            booking_result = bookings_collection.insert_one(booking_data)
            booking_id = str(booking_result.inserted_id)
            
            # Save to wallet (payment transaction)
            wallet_collection = db['wallet']
            wallet_transaction = {
                'user_id': session.get('user_id'),
                'user_email': session.get('username'),
                'transaction_type': 'payment',
                'amount': session.get('calculated_price', 0),
                'payment_method': payment_method,
                'booking_id': booking_id,
                'description': f'Payment for ride: {session.get("car_name")}',
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            }
            wallet_collection.insert_one(wallet_transaction)
            
            # Save to activity (ride booking)
            activity_collection = db['activity']
            activity_data = {
                'user_id': session.get('user_id'),
                'user_email': session.get('username'),
                'activity_type': 'ride_booking',
                'car_name': session.get('car_name'),
                'plate_num': session.get('plate_num'),
                'pickup': session.get('pickup'),
                'dropoff': session.get('dropoff'),
                'distance_km': session.get('distance_km', 0),
                'price': session.get('calculated_price', 0),
                'booking_time': session.get('booking_time'),
                'status': 'confirmed',
                'booking_id': booking_id,
                'created_at': datetime.now().isoformat()
            }
            activity_collection.insert_one(activity_data)
            
            flash('Payment successful! Your ride has been booked.', 'success')
            
            # Clear session booking data
            session.pop('car_id', None)
            session.pop('car_name', None)
            session.pop('car_image', None)
            session.pop('plate_num', None)
            session.pop('pickup', None)
            session.pop('dropoff', None)
            session.pop('distance_km', None)
            session.pop('calculated_price', None)
            session.pop('booking_time', None)
            
            return redirect(url_for('user_dashboard'))
            
        except Exception as e:
            flash(f'Payment failed: {str(e)}', 'danger')
            return redirect(url_for('payment'))
    
    # GET request - show payment page
    car_name = session.get('car_name', 'Unknown Car')
    car_image = session.get('car_image', 'default.jpg')
    plate_num = session.get('plate_num', 'N/A')
    pickup = session.get('pickup', 'Not specified')
    dropoff = session.get('dropoff', 'Not specified')
    
    # Calculate distance and price if not already calculated
    distance_km = session.get('distance_km')
    calculated_price = session.get('calculated_price')
    
    if not distance_km or not calculated_price:
        # Default values if distance not calculated
        distance_km = 10.0  # Default 10km
        calculated_price = distance_km * 25  # 1km = 25tk
        session['distance_km'] = distance_km
        session['calculated_price'] = calculated_price
    
    # Get booking time
    booking_time = session.get('booking_time')
    if not booking_time:
        booking_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session['booking_time'] = booking_time
    
    return render_template('payment.html', 
                         car_name=car_name, 
                         car_image=car_image, 
                         plate_num=plate_num,
                         pickup=pickup,
                         dropoff=dropoff,
                         distance_km=distance_km,
                         price=calculated_price,
                         booking_time=booking_time)

# Calculate distance API endpoint
@app.route('/calculate_distance', methods=['POST'])
def calculate_distance():
    try:
        data = request.get_json()
        pickup = data.get('pickup', '')
        dropoff = data.get('dropoff', '')
        
        if not pickup or not dropoff:
            return jsonify({'error': 'Pickup and dropoff locations required'}), 400
        
        # Use Nominatim API to get coordinates
        try:
            import requests
        except ImportError:
            return jsonify({'error': 'Requests library not installed'}), 500
        
        # Get pickup coordinates
        pickup_response = requests.get(
            f'https://nominatim.openstreetmap.org/search?format=json&q={pickup}',
            headers={'User-Agent': 'DriveX App'}
        )
        pickup_data = pickup_response.json()
        
        # Get dropoff coordinates
        dropoff_response = requests.get(
            f'https://nominatim.openstreetmap.org/search?format=json&q={dropoff}',
            headers={'User-Agent': 'DriveX App'}
        )
        dropoff_data = dropoff_response.json()
        
        if not pickup_data or not dropoff_data:
            return jsonify({'error': 'Could not find locations'}), 400
        
        pickup_lat = float(pickup_data[0]['lat'])
        pickup_lon = float(pickup_data[0]['lon'])
        dropoff_lat = float(dropoff_data[0]['lat'])
        dropoff_lon = float(dropoff_data[0]['lon'])
        
        # Calculate distance using Haversine formula
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = radians(pickup_lat), radians(pickup_lon)
        lat2, lon2 = radians(dropoff_lat), radians(dropoff_lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance_km = R * c
        
        # Calculate price: 1km = 25tk
        price = distance_km * 25
        
        # Store in session
        session['distance_km'] = round(distance_km, 2)
        session['calculated_price'] = round(price, 2)
        
        return jsonify({
            'distance_km': round(distance_km, 2),
            'price': round(price, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database with default data (optional)
@app.route('/init_db')
def init_db():
    try:
        # Initialize pickup points if needed
        init_default_pickup_points()
        
        # You can add more initialization here if needed
        return "Database initialized successfully!"
    except Exception as e:
        return f"Error initializing database: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
