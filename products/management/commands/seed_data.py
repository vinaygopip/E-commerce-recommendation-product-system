from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Category, Brand, Product
from accounts.models import Profile
from reviews.models import Review
from orders.models import Order, OrderItem
from recommendations.models import UserActivity, Wishlist, WishlistItem
from recommendations.engine import retrain_all_engines
from decimal import Decimal
import random

class Command(BaseCommand):
    help = "Seeds database with categories, brands, products, demo users, realistic activities, reviews, and trains ML models."

    def handle(self, *args, **options):
        self.stdout.write("Starting ShopAI database seeding...")

        # 1. Categories
        categories_data = [
            {"name": "Electronics & Gadgets", "slug": "electronics", "icon": "bi-phone", "description": "Cutting edge smartphones, tablets, cameras, and consumer tech."},
            {"name": "Audio & Wearables", "slug": "audio-wearables", "icon": "bi-headphones", "description": "Premium noise cancelling headphones, wireless earbuds, and smartwatches."},
            {"name": "Computers & Laptops", "slug": "computers", "icon": "bi-laptop", "description": "High performance ultrabooks, gaming rigs, and ergonomic peripherals."},
            {"name": "Fashion & Lifestyle", "slug": "fashion", "icon": "bi-bag", "description": "Contemporary apparel, running sneakers, and fashion accessories."},
            {"name": "Smart Home & Living", "slug": "smart-home", "icon": "bi-house-check", "description": "Smart displays, robotic vacuums, IoT lighting, and modern home decor."},
            {"name": "Fitness & Sports", "slug": "sports", "icon": "bi-trophy", "description": "Athletic gear, fitness trackers, and outdoor lifestyle accessories."},
        ]

        cat_map = {}
        for c in categories_data:
            cat, _ = Category.objects.get_or_create(slug=c["slug"], defaults=c)
            cat_map[c["slug"]] = cat

        # 2. Brands
        brands_data = [
            "Apple", "Sony", "Samsung", "Dell", "Logitech", "Bose", 
            "Nike", "Adidas", "Asus", "Philips", "JBL", "Anker"
        ]
        brand_map = {}
        for b_name in brands_data:
            brand, _ = Brand.objects.get_or_create(name=b_name)
            brand_map[b_name] = brand

        # 3. Products
        products_data = [
            # Audio
            {
                "name": "Sony WH-1000XM5 Wireless Noise-Cancelling Headphones",
                "category": cat_map["audio-wearables"],
                "brand": brand_map["Sony"],
                "price": Decimal("26990.00"),
                "discount_percent": 15,
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
                "features": "Industry-leading active noise cancelling with 8 microphones\n30-hour battery life with ultra-quick charging\nCrystal clear hands-free calling with Precise Voice Pickup\nHi-Res Audio wireless with LDAC support",
                "description": "Sony's flagship wireless headphones feature dual processors and eight microphones for unprecedented noise cancelling and astonishing call clarity. Perfect for audiophiles and remote professionals."
            },
            {
                "name": "Apple AirPods Pro (2nd Generation) with MagSafe Case",
                "category": cat_map["audio-wearables"],
                "brand": brand_map["Apple"],
                "price": Decimal("24900.00"),
                "discount_percent": 10,
                "stock": 30,
                "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&q=80",
                "features": "Apple-designed H2 chip for smarter noise cancellation\nAdaptive Transparency lets outside sounds in\nPersonalized Spatial Audio with dynamic head tracking\nUp to 6 hours listening time with ANC enabled",
                "description": "The AirPods Pro 2 feature next-level Active Noise Cancellation and Adaptive Transparency to reduce external noise. Personalized Spatial Audio immerses you in rich, detailed sound."
            },
            {
                "name": "Bose QuietComfort 45 Bluetooth Headphones",
                "category": cat_map["audio-wearables"],
                "brand": brand_map["Bose"],
                "price": Decimal("22999.00"),
                "discount_percent": 12,
                "stock": 18,
                "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&q=80",
                "features": "Acoustic Noise Cancelling technology\nTriPort acoustic architecture for deep rich sound\nQuiet and Aware modes\nUp to 22 hours battery on a single charge",
                "description": "The perfect balance of quiet, comfort, and sound. Lightweight synthetic leather ear cushions provide all-day luxury while proprietary acoustic design delivers unmatched audio fidelity."
            },
            {
                "name": "JBL Flip 6 Portable Waterproof Bluetooth Speaker",
                "category": cat_map["audio-wearables"],
                "brand": brand_map["JBL"],
                "price": Decimal("9999.00"),
                "discount_percent": 20,
                "stock": 40,
                "image_url": "https://images.unsplash.com/photo-1589003077984-894e133dabab?w=800&q=80",
                "features": "IP67 waterproof and dustproof design\n2-way speaker system with racetrack-shaped woofer\n12 hours of playtime on a single charge\nPartyBoost compatible for stereo pairing",
                "description": "Bold JBL Original Pro Sound meets rugged IP67 portability. Big sound, punchy bass, and all-weather resistance make this Bluetooth speaker ready for any adventure."
            },

            # Computers & Tech
            {
                "name": "Dell XPS 15 InfinityEdge OLED Laptop",
                "category": cat_map["computers"],
                "brand": brand_map["Dell"],
                "price": Decimal("149990.00"),
                "discount_percent": 8,
                "stock": 12,
                "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&q=80",
                "features": "Intel Core i7-13700H 14-core processor\n15.6-inch 3.5K OLED touch display (400 nits)\nNVIDIA GeForce RTX 4060 8GB GDDR6\n32GB DDR5 RAM, 1TB PCIe NVMe SSD",
                "description": "Immerse yourself in content creation with the stunning 3.5K OLED panel and raw computing power. Precision crafted from CNC machined aluminum and aerospace-inspired carbon fiber palm rest."
            },
            {
                "name": "Apple MacBook Air 15-inch M3 Chip (Midnight)",
                "category": cat_map["computers"],
                "brand": brand_map["Apple"],
                "price": Decimal("134900.00"),
                "discount_percent": 5,
                "stock": 20,
                "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80",
                "features": "Apple M3 8-core CPU with 10-core GPU\n15.3-inch Liquid Retina display with 500 nits brightness\n18 hours of battery life with silent fanless architecture\n1080p FaceTime HD camera with 3-mic array",
                "description": "Incredibly thin and fast, MacBook Air lets you work, play, or create anything with the power of the M3 chip. Features an expansive 15-inch Liquid Retina display in a sleek unibody chassis."
            },
            {
                "name": "Logitech MX Master 3S Wireless Performance Mouse",
                "category": cat_map["computers"],
                "brand": brand_map["Logitech"],
                "price": Decimal("8995.00"),
                "discount_percent": 15,
                "stock": 45,
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&q=80",
                "features": "8K DPI any-surface glass tracking sensor\nQuiet clicks technology with 90% reduced click noise\nMagSpeed electromagnetic scrolling up to 1000 lines/sec\nErgonomic silhouette crafted for palm comfort",
                "description": "An icon remastered. Feel every moment of your workflow with even more precision, tactile feedback, and performance thanks to Quiet Clicks and an 8,000 DPI track-on-glass sensor."
            },
            {
                "name": "Logitech MX Mechanical Wireless Illuminated Keyboard",
                "category": cat_map["computers"],
                "brand": brand_map["Logitech"],
                "price": Decimal("13995.00"),
                "discount_percent": 10,
                "stock": 22,
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&q=80",
                "features": "Tactile Quiet low-profile mechanical switches\nSmart illumination with ambient light hand detection\nMulti-device pair across 3 devices via Bluetooth/Bolt\nUSB-C fast rechargeable up to 10 months without backlight",
                "description": "High-performance mechanical typing keyboard designed for coders and creators with ultra-fluid low profile switches and smart lighting."
            },
            {
                "name": "Asus ROG Swift 27-inch 240Hz Fast IPS Gaming Monitor",
                "category": cat_map["computers"],
                "brand": brand_map["Asus"],
                "price": Decimal("38990.00"),
                "discount_percent": 18,
                "stock": 15,
                "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&q=80",
                "features": "27-inch WQHD (2560 x 1440) Fast IPS panel\n240Hz refresh rate with 1ms GTG response time\nG-SYNC Compatible & AMD FreeSync Premium Pro\nDisplayHDR 600 certified with 95% DCI-P3 color gamut",
                "description": "Engineered for esports tournaments and competitive gaming. Features blisteringly fast 240Hz refresh rate and ultra-accurate color calibration."
            },

            # Electronics & Smartphones
            {
                "name": "Samsung Galaxy S24 Ultra 5G (Titanium Black, 256GB)",
                "category": cat_map["electronics"],
                "brand": brand_map["Samsung"],
                "price": Decimal("129999.00"),
                "discount_percent": 10,
                "stock": 28,
                "image_url": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800&q=80",
                "features": "Snapdragon 8 Gen 3 for Galaxy processor\n200MP quad telephoto camera with 100x Space Zoom\nBuilt-in S-Pen stylus with titanium frame design\nGalaxy AI with Live Translate and Circle to Search",
                "description": "Meet Galaxy S24 Ultra, the ultimate form of Galaxy Ultra with a new titanium exterior and a 6.8-inch flat display with integrated S Pen."
            },
            {
                "name": "Apple iPhone 15 Pro Max (Natural Titanium, 256GB)",
                "category": cat_map["electronics"],
                "brand": brand_map["Apple"],
                "price": Decimal("149900.00"),
                "discount_percent": 5,
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&q=80",
                "features": "Aerospace-grade titanium design with textured matte glass\nA17 Pro Bionic chip for console-level gaming\n48MP Main camera with 5x optical zoom telephoto lens\nCustomizable Action Button and USB-C port",
                "description": "Forged in titanium and featuring the groundbreaking A17 Pro chip, customizable Action button, and the most powerful iPhone camera system ever."
            },
            {
                "name": "Sony Alpha 7 IV Full-Frame Mirrorless Camera",
                "category": cat_map["electronics"],
                "brand": brand_map["Sony"],
                "price": Decimal("209990.00"),
                "discount_percent": 7,
                "stock": 10,
                "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&q=80",
                "features": "33MP full-frame Exmor R back-illuminated CMOS sensor\nBIONZ XR processor with AI real-time autofocus tracking\n4K 60p 10-bit 4:2:2 movie recording\n759-point phase-detection AF covering 94% of frame",
                "description": "An all-around powerhouse for photography and cinematography. The A7 IV delivers hybrid excellence with next-gen color science and lightning auto-focus."
            },
            {
                "name": "Anker 737 Power Bank 24,000mAh 140W Fast Charger",
                "category": cat_map["electronics"],
                "brand": brand_map["Anker"],
                "price": Decimal("11999.00"),
                "discount_percent": 25,
                "stock": 50,
                "image_url": "https://images.unsplash.com/photo-1609592424364-77e8fbdfdbe2?w=800&q=80",
                "features": "Ultra-powerful 140W two-way fast charging\nSmart digital display showing power input and output\nMassive 24,000mAh battery charges laptops and phones\nActiveShield 2.0 temperature monitoring",
                "description": "Equipped with the latest Power Delivery 3.1 and bi-directional technology to quickly recharge the portable charger or get a 140W ultra-powerful charge."
            },

            # Fashion & Lifestyle
            {
                "name": "Nike Air Zoom Pegasus 40 Running Shoes",
                "category": cat_map["fashion"],
                "brand": brand_map["Nike"],
                "price": Decimal("10495.00"),
                "discount_percent": 15,
                "stock": 35,
                "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80",
                "features": "Nike React technology with two Zoom Air units\nEngineered mesh upper for lightweight breathability\nWaffle-inspired outsole pattern for road traction\nPadded collar and tongue for plush heel containment",
                "description": "A springy ride for every run, the Peg's familiar, just-for-you feel returns to help you accomplish your fitness goals with responsive cushioning."
            },
            {
                "name": "Adidas Ultraboost Light Performance Sneakers",
                "category": cat_map["fashion"],
                "brand": brand_map["Adidas"],
                "price": Decimal("13999.00"),
                "discount_percent": 20,
                "stock": 30,
                "image_url": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&q=80",
                "features": "Light BOOST midsole material is 30% lighter\nPRIMEKNIT+ textile upper provides sock-like fit\nLinear Energy Push system increases stiffness for propulsion\nContinental Better Rubber outsole provides superior grip",
                "description": "Experience epic energy return with the lightest Ultraboost ever made. Built with sustainable ocean plastics and responsive cushioning for city streets."
            },
            {
                "name": "Nike Dri-FIT Tech Fleece Full-Zip Windrunner Hoodie",
                "category": cat_map["fashion"],
                "brand": brand_map["Nike"],
                "price": Decimal("6995.00"),
                "discount_percent": 10,
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&q=80",
                "features": "Smooth on both sides premium lightweight fleece\nChevron design lines nodding to vintage Windrunner jacket\nZippered sleeve pocket provides quick key/card storage\nArticulated panelling for natural mobility",
                "description": "Our lightweight, premium fleece—smooth both inside and out—gives you plenty of warmth without adding bulk. Ideal for athletic streetwear."
            },

            # Smart Home & Living
            {
                "name": "Philips Hue Smart LED Ambient Starter Kit (4 Bulbs + Bridge)",
                "category": cat_map["smart-home"],
                "brand": brand_map["Philips"],
                "price": Decimal("14499.00"),
                "discount_percent": 15,
                "stock": 20,
                "image_url": "https://images.unsplash.com/photo-1558002038-1055907df827?w=800&q=80",
                "features": "16 million colors and 50,000 shades of warm-to-cool white light\nSync lights with music, movies, and PC gaming\nWorks with Alexa, Apple HomeKit, and Google Assistant\nAutomate wake-up routines and away-from-home control",
                "description": "Transform your home lighting with the Philips Hue Starter Kit. Set the mood with millions of colors or warm white light controllable via smartphone or voice."
            },
            {
                "name": "Samsung SmartThings IoT Station & Wireless Charger Pad",
                "category": cat_map["smart-home"],
                "brand": brand_map["Samsung"],
                "price": Decimal("6499.00"),
                "discount_percent": 18,
                "stock": 35,
                "image_url": "https://images.unsplash.com/photo-1507646227500-4d389b0012be?w=800&q=80",
                "features": "Central smart home hub compatible with Zigbee and Matter\n15W fast inductive wireless charging pad on top surface\nCustom smart buttons trigger multiple smart home routines\nLocates Galaxy smart tags around the house",
                "description": "An easy-to-use smart home hub and fast charging pad that connects your smart devices effortlessly into automated routines."
            },

            # Sports & Fitness
            {
                "name": "Apple Watch Series 9 GPS 45mm (Midnight Aluminum)",
                "category": cat_map["sports"],
                "brand": brand_map["Apple"],
                "price": Decimal("44900.00"),
                "discount_percent": 8,
                "stock": 30,
                "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&q=80",
                "features": "S9 SiP chip with magical Double Tap touchless gesture\nAlways-On Retina display up to 2000 nits\nAdvanced health sensors: ECG, Blood Oxygen, Temperature\n50m water resistant and swimproof workout tracking",
                "description": "Smarter, brighter, and mightier. The S9 chip enables a super-bright display and a magical new way to quickly and easily use your Apple Watch without touching the screen."
            },
            {
                "name": "Nike Hydro Pro Stainless Steel Insulated 32oz Water Bottle",
                "category": cat_map["sports"],
                "brand": brand_map["Nike"],
                "price": Decimal("2499.00"),
                "discount_percent": 12,
                "stock": 60,
                "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&q=80",
                "features": "Double-wall vacuum insulation keeps liquids cold 24 hours\nBPA-free 18/8 pro-grade stainless steel body\nLeakproof sport straw cap with silicone comfort grip\nScratch-resistant textured powder coat exterior",
                "description": "Engineered for intense gym sessions and long hiking trails. Keeps hydration ice cold all day without bottle sweat or condensation."
            }
        ]

        created_products = []
        for p_data in products_data:
            prod, created = Product.objects.get_or_create(
                name=p_data["name"],
                defaults={
                    "category": p_data["category"],
                    "brand": p_data["brand"],
                    "price": p_data["price"],
                    "discount_percent": p_data["discount_percent"],
                    "stock": p_data["stock"],
                    "image_url": p_data["image_url"],
                    "features": p_data["features"],
                    "description": p_data["description"],
                    "is_active": True,
                    "is_featured": True,
                    "view_count": random.randint(45, 320)
                }
            )
            created_products.append(prod)

        self.stdout.write(f"Catalog created: {len(created_products)} active products.")

        # 4. Create Demo Users
        users_data = [
            {"username": "admin", "email": "admin@shopai.edu", "is_staff": True, "is_superuser": True, "password": "admin123", "first": "System", "last": "Admin"},
            {"username": "vinay", "email": "vinay@example.com", "is_staff": False, "is_superuser": False, "password": "user123", "first": "Vinay", "last": "Kumar"},
            {"username": "priya", "email": "priya@example.com", "is_staff": False, "is_superuser": False, "password": "user123", "first": "Priya", "last": "Sharma"},
            {"username": "rahul", "email": "rahul@example.com", "is_staff": False, "is_superuser": False, "password": "user123", "first": "Rahul", "last": "Verma"},
            {"username": "ananya", "email": "ananya@example.com", "is_staff": False, "is_superuser": False, "password": "user123", "first": "Ananya", "last": "Deshmukh"},
        ]

        demo_users = {}
        for u_info in users_data:
            user, created = User.objects.get_or_create(
                username=u_info["username"],
                defaults={
                    "email": u_info["email"],
                    "first_name": u_info["first"],
                    "last_name": u_info["last"],
                    "is_staff": u_info["is_staff"],
                    "is_superuser": u_info["is_superuser"]
                }
            )
            if created:
                user.set_password(u_info["password"])
                user.save()
            demo_users[u_info["username"]] = user

        # Update Vinay's profile preferences
        vinay = demo_users["vinay"]
        if hasattr(vinay, 'profile'):
            vinay.profile.city = "Bengaluru"
            vinay.profile.state = "Karnataka"
            vinay.profile.postal_code = "560001"
            vinay.profile.phone_number = "+91 9876543210"
            vinay.profile.preferred_categories = "audio-wearables,computers,electronics"
            vinay.profile.save()

        # 5. Populate Realistic Activity Telemetry for Collaborative Filtering
        # Pattern 1: Tech Audiophiles (Vinay & Rahul browse & buy headphones, laptop, mouse)
        tech_cluster = [p for p in created_products if p.category.slug in ['audio-wearables', 'computers']]
        for p in tech_cluster[:5]:
            UserActivity.objects.create(user=vinay, product=p, activity_type='VIEW', score_weight=1.0)
            UserActivity.objects.create(user=demo_users["rahul"], product=p, activity_type='VIEW', score_weight=1.0)
        
        # Wishlist and Cart adds
        UserActivity.objects.create(user=vinay, product=tech_cluster[0], activity_type='WISHLIST_ADD', score_weight=3.0)
        UserActivity.objects.create(user=vinay, product=tech_cluster[1], activity_type='CART_ADD', score_weight=4.0)
        UserActivity.objects.create(user=vinay, product=tech_cluster[4], activity_type='PURCHASE', score_weight=6.0)

        UserActivity.objects.create(user=demo_users["rahul"], product=tech_cluster[0], activity_type='PURCHASE', score_weight=6.0)
        UserActivity.objects.create(user=demo_users["rahul"], product=tech_cluster[6], activity_type='CART_ADD', score_weight=4.0)

        # Pattern 2: Fitness & Fashion Cluster (Priya & Ananya)
        fitness_cluster = [p for p in created_products if p.category.slug in ['fashion', 'sports']]
        for p in fitness_cluster:
            UserActivity.objects.create(user=demo_users["priya"], product=p, activity_type='VIEW', score_weight=1.0)
            UserActivity.objects.create(user=demo_users["ananya"], product=p, activity_type='VIEW', score_weight=1.0)

        UserActivity.objects.create(user=demo_users["priya"], product=fitness_cluster[0], activity_type='PURCHASE', score_weight=6.0)
        UserActivity.objects.create(user=demo_users["priya"], product=fitness_cluster[1], activity_type='WISHLIST_ADD', score_weight=3.0)
        UserActivity.objects.create(user=demo_users["ananya"], product=fitness_cluster[0], activity_type='CART_ADD', score_weight=4.0)

        # Add initial item to Vinay's wishlist
        wishlist, _ = Wishlist.objects.get_or_create(user=vinay)
        WishlistItem.objects.get_or_create(wishlist=wishlist, product=tech_cluster[0])
        WishlistItem.objects.get_or_create(wishlist=wishlist, product=tech_cluster[2])

        # 6. Customer Reviews and Verified Ratings
        reviews_sample = [
            (tech_cluster[0], demo_users["rahul"], 5, "Unbelievable Noise Cancellation", "The dual chip ANC completely blocks out office and airplane drone. Audio fidelity is crisp and bass is deep."),
            (tech_cluster[1], vinay, 5, "Best wireless earbuds on the market", "Spatial audio feels like being in a studio. Seamless device switching between my laptop and phone."),
            (tech_cluster[4], vinay, 5, "Powerhouse laptop for code and ML", "The OLED display is jaw-dropping and handles compilation without throttling."),
            (fitness_cluster[0], demo_users["priya"], 4, "Extremely comfortable road runners", "Ran 10k right out of the box with zero blisters. Highly recommended!"),
            (fitness_cluster[1], demo_users["ananya"], 5, "Lightweight cloud cushioning", "The Ultraboost light midsole delivers crazy energy return.")
        ]

        for prod, usr, rating, title, comment in reviews_sample:
            Review.objects.get_or_create(
                product=prod,
                user=usr,
                defaults={
                    "rating": rating,
                    "title": title,
                    "comment": comment,
                    "is_verified_purchase": True
                }
            )

        # 7. Create Demo Orders for Analytics Dashboard
        order1 = Order.objects.create(
            user=vinay,
            full_name="Vinay Kumar",
            email="vinay@example.com",
            phone="+91 9876543210",
            address="#42, Silicon Residency, Outer Ring Road",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            payment_method="Card",
            payment_status="Paid",
            order_status="Delivered",
            subtotal=tech_cluster[4].discounted_price,
            discount_amount=tech_cluster[4].savings_amount,
            shipping_fee=Decimal("0.00"),
            total_amount=tech_cluster[4].discounted_price
        )
        OrderItem.objects.create(
            order=order1,
            product=tech_cluster[4],
            product_name=tech_cluster[4].name,
            price=tech_cluster[4].discounted_price,
            quantity=1,
            total_price=tech_cluster[4].discounted_price
        )

        order2 = Order.objects.create(
            user=demo_users["priya"],
            full_name="Priya Sharma",
            email="priya@example.com",
            phone="+91 9123456780",
            address="7B Green Glen Layout",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560103",
            payment_method="UPI",
            payment_status="Paid",
            order_status="Shipped",
            subtotal=fitness_cluster[0].discounted_price,
            discount_amount=fitness_cluster[0].savings_amount,
            shipping_fee=Decimal("0.00"),
            total_amount=fitness_cluster[0].discounted_price
        )
        OrderItem.objects.create(
            order=order2,
            product=fitness_cluster[0],
            product_name=fitness_cluster[0].name,
            price=fitness_cluster[0].discounted_price,
            quantity=1,
            total_price=fitness_cluster[0].discounted_price
        )

        # 8. Seed Cross-Platform Deals for all products
        from recommendations.cross_platform import generate_default_platform_deals
        self.stdout.write("Generating cross-platform market deals (Amazon, Flipkart, Croma, Myntra, etc.)...")
        for p in created_products:
            generate_default_platform_deals(p)

        # 9. Trigger Machine Learning Training
        self.stdout.write("Fitting TF-IDF Vectorizer and Collaborative Interaction Matrices...")
        retrain_results = retrain_all_engines()
        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded database! ML Models trained: Content-Based={retrain_results['content_based']}, "
            f"Collaborative={retrain_results['collaborative']}"
        ))
