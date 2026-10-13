import os
import django
import requests
from PIL import Image
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Product
from django.conf import settings

# Directory for media products
media_products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
os.makedirs(media_products_dir, exist_ok=True)

# Curated, verified product photography URLs for every single product category and title
PRODUCT_IMAGE_MAP = {
    # --- AUDIO & WEARABLES ---
    "Sony WH-1000XM5 Wireless Noise-Cancelling Headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
    "Apple AirPods Pro (2nd Gen) with MagSafe Case (USB-C)": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&auto=format&fit=crop&q=80",
    "Apple AirPods Pro (2nd Generation) with MagSafe Case": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&auto=format&fit=crop&q=80",
    "Bose QuietComfort 45 Bluetooth Headphones": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop&q=80",
    "Bose QuietComfort Ultra Wireless Over-Ear Headphones": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop&q=80",
    "JBL Flip 6 Portable Waterproof Bluetooth Speaker": "https://images.unsplash.com/photo-1589003077984-894e133dabab?w=800&auto=format&fit=crop&q=80",
    "JBL Charge 5 Portable Waterproof Bluetooth Speaker with Powerbank": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=800&auto=format&fit=crop&q=80",
    "Samsung Galaxy Buds2 Pro True Wireless Bluetooth Earbuds": "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=800&auto=format&fit=crop&q=80",
    "Anker Soundcore Space One Adaptive ANC Wireless Headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
    "Apple AirPods Max Wireless Over-Ear Headphones (Space Gray)": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop&q=80",
    "Bose SoundLink Flex Bluetooth Portable Waterproof Speaker": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop&q=80",
    "Sony WF-1000XM5 Truly Wireless Noise Cancelling Earbuds": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80",
    "Sennheiser Momentum 4 Wireless ANC Headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
    "Marshall Stanmore III Bluetooth Home Speaker": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop&q=80",
    "Sony SRS-XG300 X-Series Portable Wireless Speaker": "https://images.unsplash.com/photo-1589003077984-894e133dabab?w=800&auto=format&fit=crop&q=80",
    "Bose QuietComfort Earbuds II (Triple Black)": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80",
    "JBL Live Pro 2 True Wireless Noise Cancelling Earbuds": "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=800&auto=format&fit=crop&q=80",
    "Apple Beats Studio Pro Wireless Noise Cancelling Headphones": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop&q=80",
    "Anker Soundcore Motion Boom Plus 80W Outdoor Speaker": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=800&auto=format&fit=crop&q=80",
    "Samsung Galaxy Watch 6 Classic 47mm (Rotating Bezel, Bluetooth)": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80",
    "Sony LinkBuds S Ultra Lightweight Truly Wireless Earbuds": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80",
    "Garmin Forerunner 265 AMOLED GPS Running Smartwatch": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=800&auto=format&fit=crop&q=80",

    # --- COMPUTERS & LAPTOPS & PERIPHERALS ---
    "Dell XPS 15 InfinityEdge OLED Laptop": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&auto=format&fit=crop&q=80",
    "Apple MacBook Air 15-inch M3 Chip (Midnight)": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80",
    "Apple MacBook Air 13.6\" M2 Chip (8GB RAM, 256GB SSD - Midnight)": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&auto=format&fit=crop&q=80",
    "Apple MacBook Pro 14\" M3 Pro Chip (18GB Unified Memory, 512GB SSD)": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80",
    "Dell XPS 13 Plus 9320 (Intel Core i7 13th Gen, 16GB, 1TB SSD)": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&auto=format&fit=crop&q=80",
    "Dell Inspiron 16 Plus (Core i7 13th Gen, 16GB RAM, RTX 4050)": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=80",
    "Asus Zenbook 14 OLED Ultra Slim (Intel Core Ultra 7, 16GB, 1TB)": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&auto=format&fit=crop&q=80",
    "Asus ROG Zephyrus G16 OLED 240Hz Gaming Laptop (RTX 4070)": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=800&auto=format&fit=crop&q=80",
    "Dell Alienware m16 R2 QHD+ 240Hz Gaming Laptop": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&auto=format&fit=crop&q=80",
    "Apple Mac Studio (M2 Max Chip, 32GB RAM, 512GB SSD)": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80",
    
    # Monitors
    "Asus ROG Swift 27-inch 240Hz Fast IPS Gaming Monitor": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80",
    "Samsung Odyssey G7 32\" Curved 240Hz QLED Gaming Monitor": "https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=800&auto=format&fit=crop&q=80",
    "Dell UltraSharp 27\" 4K USB-C Hub Monitor (U2723QE IPS Black)": "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=800&auto=format&fit=crop&q=80",
    "Asus ProArt Display 27\" 4K HDR Professional Monitor (PA279CV)": "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=800&auto=format&fit=crop&q=80",
    "Samsung ViewFinity S9 27\" 5K IPS Smart Monitor with 4K SlimFit Cam": "https://images.unsplash.com/photo-1551645120-d70bfe84c826?w=800&auto=format&fit=crop&q=80",

    # Peripherals & Storage
    "Logitech MX Master 3S Wireless Performance Ergonomic Mouse": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&auto=format&fit=crop&q=80",
    "Logitech MX Mechanical Wireless Illuminated Keyboard (Tactile Quiet)": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
    "Logitech G PRO X TKL LIGHTSPEED Wireless Mechanical Keyboard": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
    "Asus ROG Harpe Ace Aim Lab Edition Ultralight Wireless Gaming Mouse": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&auto=format&fit=crop&q=80",
    "Apple Magic Trackpad (Multi-Touch Surface, Wireless Bluetooth)": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&auto=format&fit=crop&q=80",
    "Logitech Brio 4K Ultra HD Pro Stream Webcam with HDR": "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?w=800&auto=format&fit=crop&q=80",
    "Samsung 990 PRO 2TB PCIe 4.0 NVMe M.2 Internal SSD with Heatsink": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800&auto=format&fit=crop&q=80",
    "Dell Premier Wireless ANC Headset with Mic Boom (WL7024)": "https://images.unsplash.com/photo-1577174881658-0f30ed549adc?w=800&auto=format&fit=crop&q=80",

    # --- ELECTRONICS & GADGETS ---
    "Apple iPhone 15 Pro Max 256GB (Natural Titanium)": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&auto=format&fit=crop&q=80",
    "Apple iPhone 15 128GB (Blue with Dynamic Island)": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&auto=format&fit=crop&q=80",
    "Samsung Galaxy S24 Ultra 5G (512GB, Titanium Gray with S-Pen)": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800&auto=format&fit=crop&q=80",
    "Samsung Galaxy Z Fold 5 5G (256GB, Icy Blue)": "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=800&auto=format&fit=crop&q=80",
    "Sony Alpha 7 IV Full-Frame Mirrorless Professional Camera": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80",
    "GoPro HERO12 Black Waterproof Action Camera with HDR 5.3K": "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&auto=format&fit=crop&q=80",
    "DJI Mini 4 Pro 4K HDR Camera Foldable Drone (RC 2 Controller)": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=800&auto=format&fit=crop&q=80",
    "Samsung 65\" Neo QLED 4K Smart TV with Dolby Atmos (QN85C)": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&auto=format&fit=crop&q=80",
    "Sony Bravia 55\" 4K Ultra HD Smart Google TV (XR-55A80L OLED)": "https://images.unsplash.com/photo-1461151304267-38535e780c79?w=800&auto=format&fit=crop&q=80",
    "Sony PlayStation 5 Slim Console (1TB SSD, DualSense Controller)": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800&auto=format&fit=crop&q=80",
    "Apple iPad Pro 11\" M2 Chip Liquid Retina Display (128GB)": "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800&auto=format&fit=crop&q=80",
    "Samsung Galaxy Tab S9 Ultra 14.6\" Dynamic AMOLED 2X Display": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&auto=format&fit=crop&q=80",
    "Anker 737 Power Bank (PowerCore 24K, 140W Ultra Fast Charging)": "https://images.unsplash.com/photo-1609592424364-77e8fbdfdbe2?w=800&auto=format&fit=crop&q=80",
    "Anker Prime 20,000mAh Power Bank (200W Output with App Control)": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=800&auto=format&fit=crop&q=80",
    "Anker 3-in-1 MagSafe Fast Wireless Charging Cube for Apple Devices": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&auto=format&fit=crop&q=80",
    "Amazon Kindle Paperwhite Signature Edition 32GB (6.8\" Display)": "https://images.unsplash.com/photo-1592496001020-d31bd830651f?w=800&auto=format&fit=crop&q=80",
    "Apple TV 4K Wi-Fi + Ethernet (128GB Storage, 3rd Generation)": "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=800&auto=format&fit=crop&q=80",
    "Philips Sonicare DiamondClean 9000 Smart Electric Toothbrush": "https://images.unsplash.com/photo-1559591937-e11124b81ef1?w=800&auto=format&fit=crop&q=80",
    "Philips Multigroom Series 9000 All-in-One Trimmer (15-in-1 Kit)": "https://images.unsplash.com/photo-1621607512214-68297480165e?w=800&auto=format&fit=crop&q=80",
    "Samsung Galaxy SmartTag2 Bluetooth Item Tracker (4-Pack)": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&auto=format&fit=crop&q=80",

    # --- FASHION & LIFESTYLE ---
    "Nike Air Jordan 1 Retro High OG Men's Classic Sneakers": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800&auto=format&fit=crop&q=80",
    "Nike Air Force 1 '07 Triple White Classic Basketball Shoes": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&auto=format&fit=crop&q=80",
    "Nike Dunk Low Retro White Black (Panda Colorway)": "https://images.unsplash.com/photo-1597045566677-8cf032ed6634?w=800&auto=format&fit=crop&q=80",
    "Nike Air Max 270 React Athletic Casual Shoes": "https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=800&auto=format&fit=crop&q=80",
    "Nike Tech Hera Chunky Y2K Lifestyle Sneakers": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=800&auto=format&fit=crop&q=80",
    "Adidas Originals Samba OG Leather Casual Shoes (Cloud White)": "https://images.unsplash.com/photo-1582588678413-dbf45f4823e9?w=800&auto=format&fit=crop&q=80",
    "Adidas Originals Superstar Classic Casual Sneakers": "https://images.unsplash.com/photo-1518002171953-a080ee817e1f?w=800&auto=format&fit=crop&q=80",
    "Adidas Ultraboost Light Performance Running Shoes": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&auto=format&fit=crop&q=80",
    "Adidas Stan Smith Primegreen Classic White Sneakers": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800&auto=format&fit=crop&q=80",
    "Adidas Terrex Free Hiker 2.0 Gore-Tex Waterproof Boots": "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=800&auto=format&fit=crop&q=80",
    
    # Apparel (Jackets, Hoodies, Pants, Backpacks)
    "Nike Dri-FIT Tech Fleece Full-Zip Windrunner Hoodie": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop&q=80",
    "Nike Sportswear Club Fleece Pullover Hoodie": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop&q=80",
    "Nike Sportswear Windrunner Men's Hooded Running Jacket": "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=800&auto=format&fit=crop&q=80",
    "Adidas Originals Trefoil Heavyweight Cotton Graphic Hoodie": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=800&auto=format&fit=crop&q=80",
    "Adidas Essentials 3-Stripes Warm-Up Track Jacket": "https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80",
    "Adidas City Escape Casual Utility Cargo Jacket": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&auto=format&fit=crop&q=80",
    "Nike Dri-FIT Academy Pro Soccer Training Pants": "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=800&auto=format&fit=crop&q=80",
    "Adidas Adicolor Classics Beckenbauer Retro Track Pants": "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=800&auto=format&fit=crop&q=80",
    "Nike Club Cargo Fleece Brushed Athletic Sweatpants": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=800&auto=format&fit=crop&q=80",
    "Adidas Tiro 23 League Slim Training Track Pants": "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=800&auto=format&fit=crop&q=80",
    "Nike Heritage Eugene Vintage Laptop Backpack (23L)": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80",

    # --- FITNESS & SPORTS ---
    "Nike Air Zoom Pegasus 40 Road Running Shoes": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80",
    "Nike Metcon 9 Cross-Training & Workout Shoes": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&auto=format&fit=crop&q=80",
    "Nike React Infinity 3 Flyknit Distance Running Shoes": "https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?w=800&auto=format&fit=crop&q=80",
    "Adidas Adizero Adios Pro 3 Marathon Racing Shoes": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800&auto=format&fit=crop&q=80",
    "Adidas Powerlift 5 Weightlifting Cross-Training Shoes": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&auto=format&fit=crop&q=80",
    "Apple Watch Series 9 GPS 45mm (Midnight Aluminum)": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&auto=format&fit=crop&q=80",
    "Apple Watch Ultra 2 GPS + Cellular 49mm Titanium Case": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&auto=format&fit=crop&q=80",
    "Nike Hydro Pro Stainless Steel Insulated 32oz Water Bottle": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&auto=format&fit=crop&q=80",
    "Adidas Steel Hydro Thermal Sports Shaker Bottle (750ml)": "https://images.unsplash.com/photo-1570831739435-6601aa3fa4fb?w=800&auto=format&fit=crop&q=80",
    "Adidas Aeroready Premium Training Yoga Mat (10mm Cushioned)": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=800&auto=format&fit=crop&q=80",
    "Adidas Speed Rope Pro Weighted Bearing Jump Rope": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&auto=format&fit=crop&q=80",
    "Adidas 5kg Cast Iron Hexagonal Gym Dumbbell Pair": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=800&auto=format&fit=crop&q=80",
    "Adidas Performance Adjustable Ankle & Wrist Weights (Pair)": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=800&auto=format&fit=crop&q=80",
    "Adidas High-Resistance Loop Power Bands (3-Piece Set)": "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=800&auto=format&fit=crop&q=80",
    "Nike Push-Up Grip Handles 2.0 (Non-Slip Workout Stands)": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&auto=format&fit=crop&q=80",
    "Nike Recovery Foam Massage Roller (Textured 13-Inch)": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=800&auto=format&fit=crop&q=80",
    "Nike Pro Combat Wrist & Thumb Stabilizer Wrap Support": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&auto=format&fit=crop&q=80",
    "Nike Pro Dri-FIT Tight Compression Athletic Shirt": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&auto=format&fit=crop&q=80",
    "Nike Strike Pro Match Quality Football (Size 5)": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800&auto=format&fit=crop&q=80",
    "Adidas Boxing Speed Gloves with Shock Absorbing Foam (12oz)": "https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=800&auto=format&fit=crop&q=80",
    "Nike Brasilia 9.5 Training Duffel Gym Bag (60L Medium)": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80",
    "Nike Utility Power Graphic Gym Backpack (32L Heavy Duty)": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80",

    # --- SMART HOME & LIVING ---
    "Philips Hue Smart LED Ambient Starter Kit (4 Bulbs + Bridge)": "https://images.unsplash.com/photo-1558002038-1055907df827?w=800&auto=format&fit=crop&q=80",
    "Philips Hue Play White & Color Light Bar (Double Pack)": "https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=800&auto=format&fit=crop&q=80",
    "Philips Smart Wi-Fi LED Lightstrip 2m Base (16 Million Colors)": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=800&auto=format&fit=crop&q=80",
    "Philips Hue Gradient Signe Smart Floor Standing Lamp": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&auto=format&fit=crop&q=80",
    "Philips Hue White & Color Ambiance E27 Smart LED Bulb (9W)": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&auto=format&fit=crop&q=80",
    "Philips Hue Smart Motion Sensor for Indoor Lighting": "https://images.unsplash.com/photo-1558002038-1055907df827?w=800&auto=format&fit=crop&q=80",
    "Philips Smart Wi-Fi 16A Smart Plug with Power Metering": "https://images.unsplash.com/photo-1542435503-956c469947f6?w=800&auto=format&fit=crop&q=80",
    "Philips Smart Air Purifier Series 3000i with HEPA Filter": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&auto=format&fit=crop&q=80",
    "Philips Smart Sunrise Simulation Wake-Up Light Alarm Clock": "https://images.unsplash.com/photo-1507646227500-4d389b0012be?w=800&auto=format&fit=crop&q=80",
    "Philips EasyKey Digital Fingerprint & Touchpad Smart Door Lock": "https://images.unsplash.com/photo-1558002038-1055907df827?w=800&auto=format&fit=crop&q=80",
    "Samsung SmartThings Hub Home Automation Controller v3": "https://images.unsplash.com/photo-1616469829941-c7200edec809?w=800&auto=format&fit=crop&q=80",
    "Samsung SmartThings IoT Station & Wireless Charger Pad": "https://images.unsplash.com/photo-1616469829941-c7200edec809?w=800&auto=format&fit=crop&q=80",
    "Samsung Smart Door Lock with Touchscreen Keypad & RFID": "https://images.unsplash.com/photo-1558002038-1055907df827?w=800&auto=format&fit=crop&q=80",
    "Samsung SmartThings Multipurpose Water Leak & Temperature Sensor": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&auto=format&fit=crop&q=80",
    "Samsung SmartThings Smart Outlet Plug (Zigbee Power Monitoring)": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop&q=80",
    "Anker Eufy RoboVac X8 Hybrid Laser Robot Vacuum & Mop": "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=800&auto=format&fit=crop&q=80",
    "Anker Eufy RoboVac L35 Hybrid+ Self-Emptying Robot Vacuum & Mop": "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=800&auto=format&fit=crop&q=80",
    "Anker Eufy Security 2K Dual Camera Smart Video Doorbell": "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=800&auto=format&fit=crop&q=80",
    "Anker Eufy Security eufyCam 2C Wireless 2-Camera Home Kit": "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=800&auto=format&fit=crop&q=80",
    "Anker Soundcore Wakey All-in-One Smart Bedside Speaker Clock": "https://images.unsplash.com/photo-1507646227500-4d389b0012be?w=800&auto=format&fit=crop&q=80",
    "Anker Eufy Smart Scale P2 Pro with 16 Body Composition Metrics": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&auto=format&fit=crop&q=80",
    "Anker Nebula Capsule 3 Laser 1080p Smart Portable Mini Projector": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=800&auto=format&fit=crop&q=80",
}

# Generic fallback per keyword for any unmapped or dynamically created product
KEYWORD_FALLBACKS = [
    ("track pant", "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=800&auto=format&fit=crop&q=80"),
    ("sweatpant", "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=800&auto=format&fit=crop&q=80"),
    ("pants", "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=800&auto=format&fit=crop&q=80"),
    ("jacket", "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=800&auto=format&fit=crop&q=80"),
    ("hoodie", "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop&q=80"),
    ("shoe", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80"),
    ("sneaker", "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&auto=format&fit=crop&q=80"),
    ("boot", "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=800&auto=format&fit=crop&q=80"),
    ("backpack", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80"),
    ("bag", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80"),
    ("toothbrush", "https://images.unsplash.com/photo-1559591937-e11124b81ef1?w=800&auto=format&fit=crop&q=80"),
    ("trimmer", "https://images.unsplash.com/photo-1621607512214-68297480165e?w=800&auto=format&fit=crop&q=80"),
    ("headphone", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80"),
    ("earbud", "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80"),
    ("speaker", "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop&q=80"),
    ("watch", "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&auto=format&fit=crop&q=80"),
    ("laptop", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80"),
    ("monitor", "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80"),
    ("mouse", "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&auto=format&fit=crop&q=80"),
    ("keyboard", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80"),
    ("phone", "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&auto=format&fit=crop&q=80"),
    ("camera", "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80"),
    ("drone", "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=800&auto=format&fit=crop&q=80"),
    ("tv", "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&auto=format&fit=crop&q=80"),
    ("tablet", "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800&auto=format&fit=crop&q=80"),
    ("power bank", "https://images.unsplash.com/photo-1609592424364-77e8fbdfdbe2?w=800&auto=format&fit=crop&q=80"),
    ("bottle", "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&auto=format&fit=crop&q=80"),
    ("dumbbell", "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=800&auto=format&fit=crop&q=80"),
    ("vacuum", "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=800&auto=format&fit=crop&q=80"),
    ("robovac", "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=800&auto=format&fit=crop&q=80"),
    ("light", "https://images.unsplash.com/photo-1558002038-1055907df827?w=800&auto=format&fit=crop&q=80"),
    ("bulb", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&auto=format&fit=crop&q=80"),
    ("plug", "https://images.unsplash.com/photo-1542435503-956c469947f6?w=800&auto=format&fit=crop&q=80"),
]

def update_all_database_products():
    total = 0
    updated = 0
    
    for product in Product.objects.all():
        total += 1
        target_url = None
        
        # Exact match
        if product.name in PRODUCT_IMAGE_MAP:
            target_url = PRODUCT_IMAGE_MAP[product.name]
        else:
            # Fallback substring matching
            name_lower = product.name.lower()
            for key, url in PRODUCT_IMAGE_MAP.items():
                if key.lower() in name_lower or name_lower in key.lower():
                    target_url = url
                    break
            if not target_url:
                for kw, url in KEYWORD_FALLBACKS:
                    if kw in name_lower:
                        target_url = url
                        break
        
        if not target_url:
            print(f"Warning: No match for [{product.id}] {product.name}")
            continue

        if product.image_url != target_url:
            print(f"Updating [{product.id}] {product.name}")
            print(f"  Old: {product.image_url}")
            print(f"  New: {target_url}")
            product.image_url = target_url
            product.image = None  # Use crisp remote CDN image
            product.save()
            updated += 1

    print(f"\nAudit complete: Checked {total} products, updated {updated} products.")

if __name__ == "__main__":
    update_all_database_products()
