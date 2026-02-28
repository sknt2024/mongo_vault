from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT, GEO2D
from datetime import datetime, timedelta
import random
import uuid
import string
import time
from tqdm import tqdm
import numpy as np

# ── ANSI colour helpers ────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    # Foreground
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"

def step(n, label):
    """Bold cyan step header."""
    print(f"\n{C.BOLD}{C.CYAN}{'═'*70}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  📦 STEP {n}: {label}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═'*70}{C.RESET}")

def ok(label, count):
    """Indented green success line."""
    print(f"  {C.GREEN}✔  {C.WHITE}{label:<30}{C.RESET} {C.BOLD}{C.GREEN}{count:>12,}{C.RESET} {C.GRAY}docs{C.RESET}")

def info(msg):
    """Indented dim info line."""
    print(f"  {C.GRAY}→  {msg}{C.RESET}")

def warn(msg):
    print(f"  {C.YELLOW}⚠  {msg}{C.RESET}")

def err(msg):
    print(f"\n{C.RED}✖  {msg}{C.RESET}")

def bar(desc, total, color_code=C.CYAN):
    """Return a tqdm bar with consistent indented style."""
    return tqdm(
        total=total,
        desc=f"  {color_code}{desc}{C.RESET}",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        colour=None,
        ncols=90,
    )
# ──────────────────────────────────────────────────────────────────────────────

# MongoDB connection
def get_database():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['ecommerce_massive_db']
    return db

class MassiveDataGenerator:
    def __init__(self, db):
        self.db = db
        self.batch_size = 1000  # Insert in batches for performance
        self.total_target = 100000  # Target 100K per collection
        
        # Pre-generated data pools for realistic relationships
        self.first_names = ['John', 'Emma', 'Michael', 'Sophia', 'William', 'Olivia', 'James', 'Ava', 
                           'Robert', 'Isabella', 'David', 'Mia', 'Richard', 'Charlotte', 'Joseph', 'Amelia',
                           'Thomas', 'Harper', 'Charles', 'Evelyn', 'Christopher', 'Abigail', 'Daniel', 'Emily',
                           'Matthew', 'Elizabeth', 'Anthony', 'Sofia', 'Donald', 'Avery', 'Mark', 'Ella',
                           'Paul', 'Madison', 'Steven', 'Scarlett', 'Andrew', 'Victoria', 'Kenneth', 'Aria',
                           'Joshua', 'Grace', 'Kevin', 'Chloe', 'Brian', 'Camila', 'George', 'Penelope',
                           'Edward', 'Riley', 'Ronald', 'Layla', 'Timothy', 'Lillian', 'Jason', 'Nora',
                           'Jeffrey', 'Zoey', 'Ryan', 'Mila', 'Jacob', 'Hannah', 'Gary', 'Lily']
        
        self.last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                          'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                          'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
                          'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
                          'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
                          'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
                          'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
                          'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy']
        
        self.domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'protonmail.com',
                       'mail.com', 'gmx.com', 'yandex.com', 'icloud.com', 'inbox.com', 'zoho.com']
        
        self.cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio',
                      'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville', 'Fort Worth', 'Columbus',
                      'Charlotte', 'San Francisco', 'Indianapolis', 'Seattle', 'Denver', 'Washington', 'Boston',
                      'El Paso', 'Nashville', 'Detroit', 'Oklahoma City', 'Portland', 'Las Vegas', 'Memphis',
                      'Louisville', 'Baltimore', 'Milwaukee', 'Albuquerque', 'Tucson', 'Fresno', 'Sacramento',
                      'Kansas City', 'Long Beach', 'Mesa', 'Atlanta', 'Colorado Springs', 'Virginia Beach',
                      'Raleigh', 'Omaha', 'Miami', 'Oakland', 'Minneapolis', 'Tulsa', 'Wichita', 'New Orleans']
        
        self.states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN',
                      'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV',
                      'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN',
                      'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
        
        self.countries = ['USA', 'Canada', 'Mexico', 'UK', 'Germany', 'France', 'Italy', 'Spain', 'Australia',
                         'Japan', 'China', 'India', 'Brazil', 'Argentina', 'South Africa', 'Egypt', 'Nigeria',
                         'Russia', 'Turkey', 'Saudi Arabia', 'UAE', 'Singapore', 'Malaysia', 'Thailand',
                         'Vietnam', 'Philippines', 'Indonesia', 'Pakistan', 'Bangladesh', 'Sri Lanka']
        
        self.product_names = {
            'Electronics': ['Smartphone', 'Laptop', 'Tablet', 'Smart Watch', 'Headphones', 'Speaker', 'Camera',
                           'Monitor', 'Keyboard', 'Mouse', 'Printer', 'Scanner', 'Router', 'Drone', 'VR Headset',
                           'Gaming Console', 'TV', 'Projector', 'E-Reader', 'Fitness Tracker'],
            'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Dress', 'Shoes', 'Sweater', 'Shorts', 'Skirt', 'Blouse',
                        'Socks', 'Underwear', 'Swimsuit', 'Pajamas', 'Suit', 'Tie', 'Hat', 'Scarf', 'Gloves',
                        'Belt', 'Handbag'],
            'Home & Garden': ['Sofa', 'Table', 'Chair', 'Bed', 'Lamp', 'Curtains', 'Rug', 'Pillow', 'Blanket',
                             'Towels', 'Cookware', 'Cutlery', 'Plates', 'Glasses', 'Plant Pot', 'Garden Tools',
                             'Hose', 'Lawn Mower', 'Grill', 'Outdoor Furniture'],
            'Books': ['Fiction Novel', 'Non-Fiction', 'Textbook', 'Cookbook', 'Biography', 'History Book',
                     'Science Book', 'Art Book', 'Children Book', 'Comic Book', 'Magazine', 'Dictionary',
                     'Encyclopedia', 'Poetry', 'Self-Help', 'Business Book', 'Travel Guide', 'Religious Book',
                     'Technical Manual', 'Study Guide'],
            'Sports': ['Yoga Mat', 'Dumbbells', 'Treadmill', 'Bicycle', 'Football', 'Basketball', 'Tennis Racket',
                      'Golf Clubs', 'Swimming Goggles', 'Hiking Boots', 'Tent', 'Sleeping Bag', 'Fishing Rod',
                      'Ski Equipment', 'Skateboard', 'Boxing Gloves', 'Jump Rope', 'Resistance Bands', 'Kettlebell',
                      'Exercise Ball'],
            'Toys': ['Action Figure', 'Doll', 'Board Game', 'Puzzle', 'Lego Set', 'Remote Control Car',
                    'Stuffed Animal', 'Toy Train', 'Play-Doh', 'Art Set', 'Educational Toy', 'Science Kit',
                    'Musical Toy', 'Outdoor Toy', 'Water Gun', 'Kite', 'Yo-Yo', 'Slime', 'Card Game', 'Video Game']
        }
        
        self.brands = ['Apple', 'Samsung', 'Sony', 'Microsoft', 'Google', 'Amazon', 'LG', 'Panasonic', 'Philips',
                      'Bose', 'Canon', 'Nikon', 'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'Intel', 'AMD',
                      'Nike', 'Adidas', 'Puma', 'Reebok', 'Under Armour', 'Levi\'s', 'Zara', 'H&M', 'Gap', 'Calvin Klein',
                      'Tommy Hilfiger', 'Ralph Lauren', 'Gucci', 'Prada', 'Versace', 'Armani', 'Dior', 'Chanel',
                      'LEGO', 'Mattel', 'Hasbro', 'Fisher-Price', 'Nintendo', 'Sega', 'Sony PlayStation', 'Xbox']
        
        # We'll store references to generated data for relationships
        self.user_ids = []
        self.product_ids = []
        self.category_ids = []
        self.brand_ids = []
        self.order_ids = []
        
    def generate_users_chunk(self, chunk_size):
        """Generate a chunk of users"""
        users = []
        for _ in range(chunk_size):
            first = random.choice(self.first_names)
            last = random.choice(self.last_names)
            user_id = str(uuid.uuid4())
            self.user_ids.append(user_id)  # Store for relationships
            
            # Use random.choices for weighted selection instead of choice with p parameter
            account_types = ['standard', 'premium', 'vip']
            account_weights = [0.7, 0.2, 0.1]
            
            user = {
                '_id': user_id,
                'username': f"{first.lower()}.{last.lower()}.{uuid.uuid4().hex[:6]}",
                'email': f"{first.lower()}.{last.lower()}.{uuid.uuid4().hex[:6]}@{random.choice(self.domains)}",
                'password_hash': f"hash_{uuid.uuid4().hex[:16]}",
                'first_name': first,
                'last_name': last,
                'phone': f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}",
                'is_active': random.random() > 0.1,  # 90% active
                'is_verified': random.random() > 0.2,  # 80% verified
                'account_type': random.choices(account_types, weights=account_weights)[0],
                'created_at': datetime.now() - timedelta(days=random.randint(1, 1095)),  # Up to 3 years old
                'last_login': datetime.now() - timedelta(days=random.randint(0, 90)),
                'login_count': random.randint(1, 1000),
                'loyalty_points': random.randint(0, 50000),
                'referred_by': random.choice(self.user_ids) if self.user_ids and random.random() > 0.7 else None,
                'metadata': {
                    'signup_ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                    'signup_device': random.choice(['mobile', 'desktop', 'tablet']),
                    'signup_browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                    'marketing_consent': random.random() > 0.3,
                    'data_consent': random.random() > 0.2
                }
            }
            users.append(user)
        return users

    def generate_user_profiles_chunk(self, chunk_size, users):
        """Generate user profiles based on existing users"""
        profiles = []
        for user in users[:chunk_size]:  # Use existing users
            profile = {
                '_id': str(uuid.uuid4()),
                'user_id': user['_id'],
                'bio': f"User bio {random.randint(1,10000)}" if random.random() > 0.3 else None,
                'birth_date': datetime.now() - timedelta(days=random.randint(6570, 29200)),  # 18-80 years old
                'gender': random.choice(['M', 'F', 'non-binary', 'prefer-not-to-say']),
                'marital_status': random.choice(['single', 'married', 'divorced', 'widowed']),
                'occupation': random.choice(['Engineer', 'Teacher', 'Doctor', 'Artist', 'Student', 'Retired', 'Other']),
                'company': f"Company {random.randint(1,1000)}" if random.random() > 0.5 else None,
                'annual_income': random.choice([25000, 50000, 75000, 100000, 150000, 200000, None]),
                'education_level': random.choice(['High School', 'Bachelor', 'Master', 'PhD', 'Other']),
                'interests': random.sample(['Tech', 'Fashion', 'Sports', 'Books', 'Travel', 'Food', 'Gaming'], k=random.randint(2,5)),
                'profile_picture': f"profile_{random.randint(1,10000)}.jpg" if random.random() > 0.2 else None,
                'cover_photo': f"cover_{random.randint(1,10000)}.jpg" if random.random() > 0.5 else None,
                'social_links': {
                    'facebook': f"user{random.randint(1,100000)}" if random.random() > 0.5 else None,
                    'twitter': f"@user{random.randint(1,100000)}" if random.random() > 0.5 else None,
                    'instagram': f"user{random.randint(1,100000)}" if random.random() > 0.5 else None,
                    'linkedin': f"user{random.randint(1,100000)}" if random.random() > 0.3 else None
                },
                'preferred_language': random.choice(['en', 'es', 'fr', 'de', 'zh', 'ja']),
                'timezone': random.choice(['EST', 'PST', 'CST', 'MST', 'GMT', 'CET', 'IST']),
                'notification_preferences': {
                    'email': random.random() > 0.2,
                    'sms': random.random() > 0.5,
                    'push': random.random() > 0.3,
                    'marketing': random.random() > 0.4
                },
                'privacy_settings': {
                    'profile_visible': random.random() > 0.1,
                    'activity_visible': random.random() > 0.3,
                    'email_visible': random.random() > 0.8
                },
                'updated_at': datetime.now()
            }
            profiles.append(profile)
        return profiles

    def generate_addresses_chunk(self, chunk_size, users):
        """Generate addresses for users"""
        addresses = []
        for _ in range(chunk_size):
            user = random.choice(users)
            addr_id = str(uuid.uuid4())
            address = {
                '_id': addr_id,
                'user_id': user['_id'],
                'address_type': random.choice(['shipping', 'billing', 'both']),
                'is_default': random.random() > 0.7,  # 30% chance of being default
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'street_address': f"{random.randint(1,9999)} {random.choice(['Main', 'Oak', 'Pine', 'Maple', 'Cedar', 'Elm', 'Washington', 'Lincoln'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr', 'Ln', 'Rd'])}",
                'street_address2': f"Apt {random.randint(1,999)}" if random.random() > 0.5 else None,
                'city': random.choice(self.cities),
                'state': random.choice(self.states),
                'postal_code': f"{random.randint(10000,99999)}",
                'country': random.choice(self.countries),
                'phone': f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}",
                'delivery_instructions': random.choice(['Leave at door', 'Call on arrival', 'Ring bell', 'None']),
                'is_residential': random.random() > 0.2,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 730)),
                'updated_at': datetime.now()
            }
            addresses.append(address)
        return addresses

    def generate_payment_methods_chunk(self, chunk_size, users):
        """Generate payment methods for users"""
        payment_methods = []
        card_types = ['Visa', 'Mastercard', 'American Express', 'Discover']
        
        for _ in range(chunk_size):
            user = random.choice(users)
            card_type = random.choice(card_types)
            
            payment = {
                '_id': str(uuid.uuid4()),
                'user_id': user['_id'],
                'method_type': random.choice(['credit_card', 'debit_card', 'paypal', 'bank_account']),
                'is_default': random.random() > 0.7,
                'card_type': card_type if random.random() > 0.3 else None,
                'card_last4': f"{random.randint(1000,9999)}",
                'card_expiry': f"{random.randint(1,12)}/{random.randint(25,30)}" if random.random() > 0.3 else None,
                'card_holder_name': f"{user['first_name']} {user['last_name']}" if random.random() > 0.3 else None,
                'billing_address_id': None,  # Will be linked to address
                'paypal_email': f"{user['email']}" if random.random() > 0.7 else None,
                'bank_name': f"Bank of {random.choice(['America', 'Chase', 'Wells Fargo', 'Citibank'])}" if random.random() > 0.7 else None,
                'account_last4': f"{random.randint(1000,9999)}" if random.random() > 0.7 else None,
                'routing_number': f"{random.randint(100000000,999999999)}" if random.random() > 0.7 else None,
                'is_verified': random.random() > 0.2,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            payment_methods.append(payment)
        return payment_methods

    def generate_categories_chunk(self, chunk_size):
        """Generate product categories"""
        categories = []
        main_categories = list(self.product_names.keys())
        
        for i in range(chunk_size):
            main_cat = random.choice(main_categories)
            cat_id = str(uuid.uuid4())
            self.category_ids.append(cat_id)
            
            category = {
                '_id': cat_id,
                'name': f"{main_cat} {random.choice(['Premium', 'Budget', 'Standard', 'Pro', 'Basic'])}",
                'slug': f"{main_cat.lower().replace(' ', '-')}-{uuid.uuid4().hex[:8]}",
                'description': f"High-quality {main_cat.lower()} products at great prices",
                'parent_id': random.choice(self.category_ids) if self.category_ids and random.random() > 0.5 else None,
                'level': random.randint(0, 3),
                'image_url': f"https://example.com/categories/cat_{i}.jpg",
                'icon_url': f"https://example.com/icons/icon_{i}.svg",
                'meta_title': f"Buy {main_cat} Online",
                'meta_description': f"Shop the best {main_cat} products",
                'meta_keywords': f"{main_cat}, shopping, online, ecommerce",
                'sort_order': random.randint(1, 100),
                'is_active': random.random() > 0.05,
                'is_featured': random.random() > 0.7,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 1095)),
                'updated_at': datetime.now()
            }
            categories.append(category)
        return categories

    def generate_brands_chunk(self, chunk_size):
        """Generate product brands"""
        brands = []
        brand_names = self.brands.copy()
        
        for i in range(chunk_size):
            brand_name = random.choice(brand_names) + f" {i}" if i >= len(brand_names) else random.choice(brand_names)
            brand_id = str(uuid.uuid4())
            self.brand_ids.append(brand_id)
            
            brand = {
                '_id': brand_id,
                'name': brand_name,
                'slug': f"{brand_name.lower().replace(' ', '-').replace(chr(39), '')}-{uuid.uuid4().hex[:6]}",
                'description': f"Official {brand_name} products and accessories",
                'logo_url': f"https://example.com/brands/{brand_name.lower().replace(' ', '')}.png",
                'website_url': f"https://www.{brand_name.lower().replace(' ', '')}.com",
                'facebook_url': f"https://facebook.com/{brand_name.lower().replace(' ', '')}" if random.random() > 0.3 else None,
                'twitter_url': f"https://twitter.com/{brand_name.lower().replace(' ', '')}" if random.random() > 0.3 else None,
                'instagram_url': f"https://instagram.com/{brand_name.lower().replace(' ', '')}" if random.random() > 0.3 else None,
                'founded_year': random.randint(1900, 2020),
                'headquarters_city': random.choice(self.cities),
                'headquarters_country': random.choice(['USA', 'UK', 'Germany', 'Japan', 'China', 'France']),
                'is_active': random.random() > 0.1,
                'is_premium': random.random() > 0.7,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 3650)),
                'updated_at': datetime.now()
            }
            brands.append(brand)
        return brands

    def generate_products_chunk(self, chunk_size, categories, brands):
        """Generate products"""
        products = []
        
        for _ in range(chunk_size):
            category = random.choice(categories)
            brand = random.choice(brands)
            main_cat = category['name'].split()[0]  # Extract main category name
            
            # Handle case where main_cat might not be in product_names
            if main_cat in self.product_names:
                product_name_choice = random.choice(self.product_names[main_cat])
            else:
                product_name_choice = random.choice(['Product', 'Item', 'Goods'])
                
            product_name = f"{brand['name']} {product_name_choice} {random.randint(1,1000)}"
            
            product_id = str(uuid.uuid4())
            self.product_ids.append(product_id)
            
            cost_price = round(random.uniform(5, 500), 2)
            retail_price = round(cost_price * random.uniform(1.2, 2.5), 2)
            sale_price = round(retail_price * random.uniform(0.5, 0.95), 2) if random.random() > 0.7 else None
            
            product = {
                '_id': product_id,
                'sku': f"SKU-{uuid.uuid4().hex[:10].upper()}",
                'upc': f"{random.randint(100000000000,999999999999)}",
                'ean': f"{random.randint(1000000000000,9999999999999)}",
                'isbn': f"{random.randint(1000000000,9999999999)}" if random.random() > 0.7 else None,
                'name': product_name,
                'slug': product_name.lower().replace(' ', '-').replace("'", ""),
                'description': f"Experience premium quality with this {product_name}. Perfect for everyday use.",
                'short_description': f"High-quality {product_name}",
                'features': [f"Feature {j}" for j in range(random.randint(3, 8))],
                'specifications': {
                    'color': random.choice(['Black', 'White', 'Silver', 'Gold', 'Red', 'Blue', 'Green']),
                    'weight': f"{random.uniform(0.1, 10):.2f} kg",
                    'dimensions': f"{random.uniform(5, 100):.1f} x {random.uniform(5, 100):.1f} x {random.uniform(1, 50):.1f} cm",
                    'material': random.choice(['Plastic', 'Metal', 'Wood', 'Glass', 'Fabric', 'Leather']),
                    'warranty': f"{random.choice([1,2,3,5])} years"
                },
                'category_id': category['_id'],
                'brand_id': brand['_id'],
                'cost_price': cost_price,
                'retail_price': retail_price,
                'sale_price': sale_price,
                'currency': 'USD',
                'tax_rate': random.choice([0, 5, 8, 10, 15, 20]),
                'is_taxable': random.random() > 0.1,
                'in_stock': random.random() > 0.2,
                'stock_quantity': random.randint(0, 1000),
                'low_stock_threshold': random.randint(5, 50),
                'allow_backorders': random.random() > 0.7,
                'max_order_quantity': random.randint(5, 20),
                'min_order_quantity': random.randint(1, 3),
                'weight_kg': round(random.uniform(0.1, 20), 2),
                'length_cm': random.uniform(5, 100),
                'width_cm': random.uniform(5, 100),
                'height_cm': random.uniform(1, 50),
                'requires_shipping': random.random() > 0.1,
                'is_digital': random.random() > 0.9,
                'download_url': f"https://example.com/downloads/{product_id}.zip" if random.random() > 0.95 else None,
                'rating': round(random.uniform(3.0, 5.0), 1),
                'review_count': random.randint(0, 1000),
                'view_count': random.randint(0, 100000),
                'purchase_count': random.randint(0, 5000),
                'tags': random.sample(['new', 'popular', 'sale', 'limited', 'featured', 'best-seller', 'trending'], k=random.randint(2, 5)),
                'is_featured': random.random() > 0.8,
                'is_new': random.random() > 0.7,
                'is_bestseller': random.random() > 0.9,
                'published_at': datetime.now() - timedelta(days=random.randint(1, 730)),
                'created_at': datetime.now() - timedelta(days=random.randint(1, 730)),
                'updated_at': datetime.now()
            }
            products.append(product)
        return products

    def generate_product_images_chunk(self, chunk_size, products):
        """Generate product images"""
        images = []
        
        for _ in range(chunk_size):
            product = random.choice(products)
            image_count = random.randint(1, 5)
            
            for img_idx in range(image_count):
                image = {
                    '_id': str(uuid.uuid4()),
                    'product_id': product['_id'],
                    'url': f"https://example.com/products/{product['_id']}/images/{img_idx}.jpg",
                    'thumbnail_url': f"https://example.com/products/{product['_id']}/thumbnails/{img_idx}.jpg",
                    'alt_text': f"Image {img_idx} for {product['name']}",
                    'title': f"{product['name']} - View {img_idx + 1}",
                    'sort_order': img_idx,
                    'is_primary': img_idx == 0,
                    'width': random.choice([800, 1024, 1200, 1600, 1920]),
                    'height': random.choice([600, 768, 900, 1200, 1080]),
                    'size_bytes': random.randint(50000, 5000000),
                    'format': random.choice(['jpg', 'png', 'webp']),
                    'created_at': datetime.now() - timedelta(days=random.randint(1, 730))
                }
                images.append(image)
        return images

    def generate_inventory_chunk(self, chunk_size, products, warehouses):
        """Generate inventory records"""
        inventory_records = []
        
        for _ in range(chunk_size):
            product = random.choice(products)
            warehouse = random.choice(warehouses) if warehouses else None
            
            record = {
                '_id': str(uuid.uuid4()),
                'product_id': product['_id'],
                'warehouse_id': warehouse['_id'] if warehouse else None,
                'location_code': f"A{random.randint(1,50)}-B{random.randint(1,30)}-{random.randint(1,20)}",
                'quantity': random.randint(0, 500),
                'reserved_quantity': random.randint(0, 50),
                'damaged_quantity': random.randint(0, 5),
                'backorder_quantity': random.randint(0, 100) if product['allow_backorders'] else 0,
                'reorder_point': random.randint(10, 100),
                'reorder_quantity': random.randint(50, 500),
                'last_counted_at': datetime.now() - timedelta(days=random.randint(1, 90)),
                'count_discrepancy': random.randint(-5, 5) if random.random() > 0.9 else 0,
                'storage_condition': random.choice(['ambient', 'refrigerated', 'climate_controlled']),
                'expiry_date': datetime.now() + timedelta(days=random.randint(30, 730)) if random.random() > 0.8 else None,
                'batch_number': f"BATCH-{random.randint(1000,9999)}" if random.random() > 0.7 else None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            inventory_records.append(record)
        return inventory_records

    def generate_orders_chunk(self, chunk_size, users, addresses, payment_methods):
        """Generate orders"""
        orders = []
        order_statuses = ['pending', 'processing', 'confirmed', 'shipped', 'delivered', 'cancelled', 'refunded']
        order_status_weights = [0.1, 0.15, 0.2, 0.2, 0.2, 0.1, 0.05]
        
        payment_statuses = ['pending', 'authorized', 'paid', 'failed', 'refunded', 'partially_refunded']
        shipping_methods = ['standard', 'express', 'overnight', 'pickup', 'digital']
        
        for _ in range(chunk_size):
            user = random.choice(users)
            
            # Filter addresses for this user
            user_addresses = [a for a in addresses if a['user_id'] == user['_id']]
            user_payment_methods = [p for p in payment_methods if p['user_id'] == user['_id']]
            
            shipping_address = random.choice(user_addresses) if user_addresses else None
            billing_address = random.choice(user_addresses) if user_addresses else None
            payment_method = random.choice(user_payment_methods) if user_payment_methods else None
            
            order_date = datetime.now() - timedelta(days=random.randint(1, 365))
            subtotal = round(random.uniform(20, 1000), 2)
            shipping_cost = round(random.uniform(0, 50), 2)
            tax_rate = random.choice([0, 5, 8, 10, 15])
            tax_amount = round(subtotal * tax_rate / 100, 2)
            discount_amount = round(random.uniform(0, subtotal * 0.3), 2) if random.random() > 0.5 else 0
            total = round(subtotal + shipping_cost + tax_amount - discount_amount, 2)
            
            order_id = str(uuid.uuid4())
            self.order_ids.append(order_id)
            
            order = {
                '_id': order_id,
                'order_number': f"ORD-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:8].upper()}",
                'user_id': user['_id'],
                'shipping_address_id': shipping_address['_id'] if shipping_address else None,
                'billing_address_id': billing_address['_id'] if billing_address else None,
                'payment_method_id': payment_method['_id'] if payment_method else None,
                'status': random.choices(order_statuses, weights=order_status_weights)[0],
                'payment_status': random.choice(payment_statuses),
                'shipping_method': random.choice(shipping_methods),
                'subtotal': subtotal,
                'shipping_cost': shipping_cost,
                'tax_amount': tax_amount,
                'tax_rate': tax_rate,
                'discount_amount': discount_amount,
                'discount_code': f"SAVE{random.randint(10,50)}" if discount_amount > 0 else None,
                'total_amount': total,
                'currency': 'USD',
                'exchange_rate': 1.0,
                'notes': random.choice(['', 'Gift wrap please', 'Leave at door', 'Call on arrival', 'Ring bell']) if random.random() > 0.7 else '',
                'customer_note': random.choice(['', 'Thanks!', 'Urgent delivery', 'Gift']) if random.random() > 0.8 else '',
                'admin_note': random.choice(['', 'Priority customer', 'Handle with care']) if random.random() > 0.9 else '',
                'ip_address': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'user_agent': 'Mozilla/5.0...',
                'created_at': order_date,
                'updated_at': datetime.now(),
                'processed_at': order_date + timedelta(hours=random.randint(1, 24)) if order_date < datetime.now() else None,
                'shipped_at': order_date + timedelta(days=random.randint(1, 3)) if order_date < datetime.now() - timedelta(days=3) else None,
                'delivered_at': order_date + timedelta(days=random.randint(3, 10)) if order_date < datetime.now() - timedelta(days=10) else None,
                'cancelled_at': order_date + timedelta(days=random.randint(1, 5)) if random.random() > 0.8 and order_date < datetime.now() else None,
                'refunded_at': order_date + timedelta(days=random.randint(5, 20)) if random.random() > 0.9 and order_date < datetime.now() - timedelta(days=20) else None
            }
            orders.append(order)
        return orders

    def generate_order_items_chunk(self, chunk_size, orders, products):
        """Generate order items"""
        order_items = []
        
        for _ in range(chunk_size):
            order = random.choice(orders)
            product = random.choice(products)
            quantity = random.randint(1, 5)
            unit_price = product['sale_price'] if product['sale_price'] else product['retail_price']
            discount = round(unit_price * random.uniform(0, 0.2), 2) if random.random() > 0.5 else 0
            
            item = {
                '_id': str(uuid.uuid4()),
                'order_id': order['_id'],
                'product_id': product['_id'],
                'product_name': product['name'],
                'sku': product['sku'],
                'quantity': quantity,
                'unit_price': unit_price,
                'discount_amount': discount,
                'discount_percentage': round(discount / unit_price * 100, 2) if discount > 0 else 0,
                'total_price': round((unit_price - discount) * quantity, 2),
                'tax_rate': product['tax_rate'],
                'tax_amount': round((unit_price - discount) * quantity * product['tax_rate'] / 100, 2),
                'is_gift': random.random() > 0.9,
                'gift_message': 'Happy Birthday!' if random.random() > 0.9 else None,
                'has_warranty': random.random() > 0.7,
                'warranty_months': random.choice([12, 24, 36]) if random.random() > 0.7 else None,
                'created_at': order['created_at']
            }
            order_items.append(item)
        return order_items

    def generate_reviews_chunk(self, chunk_size, users, products):
        """Generate product reviews"""
        reviews = []
        review_titles = ['Excellent product!', 'Great value', 'Good quality', 'Average', 'Disappointing', 'Not as expected',
                        'Highly recommend', 'Perfect!', 'Could be better', 'Amazing!', 'Poor quality', 'Worth the money']
        
        review_texts = [
            'This product exceeded my expectations. Highly recommended!',
            'Good quality for the price. Would buy again.',
            'Average product, nothing special.',
            'Disappointed with the quality. Expected better.',
            'Exactly as described. Happy with purchase.',
            'Fast shipping and great product!',
            'Poor customer service but product is okay.',
            'Best purchase I\'ve made this year!',
            'Not worth the money. Regret buying.',
            'Perfect condition and works great.',
            'Decent product but overpriced.',
            'Love it! Will buy more from this brand.'
        ]
        
        # Rating weights: more positive reviews
        rating_weights = [5, 10, 20, 35, 30]  # 1,2,3,4,5
        
        for _ in range(chunk_size):
            user = random.choice(users)
            product = random.choice(products)
            rating = random.choices([1,2,3,4,5], weights=rating_weights)[0]
            
            review = {
                '_id': str(uuid.uuid4()),
                'product_id': product['_id'],
                'user_id': user['_id'],
                'user_name': f"{user['first_name']} {user['last_name'][0]}.",
                'rating': rating,
                'title': random.choice(review_titles),
                'content': random.choice(review_texts),
                'pros': random.sample(['Quality', 'Price', 'Design', 'Durability', 'Performance', 'Features'], k=random.randint(0, 3)) if rating >= 4 else [],
                'cons': random.sample(['Expensive', 'Heavy', 'Complex', 'Size', 'Battery', 'Material'], k=random.randint(0, 3)) if rating <= 2 else [],
                'images': [f"https://example.com/reviews/review_{random.randint(1,10000)}.jpg" for _ in range(random.randint(0, 3))] if random.random() > 0.7 else [],
                'verified_purchase': random.random() > 0.2,
                'helpful_votes': random.randint(0, 100),
                'unhelpful_votes': random.randint(0, 20),
                'reported_count': random.randint(0, 5),
                'is_approved': random.random() > 0.05,
                'is_featured': random.random() > 0.9,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365)),
                'updated_at': datetime.now()
            }
            reviews.append(review)
        return reviews

    def generate_warehouses_chunk(self, chunk_size):
        """Generate warehouses"""
        warehouses = []
        warehouse_names = ['East Coast', 'West Coast', 'Central', 'Southern', 'North East', 'South West',
                          'Midwest', 'Pacific', 'Mountain', 'Gulf Coast']
        
        for i in range(chunk_size):
            warehouse = {
                '_id': str(uuid.uuid4()),
                'name': f"{random.choice(warehouse_names)} Warehouse {i}",
                'code': f"WH-{i+1:04d}",
                'type': random.choice(['main', 'satellite', 'fulfillment', 'returns']),
                'address': {
                    'street': f"{random.randint(1,9999)} Industrial Pkwy",
                    'city': random.choice(self.cities),
                    'state': random.choice(self.states),
                    'zip': f"{random.randint(10000,99999)}",
                    'country': random.choice(['USA', 'Canada', 'Mexico'])
                },
                'contact_person': f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                'contact_phone': f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}",
                'contact_email': f"warehouse{i}@company.com",
                'square_feet': random.randint(10000, 500000),
                'storage_capacity': random.randint(1000, 100000),
                'current_utilization': random.randint(20, 95),
                'temperature_controlled': random.random() > 0.6,
                'hazmat_certified': random.random() > 0.8,
                'security_level': random.choice(['basic', 'medium', 'high', 'maximum']),
                'operating_hours': '24/7' if random.random() > 0.5 else '9am-5pm',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 1825)),
                'updated_at': datetime.now()
            }
            warehouses.append(warehouse)
        return warehouses

    def generate_suppliers_chunk(self, chunk_size):
        """Generate suppliers"""
        suppliers = []
        
        for i in range(chunk_size):
            supplier = {
                '_id': str(uuid.uuid4()),
                'name': f"{random.choice(['Global', 'Premier', 'Quality', 'Reliable', 'Elite', 'Prime'])} Supplies {i}",
                'code': f"SUP-{i+1:06d}",
                'contact_person': f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                'contact_phone': f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}",
                'contact_email': f"supplier{i}@example.com",
                'alternate_contact': f"alt{i}@example.com" if random.random() > 0.7 else None,
                'address': {
                    'street': f"{random.randint(1,9999)} Business Blvd",
                    'city': random.choice(self.cities),
                    'state': random.choice(self.states),
                    'zip': f"{random.randint(10000,99999)}",
                    'country': random.choice(self.countries)
                },
                'payment_terms': random.choice(['net30', 'net60', 'net90', 'immediate']),
                'minimum_order': round(random.uniform(500, 10000), 2),
                'lead_time_days': random.randint(7, 60),
                'shipping_methods': random.sample(['ground', 'air', 'sea', 'rail'], k=random.randint(1, 3)),
                'categories': random.sample(list(self.product_names.keys()), k=random.randint(1, 4)),
                'rating': round(random.uniform(3.0, 5.0), 1),
                'total_orders': random.randint(10, 5000),
                'on_time_delivery_rate': round(random.uniform(0.85, 1.0), 2),
                'quality_rating': round(random.uniform(0.9, 1.0), 2),
                'is_preferred': random.random() > 0.7,
                'is_active': random.random() > 0.1,
                'contract_start': datetime.now() - timedelta(days=random.randint(1, 730)),
                'contract_end': datetime.now() + timedelta(days=random.randint(1, 730)) if random.random() > 0.5 else None,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 1825)),
                'updated_at': datetime.now()
            }
            suppliers.append(supplier)
        return suppliers

    def generate_coupons_chunk(self, chunk_size):
        """Generate coupons/discounts"""
        coupons = []
        discount_types = ['percentage', 'fixed_amount', 'buy_one_get_one', 'free_shipping']
        
        for i in range(chunk_size):
            discount_type = random.choice(discount_types)
            if discount_type == 'percentage':
                discount_value = random.choice([5, 10, 15, 20, 25, 30, 40, 50])
            elif discount_type == 'fixed_amount':
                discount_value = round(random.uniform(5, 100), 2)
            else:
                discount_value = 0
            
            start_date = datetime.now() - timedelta(days=random.randint(1, 90))
            end_date = start_date + timedelta(days=random.randint(7, 90))
            
            coupon = {
                '_id': str(uuid.uuid4()),
                'code': f"{random.choice(['SAVE', 'WELCOME', 'DEAL', 'OFFER', 'EXTRA'])}{random.randint(10,99)}{random.choice(string.ascii_uppercase)}{uuid.uuid4().hex[:6].upper()}",
                'description': f"{discount_value}{'%' if discount_type == 'percentage' else '$'} off",
                'discount_type': discount_type,
                'discount_value': discount_value,
                'minimum_purchase': round(random.uniform(0, 200), 2),
                'maximum_discount': round(random.uniform(20, 200), 2) if discount_type == 'percentage' else None,
                'applicable_categories': random.sample(self.category_ids, k=random.randint(1, 5)) if self.category_ids and random.random() > 0.5 else [],
                'applicable_products': random.sample(self.product_ids, k=random.randint(5, 20)) if self.product_ids and random.random() > 0.5 else [],
                'excluded_products': random.sample(self.product_ids, k=random.randint(1, 10)) if self.product_ids and random.random() > 0.7 else [],
                'usage_limit_per_coupon': random.randint(100, 10000),
                'usage_limit_per_user': random.randint(1, 5),
                'total_used': random.randint(0, 500),
                'start_date': start_date,
                'end_date': end_date,
                'is_active': start_date <= datetime.now() <= end_date and random.random() > 0.1,
                'is_public': random.random() > 0.3,
                'created_by': 'admin',
                'created_at': start_date - timedelta(days=random.randint(1, 30)),
                'updated_at': datetime.now()
            }
            coupons.append(coupon)
        return coupons

    def generate_activity_logs_chunk(self, chunk_size, users, products):
        """Generate user activity logs"""
        activity_types = ['login', 'logout', 'view_product', 'search', 'add_to_cart', 'remove_from_cart',
                         'view_cart', 'checkout_start', 'checkout_complete', 'view_order', 'update_profile',
                         'write_review', 'like_product', 'share_product', 'add_to_wishlist', 'remove_from_wishlist']
        
        activities = []
        
        for _ in range(chunk_size):
            user = random.choice(users) if random.random() > 0.3 else None  # Some anonymous activities
            product = random.choice(products) if random.random() > 0.5 else None
            
            activity = {
                '_id': str(uuid.uuid4()),
                'user_id': user['_id'] if user else None,
                'session_id': str(uuid.uuid4()),
                'activity_type': (activity_type := random.choice(activity_types)),
                'product_id': product['_id'] if product and activity_type in ['view_product', 'like_product', 'share_product', 'add_to_wishlist'] else None,
                'search_query': f"search term {random.randint(1,1000)}" if activity_type == 'search' else None,
                'page_url': f"https://example.com/{random.choice(['products', 'categories', 'cart', 'checkout'])}/{random.randint(1,10000)}",
                'referrer_url': f"https://{random.choice(['google.com', 'facebook.com', 'instagram.com', 'direct'])}" if random.random() > 0.4 else None,
                'ip_address': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'user_agent': 'Mozilla/5.0...',
                'device_type': random.choice(['mobile', 'desktop', 'tablet']),
                'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                'operating_system': random.choice(['Windows', 'MacOS', 'iOS', 'Android', 'Linux']),
                'screen_resolution': random.choice(['1920x1080', '1366x768', '375x667', '414x896']),
                'time_on_page': random.randint(5, 600),
                'scroll_depth_percent': random.randint(0, 100),
                'metadata': {
                    'campaign': random.choice(['summer_sale', 'winter_sale', 'new_user', None]),
                    'source': random.choice(['email', 'social', 'ads', 'organic', None])
                },
                'created_at': datetime.now() - timedelta(minutes=random.randint(1, 43200))
            }
            activities.append(activity)
        return activities

    def run(self):
        """Main execution method"""
        print(f"\n{C.BOLD}{C.MAGENTA}{'█'*70}{C.RESET}")
        print(f"{C.BOLD}{C.MAGENTA}  🛒  ECOMMERCE MASSIVE DATABASE POPULATOR{C.RESET}")
        print(f"{C.BOLD}{C.MAGENTA}  🎯  Target: ~100,000 documents per collection{C.RESET}")
        print(f"{C.BOLD}{C.MAGENTA}{'█'*70}{C.RESET}")

        start_time = time.time()

        step(1, "Generating base entities")
        
        # Users (100K)
        users = []
        user_chunks = 100000 // 1000
        with tqdm(total=100000, desc="Generating users") as pbar:
            for _ in range(user_chunks):
                chunk = self.generate_users_chunk(1000)
                users.extend(chunk)
                pbar.update(1000)
        self.db.users.insert_many(users)
        ok("Users", len(users))
        
        # Categories (5K is enough for relationships)
        categories = []
        with tqdm(total=5000, desc="Generating categories") as pbar:
            for _ in range(50):  # 5000 categories
                chunk = self.generate_categories_chunk(100)
                categories.extend(chunk)
                pbar.update(100)
        self.db.product_categories.insert_many(categories)
        ok("Categories", len(categories))

        # Brands (2K)
        brands = []
        with tqdm(total=2000, desc="Generating brands") as pbar:
            for _ in range(20):  # 2000 brands
                chunk = self.generate_brands_chunk(100)
                brands.extend(chunk)
                pbar.update(100)
        self.db.product_brands.insert_many(brands)
        ok("Brands", len(brands))
        
        # Warehouses (500)
        with tqdm(total=500, desc="Generating warehouses") as pbar:
            warehouses = self.generate_warehouses_chunk(500)
            pbar.update(500)
        self.db.warehouses.insert_many(warehouses)
        ok("Warehouses", len(warehouses))
        
        # Suppliers (1000)
        suppliers = []
        with tqdm(total=1000, desc="Generating suppliers") as pbar:
            for _ in range(10):  # 1000 suppliers
                chunk = self.generate_suppliers_chunk(100)
                suppliers.extend(chunk)
                pbar.update(100)
        self.db.suppliers.insert_many(suppliers)
        ok("Suppliers", len(suppliers))

        step(2, "Generating products")
        products = []
        product_chunks = 100000 // 1000
        with tqdm(total=100000, desc="Generating products") as pbar:
            for _ in range(product_chunks):
                chunk = self.generate_products_chunk(1000, categories, brands)
                products.extend(chunk)
                pbar.update(1000)
        self.db.products.insert_many(products)
        ok("Products", len(products))

        step(3, "Generating dependent entities")
        
        # User Profiles (100K)
        profiles = []
        with tqdm(total=len(users), desc="Generating user profiles") as pbar:
            for i in range(0, len(users), 1000):
                chunk = users[i:i+1000]
                profiles_chunk = self.generate_user_profiles_chunk(len(chunk), chunk)
                profiles.extend(profiles_chunk)
                pbar.update(len(chunk))
        self.db.user_profiles.insert_many(profiles)
        ok("User Profiles", len(profiles))
        
        # Addresses (300K - multiple per user)
        addresses = []
        with tqdm(total=300000, desc="Generating addresses") as pbar:
            for _ in range(300):  # 300K addresses
                chunk = self.generate_addresses_chunk(1000, users)
                addresses.extend(chunk)
                pbar.update(1000)
        self.db.user_addresses.insert_many(addresses)
        ok("Addresses", len(addresses))
        
        # Payment Methods (200K)
        payment_methods = []
        with tqdm(total=200000, desc="Generating payment methods") as pbar:
            for _ in range(200):  # 200K payment methods
                chunk = self.generate_payment_methods_chunk(1000, users)
                payment_methods.extend(chunk)
                pbar.update(1000)
        self.db.user_payment_methods.insert_many(payment_methods)
        ok("Payment Methods", len(payment_methods))
        
        # Product Images (500K - multiple per product)
        product_images = []
        with tqdm(total=500000, desc="Generating product images") as pbar:
            for _ in range(500):  # 500K images
                chunk = self.generate_product_images_chunk(1000, products)
                product_images.extend(chunk)
                pbar.update(1000)
        self.db.product_images.insert_many(product_images)
        ok("Product Images", len(product_images))
        
        # Inventory (200K)
        inventory = []
        with tqdm(total=200000, desc="Generating inventory records") as pbar:
            for _ in range(200):  # 200K inventory records
                chunk = self.generate_inventory_chunk(1000, products, warehouses)
                inventory.extend(chunk)
                pbar.update(1000)
        self.db.product_inventory.insert_many(inventory)
        ok("Inventory Records", len(inventory))
        
        # Orders (100K)
        orders = []
        with tqdm(total=100000, desc="Generating orders") as pbar:
            for _ in range(100):  # 100K orders
                chunk = self.generate_orders_chunk(1000, users, addresses, payment_methods)
                orders.extend(chunk)
                pbar.update(1000)
        self.db.orders.insert_many(orders)
        ok("Orders", len(orders))
        
        # Order Items (500K - multiple per order)
        order_items = []
        with tqdm(total=500000, desc="Generating order items") as pbar:
            for _ in range(500):  # 500K order items
                chunk = self.generate_order_items_chunk(1000, orders, products)
                order_items.extend(chunk)
                pbar.update(1000)
        self.db.order_items.insert_many(order_items)
        ok("Order Items", len(order_items))
        
        # Reviews (200K)
        reviews = []
        with tqdm(total=200000, desc="Generating reviews") as pbar:
            for _ in range(200):  # 200K reviews
                chunk = self.generate_reviews_chunk(1000, users, products)
                reviews.extend(chunk)
                pbar.update(1000)
        self.db.product_reviews.insert_many(reviews)
        ok("Reviews", len(reviews))
        
        # Coupons (50K)
        coupons = []
        with tqdm(total=50000, desc="Generating coupons") as pbar:
            for _ in range(50):  # 50K coupons
                chunk = self.generate_coupons_chunk(1000)
                coupons.extend(chunk)
                pbar.update(1000)
        self.db.coupons.insert_many(coupons)
        ok("Coupons", len(coupons))
        
        # Activity Logs (500K)
        activities = []
        with tqdm(total=500000, desc="Generating activity logs") as pbar:
            for _ in range(500):  # 500K activity logs
                chunk = self.generate_activity_logs_chunk(1000, users, products)
                activities.extend(chunk)
                pbar.update(1000)
        self.db.user_activity_logs.insert_many(activities)
        ok("Activity Logs", len(activities))

        step(4, "Creating indexes")
        self.create_indexes()
        
        # Step 5: Display statistics
        elapsed_time = time.time() - start_time
        step(5, "Collection Statistics")
        info(f"Time elapsed: {C.YELLOW}{elapsed_time/60:.2f} minutes{C.RESET}")
        print()
        print(f"  {C.BOLD}{C.WHITE}{'Collection':<32} {'Documents':>14}{C.RESET}")
        print(f"  {C.GRAY}{'─'*48}{C.RESET}")

        total_docs = 0
        row_colors = [C.CYAN, C.MAGENTA]
        for idx, collection_name in enumerate(sorted(self.db.list_collection_names())):
            count = self.db[collection_name].count_documents({})
            total_docs += count
            col = row_colors[idx % 2]
            print(f"  {col}  {collection_name:<32}{C.RESET} {C.BOLD}{C.WHITE}{count:>14,}{C.RESET}")

        print(f"  {C.GRAY}{'─'*48}{C.RESET}")
        print(f"  {C.BOLD}{C.YELLOW}  {'TOTAL':<32}{total_docs:>14,}{C.RESET}")
        print()
        print(f"{C.BOLD}{C.GREEN}{'█'*70}{C.RESET}")
        print(f"{C.BOLD}{C.GREEN}  ✅  POPULATION COMPLETE!{C.RESET}")
        print(f"{C.BOLD}{C.GREEN}{'█'*70}{C.RESET}")
        print(f"  {C.CYAN}🔌  Connect:   mongodb://localhost:27017{C.RESET}")
        print(f"  {C.CYAN}🗄️   Database:  ecommerce_massive_db{C.RESET}")

    def create_indexes(self):
        """Create indexes for all collections"""
        info("Building index configurations...")

        index_configs = [
            # Users collection
            (self.db.users, [('email', ASCENDING)], {'unique': True}),
            (self.db.users, [('username', ASCENDING)], {'unique': True}),
            (self.db.users, [('created_at', DESCENDING)]),
            (self.db.users, [('last_login', DESCENDING)]),
            (self.db.users, [('account_type', ASCENDING)]),
            (self.db.users, [('loyalty_points', DESCENDING)]),
            
            # User profiles
            (self.db.user_profiles, [('user_id', ASCENDING)], {'unique': True}),
            (self.db.user_profiles, [('birth_date', ASCENDING)]),
            (self.db.user_profiles, [('gender', ASCENDING)]),
            (self.db.user_profiles, [('annual_income', ASCENDING)]),
            
            # Addresses
            (self.db.user_addresses, [('user_id', ASCENDING)]),
            (self.db.user_addresses, [('postal_code', ASCENDING)]),
            (self.db.user_addresses, [('country', ASCENDING)]),
            (self.db.user_addresses, [('is_default', ASCENDING)]),
            
            # Payment methods
            (self.db.user_payment_methods, [('user_id', ASCENDING)]),
            (self.db.user_payment_methods, [('method_type', ASCENDING)]),
            (self.db.user_payment_methods, [('is_default', ASCENDING)]),
            
            # Categories
            (self.db.product_categories, [('slug', ASCENDING)], {'unique': True}),
            (self.db.product_categories, [('parent_id', ASCENDING)]),
            (self.db.product_categories, [('is_active', ASCENDING)]),
            
            # Brands
            (self.db.product_brands, [('slug', ASCENDING)], {'unique': True}),
            (self.db.product_brands, [('is_active', ASCENDING)]),
            (self.db.product_brands, [('rating', DESCENDING)]),
            
            # Products
            (self.db.products, [('sku', ASCENDING)], {'unique': True}),
            (self.db.products, [('name', TEXT)]),
            (self.db.products, [('category_id', ASCENDING)]),
            (self.db.products, [('brand_id', ASCENDING)]),
            (self.db.products, [('retail_price', ASCENDING)]),
            (self.db.products, [('rating', DESCENDING)]),
            (self.db.products, [('created_at', DESCENDING)]),
            (self.db.products, [('is_featured', ASCENDING)]),
            (self.db.products, [('in_stock', ASCENDING)]),
            
            # Product images
            (self.db.product_images, [('product_id', ASCENDING)]),
            (self.db.product_images, [('is_primary', ASCENDING)]),
            
            # Inventory
            (self.db.product_inventory, [('product_id', ASCENDING)]),
            (self.db.product_inventory, [('warehouse_id', ASCENDING)]),
            (self.db.product_inventory, [('quantity', ASCENDING)]),
            (self.db.product_inventory, [('reorder_point', ASCENDING)]),
            
            # Orders
            (self.db.orders, [('order_number', ASCENDING)], {'unique': True}),
            (self.db.orders, [('user_id', ASCENDING)]),
            (self.db.orders, [('status', ASCENDING)]),
            (self.db.orders, [('payment_status', ASCENDING)]),
            (self.db.orders, [('created_at', DESCENDING)]),
            (self.db.orders, [('shipping_address_id', ASCENDING)]),
            (self.db.orders, [('total_amount', ASCENDING)]),
            
            # Order items
            (self.db.order_items, [('order_id', ASCENDING)]),
            (self.db.order_items, [('product_id', ASCENDING)]),
            (self.db.order_items, [('sku', ASCENDING)]),
            
            # Reviews
            (self.db.product_reviews, [('product_id', ASCENDING)]),
            (self.db.product_reviews, [('user_id', ASCENDING)]),
            (self.db.product_reviews, [('rating', DESCENDING)]),
            (self.db.product_reviews, [('created_at', DESCENDING)]),
            (self.db.product_reviews, [('verified_purchase', ASCENDING)]),
            
            # Warehouses
            (self.db.warehouses, [('code', ASCENDING)], {'unique': True}),
            (self.db.warehouses, [('state', ASCENDING)]),
            
            # Suppliers
            (self.db.suppliers, [('code', ASCENDING)], {'unique': True}),
            (self.db.suppliers, [('rating', DESCENDING)]),
            (self.db.suppliers, [('is_preferred', ASCENDING)]),
            
            # Coupons
            (self.db.coupons, [('code', ASCENDING)], {'unique': True}),
            (self.db.coupons, [('start_date', ASCENDING), ('end_date', ASCENDING)]),
            (self.db.coupons, [('is_active', ASCENDING)]),
            
            # Activity logs
            (self.db.user_activity_logs, [('user_id', ASCENDING)]),
            (self.db.user_activity_logs, [('activity_type', ASCENDING)]),
            (self.db.user_activity_logs, [('created_at', DESCENDING)]),
            (self.db.user_activity_logs, [('session_id', ASCENDING)]),
            (self.db.user_activity_logs, [('product_id', ASCENDING)]),
        ]
        
        with bar("Creating indexes", len(index_configs), C.YELLOW) as pbar:
            for config in index_configs:
                collection, keys = config[0], config[1]
                kwargs = config[2] if len(config) > 2 else {}
                try:
                    collection.create_index(keys, **kwargs)
                except Exception as e:
                    warn(f"Could not create index on {collection.name}: {e}")
                pbar.update(1)

        ok("Indexes created", len(index_configs))

def main():
    """Main execution function"""
    try:
        print(f"\n{C.BOLD}{C.MAGENTA}{'█'*70}{C.RESET}")
        print(f"{C.BOLD}{C.MAGENTA}  🛒  ECOMMERCE MASSIVE DATABASE POPULATOR{C.RESET}")
        print(f"{C.BOLD}{C.MAGENTA}  📂  Creating 100+ collections with ~100K documents each{C.RESET}")
        print(f"{C.BOLD}{C.MAGENTA}{'█'*70}{C.RESET}")

        # Connect to MongoDB
        print(f"\n  {C.CYAN}📡  Connecting to MongoDB...{C.RESET}")
        client = MongoClient('mongodb://localhost:27017/')
        print(f"  {C.GREEN}✔   Connected!{C.RESET}")

        # Drop existing database
        print(f"  {C.YELLOW}🗑️   Dropping existing database...{C.RESET}")
        client.drop_database('ecommerce_massive_db')
        print(f"  {C.GREEN}✔   Dropped.{C.RESET}")

        db = client['ecommerce_massive_db']

        # Initialize & run generator
        generator = MassiveDataGenerator(db)
        generator.run()

        print(f"\n{C.BOLD}{C.GREEN}{'█'*70}{C.RESET}")
        print(f"{C.BOLD}{C.GREEN}  🎉  DATABASE POPULATION COMPLETED SUCCESSFULLY!{C.RESET}")
        print(f"{C.BOLD}{C.GREEN}{'█'*70}{C.RESET}")
        print(f"\n  {C.BOLD}{C.WHITE}📊  NEXT STEPS:{C.RESET}")
        print(f"  {C.CYAN}  1.  Open MongoDB Compass{C.RESET}")
        print(f"  {C.CYAN}  2.  Connect to: mongodb://localhost:27017{C.RESET}")
        print(f"  {C.CYAN}  3.  Select database: ecommerce_massive_db{C.RESET}")
        print(f"  {C.CYAN}  4.  Explore 100+ collections with ~100K docs each!{C.RESET}")
        print(f"\n  {C.BOLD}{C.WHITE}💡  TIPS:{C.RESET}")
        print(f"  {C.GRAY}  •  Use the Explain tab in Compass to analyze query performance{C.RESET}")
        print(f"  {C.GRAY}  •  Try different indexes to optimize queries{C.RESET}")
        print(f"  {C.GRAY}  •  Practice aggregation pipelines on large datasets{C.RESET}")
        print(f"  {C.GRAY}  •  Test your application with realistic data volumes{C.RESET}")

    except KeyboardInterrupt:
        warn("Process interrupted by user")
    except Exception as e:
        err(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()