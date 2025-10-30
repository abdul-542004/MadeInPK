from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

from api.models import (
    Province, City, Address, Category, Product, ProductImage,
    AuctionListing, Bid, FixedPriceListing, SellerProfile
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with sample data...')

        # Create provinces and cities
        self.create_locations()

        # Create users (buyers and sellers)
        self.create_users()

        # Create categories
        self.create_categories()

        # Create products and listings
        self.create_products_and_listings()

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )

    def create_locations(self):
        """Create sample provinces and cities"""
        self.stdout.write('Creating locations...')

        # Provinces
        provinces_data = [
            'Punjab', 'Sindh', 'Khyber Pakhtunkhwa', 'Balochistan',
            'Islamabad Capital Territory', 'Gilgit-Baltistan', 'Azad Jammu and Kashmir'
        ]

        provinces = []
        for name in provinces_data:
            province, created = Province.objects.get_or_create(name=name)
            provinces.append(province)
            if created:
                self.stdout.write(f'  Created province: {name}')

        # Cities
        cities_data = {
            'Punjab': ['Lahore', 'Faisalabad', 'Rawalpindi', 'Multan', 'Gujranwala', 'Sialkot'],
            'Sindh': ['Karachi', 'Hyderabad', 'Sukkur', 'Larkana', 'Nawabshah'],
            'Khyber Pakhtunkhwa': ['Peshawar', 'Mardan', 'Mingora', 'Kohat', 'Abbottabad'],
            'Balochistan': ['Quetta', 'Turbat', 'Sibi', 'Khuzdar'],
            'Islamabad Capital Territory': ['Islamabad'],
            'Gilgit-Baltistan': ['Gilgit', 'Skardu'],
            'Azad Jammu and Kashmir': ['Muzaffarabad', 'Mirpur']
        }

        for province_name, cities in cities_data.items():
            province = Province.objects.get(name=province_name)
            for city_name in cities:
                city, created = City.objects.get_or_create(
                    name=city_name,
                    province=province
                )
                if created:
                    self.stdout.write(f'  Created city: {city_name}, {province_name}')

    def create_users(self):
        """Create sample users with proper password hashing"""
        self.stdout.write('Creating users...')

        # Sample buyers
        buyers_data = [
            {
                'username': 'buyer1',
                'email': 'buyer1@example.com',
                'first_name': 'Ahmed',
                'last_name': 'Khan',
                'phone_number': '+923001234567',
                'role': 'buyer'
            },
            {
                'username': 'buyer2',
                'email': 'buyer2@example.com',
                'first_name': 'Fatima',
                'last_name': 'Ali',
                'phone_number': '+923011234567',
                'role': 'buyer'
            },
            {
                'username': 'buyer3',
                'email': 'buyer3@example.com',
                'first_name': 'Muhammad',
                'last_name': 'Hassan',
                'phone_number': '+923021234567',
                'role': 'buyer'
            },
            {
                'username': 'buyer_seller1',
                'email': 'buyer_seller1@example.com',
                'first_name': 'Sara',
                'last_name': 'Ahmed',
                'phone_number': '+923031234567',
                'role': 'both'
            }
        ]

        # Sample sellers
        sellers_data = [
            {
                'username': 'seller1',
                'email': 'seller1@example.com',
                'first_name': 'Hassan',
                'last_name': 'Textiles',
                'phone_number': '+923041234567',
                'role': 'seller',
                'brand_name': 'Hassan Textiles',
                'biography': 'Family-owned textile business for 3 generations, specializing in handwoven fabrics.',
                'business_address': '123 Textile Market, Faisalabad, Punjab',
                'website': 'https://hassantextiles.pk',
                'is_verified': True
            },
            {
                'username': 'seller2',
                'email': 'seller2@example.com',
                'first_name': 'Ayesha',
                'last_name': 'Crafts',
                'phone_number': '+923051234567',
                'role': 'seller',
                'brand_name': 'Ayesha Crafts',
                'biography': 'Artisan specializing in traditional Pakistani embroidery and handicrafts.',
                'business_address': '456 Artisan Street, Lahore, Punjab',
                'website': 'https://ayesha-crafts.pk',
                'is_verified': True
            },
            {
                'username': 'seller3',
                'email': 'seller3@example.com',
                'first_name': 'Ahmed',
                'last_name': 'Pottery',
                'phone_number': '+923061234567',
                'role': 'seller',
                'brand_name': 'Ahmed Pottery',
                'biography': 'Master potter creating traditional ceramics using age-old techniques.',
                'business_address': '789 Pottery Lane, Multan, Punjab',
                'is_verified': False
            },
            {
                'username': 'seller4',
                'email': 'seller4@example.com',
                'first_name': 'Zara',
                'last_name': 'Jewelry',
                'phone_number': '+923071234567',
                'role': 'both',
                'brand_name': 'Zara Jewelry',
                'biography': 'Designer creating contemporary jewelry with traditional Pakistani motifs.',
                'business_address': '321 Jewelry Bazaar, Karachi, Sindh',
                'website': 'https://zarajewelry.pk',
                'is_verified': True
            }
        ]

        # Create buyers
        for buyer_data in buyers_data:
            user, created = User.objects.get_or_create(
                username=buyer_data['username'],
                defaults={
                    'email': buyer_data['email'],
                    'first_name': buyer_data['first_name'],
                    'last_name': buyer_data['last_name'],
                    'phone_number': buyer_data['phone_number'],
                    'role': buyer_data['role']
                }
            )
            if created:
                user.set_password('password123')  # Hash the password
                user.save()
                self.stdout.write(f'  Created buyer: {user.username}')

                # Create address for buyer
                self.create_sample_address(user)

        # Create sellers
        for seller_data in sellers_data:
            user, created = User.objects.get_or_create(
                username=seller_data['username'],
                defaults={
                    'email': seller_data['email'],
                    'first_name': seller_data['first_name'],
                    'last_name': seller_data['last_name'],
                    'phone_number': seller_data['phone_number'],
                    'role': seller_data['role']
                }
            )
            if created:
                user.set_password('password123')  # Hash the password
                user.save()

                # Create seller profile
                SellerProfile.objects.create(
                    user=user,
                    brand_name=seller_data['brand_name'],
                    biography=seller_data['biography'],
                    business_address=seller_data['business_address'],
                    website=seller_data.get('website', ''),
                    is_verified=seller_data['is_verified']
                )

                self.stdout.write(f'  Created seller: {user.username} ({seller_data["brand_name"]})')

                # Create address for seller
                self.create_sample_address(user)

    def create_sample_address(self, user):
        """Create a sample address for user"""
        cities = City.objects.all()
        if cities.exists():
            city = random.choice(cities)
            Address.objects.get_or_create(
                user=user,
                street_address=f'{random.randint(1, 999)} {random.choice(["Main Street", "Market Road", "Commercial Area"])}',
                city=city,
                postal_code=f'{random.randint(10000, 99999)}',
                is_default=True
            )

    def create_categories(self):
        """Create product categories"""
        self.stdout.write('Creating categories...')

        categories_data = [
            {'name': 'Textiles', 'description': 'Fabrics, clothing, and textile products'},
            {'name': 'Handicrafts', 'description': 'Handmade decorative items and crafts'},
            {'name': 'Pottery', 'description': 'Ceramic and pottery items'},
            {'name': 'Jewelry', 'description': 'Traditional and contemporary jewelry'},
            {'name': 'Home Decor', 'description': 'Home decoration and furnishing items'},
            {'name': 'Carpets', 'description': 'Handwoven carpets and rugs'},
            {'name': 'Leather Goods', 'description': 'Leather products and accessories'},
            {'name': 'Woodwork', 'description': 'Wooden furniture and carvings'}
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'  Created category: {cat_data["name"]}')

    def create_products_and_listings(self):
        """Create sample products with both auction and fixed price listings"""
        self.stdout.write('Creating products and listings...')

        sellers = User.objects.filter(role__in=['seller', 'both'])

        # Sample products data
        products_data = [
            # Textiles
            {
                'name': 'Handwoven Pashmina Shawl',
                'description': 'Exquisite handwoven pashmina shawl from Kashmir, featuring traditional paisley patterns. Made from the finest cashmere wool, perfect for special occasions.',
                'condition': 'new',
                'category': 'Textiles',
                'seller_username': 'seller1',
                'images': ['pashmina_shawl.jpg'],
                'listing_type': 'auction',
                'starting_price': 2500,
                'duration_hours': 48
            },
            {
                'name': 'Embroidered Cotton Kurti',
                'description': 'Beautiful hand-embroidered cotton kurti with mirror work and traditional motifs. Comfortable for everyday wear.',
                'condition': 'new',
                'category': 'Textiles',
                'seller_username': 'seller1',
                'images': ['embroidered_kurti.jpg'],
                'listing_type': 'fixed_price',
                'price': 1200,
                'quantity': 5
            },
            {
                'name': 'Silk Bedspread Set',
                'description': 'Luxurious silk bedspread with matching pillow covers, handwoven with gold zari work. King size.',
                'condition': 'new',
                'category': 'Textiles',
                'seller_username': 'seller1',
                'images': ['silk_bedspread.jpg'],
                'listing_type': 'auction',
                'starting_price': 8500,
                'duration_hours': 72
            },

            # Handicrafts
            {
                'name': 'Brass Wall Hanging',
                'description': 'Intricately designed brass wall hanging with traditional Islamic calligraphy. Handcrafted by skilled artisans.',
                'condition': 'new',
                'category': 'Handicrafts',
                'seller_username': 'seller2',
                'images': ['brass_wall_hanging.jpg'],
                'listing_type': 'fixed_price',
                'price': 3200,
                'quantity': 3
            },
            {
                'name': 'Wooden Jewelry Box',
                'description': 'Hand-carved sheesham wood jewelry box with brass inlay work. Features multiple compartments and a mirror.',
                'condition': 'new',
                'category': 'Handicrafts',
                'seller_username': 'seller2',
                'images': ['jewelry_box.jpg'],
                'listing_type': 'auction',
                'starting_price': 1800,
                'duration_hours': 24
            },

            # Pottery
            {
                'name': 'Blue Pottery Vase',
                'description': 'Traditional Multani blue pottery vase, hand-painted with floral motifs. Authentic craftsmanship from Multan.',
                'condition': 'new',
                'category': 'Pottery',
                'seller_username': 'seller3',
                'images': ['blue_pottery_vase.jpg'],
                'listing_type': 'fixed_price',
                'price': 950,
                'quantity': 8
            },
            {
                'name': 'Ceramic Dinner Set',
                'description': '16-piece ceramic dinner set with traditional Pakistani designs. Includes plates, bowls, and serving dishes.',
                'condition': 'new',
                'category': 'Pottery',
                'seller_username': 'seller3',
                'images': ['ceramic_dinner_set.jpg'],
                'listing_type': 'auction',
                'starting_price': 4200,
                'duration_hours': 36
            },

            # Jewelry
            {
                'name': 'Silver Enamel Necklace',
                'description': 'Sterling silver necklace with enamel work featuring traditional Pakistani motifs. Handcrafted by master jewelers.',
                'condition': 'new',
                'category': 'Jewelry',
                'seller_username': 'seller4',
                'images': ['silver_necklace.jpg'],
                'listing_type': 'fixed_price',
                'price': 2850,
                'quantity': 2
            },
            {
                'name': 'Gold-Plated Earrings Set',
                'description': 'Elegant gold-plated earrings with semi-precious stones. Contemporary design with traditional elements.',
                'condition': 'new',
                'category': 'Jewelry',
                'seller_username': 'seller4',
                'images': ['gold_earrings.jpg'],
                'listing_type': 'auction',
                'starting_price': 1200,
                'duration_hours': 48
            },

            # Carpets
            {
                'name': 'Kashmiri Silk Carpet',
                'description': 'Handwoven silk carpet from Kashmir, 6x4 feet, with 400 knots per square inch. Features intricate floral medallion design.',
                'condition': 'new',
                'category': 'Carpets',
                'seller_username': 'seller1',
                'images': ['silk_carpet.jpg'],
                'listing_type': 'auction',
                'starting_price': 25000,
                'duration_hours': 96
            },

            # Woodwork
            {
                'name': 'Sheesham Wood Dining Table',
                'description': 'Solid sheesham wood dining table, extends to seat 8 people. Handcrafted with traditional joinery techniques.',
                'condition': 'new',
                'category': 'Woodwork',
                'seller_username': 'seller2',
                'images': ['dining_table.jpg'],
                'listing_type': 'fixed_price',
                'price': 45000,
                'quantity': 1
            }
        ]

        for product_data in products_data:
            try:
                seller = sellers.get(username=product_data['seller_username'])
                category = Category.objects.get(name=product_data['category'])

                # Create product
                product = Product.objects.create(
                    seller=seller,
                    category=category,
                    name=product_data['name'],
                    description=product_data['description'],
                    condition=product_data['condition']
                )

                # Create product images (placeholder URLs for now)
                for image_name in product_data['images']:
                    ProductImage.objects.create(
                        product=product,
                        image=f'products/{image_name}',  # This would be uploaded in real scenario
                        is_primary=True
                    )

                # Create listing
                if product_data['listing_type'] == 'auction':
                    start_time = timezone.now()
                    end_time = start_time + timedelta(hours=product_data['duration_hours'])

                    AuctionListing.objects.create(
                        product=product,
                        starting_price=Decimal(str(product_data['starting_price'])),
                        current_price=Decimal(str(product_data['starting_price'])),
                        start_time=start_time,
                        end_time=end_time,
                        status='active'
                    )
                    self.stdout.write(f'  Created auction: {product.name}')

                elif product_data['listing_type'] == 'fixed_price':
                    FixedPriceListing.objects.create(
                        product=product,
                        price=Decimal(str(product_data['price'])),
                        quantity=product_data['quantity'],
                        status='active'
                    )
                    self.stdout.write(f'  Created fixed price listing: {product.name}')

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  Error creating product {product_data["name"]}: {e}')
                )

        # Create some sample bids for auctions
        self.create_sample_bids()

    def create_sample_bids(self):
        """Create sample bids on auctions"""
        self.stdout.write('Creating sample bids...')

        auctions = AuctionListing.objects.filter(status='active')
        buyers = User.objects.filter(role__in=['buyer', 'both'])

        if not auctions.exists() or not buyers.exists():
            return

        for auction in auctions:
            # Create 2-5 random bids for each auction
            num_bids = random.randint(2, 5)
            bidders = random.sample(list(buyers), min(num_bids, len(buyers)))

            current_price = auction.starting_price
            for bidder in bidders:
                # Bid amount increases by 5-15% each time
                increase_percent = random.uniform(0.05, 0.15)
                bid_amount = current_price * (1 + Decimal(str(increase_percent)))
                bid_amount = bid_amount.quantize(Decimal('0.01'))  # Round to 2 decimal places

                # Mark previous bids as not winning
                Bid.objects.filter(auction=auction, is_winning=True).update(is_winning=False)

                # Create new bid
                bid_time = timezone.now() - timedelta(minutes=random.randint(1, 300))
                Bid.objects.create(
                    auction=auction,
                    bidder=bidder,
                    amount=bid_amount,
                    bid_time=bid_time,
                    is_winning=True
                )

                # Update auction current price
                auction.current_price = bid_amount
                auction.save()

                current_price = bid_amount

            self.stdout.write(f'  Created {num_bids} bids for auction: {auction.product.name}')