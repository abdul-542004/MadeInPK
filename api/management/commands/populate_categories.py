from django.core.management.base import BaseCommand
from api.models import Category


class Command(BaseCommand):
    help = 'Populate database with product categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force repopulation even if data exists',
        )

    def handle(self, *args, **options):
        self.stdout.write('Populating categories...')

        # Check if data already exists
        if Category.objects.exists() and not options['force']:
            self.stdout.write(
                self.style.WARNING('⚠️  Categories already exist. Use --force to repopulate.')
            )
            return

        if options['force']:
            self.stdout.write(self.style.WARNING('Clearing existing categories...'))
            Category.objects.all().delete()

        # Create categories
        self.create_categories()

        self.stdout.write(
            self.style.SUCCESS('✓ Successfully populated categories!')
        )

    def create_categories(self):
        """Create product categories"""
        
        categories_data = [
            {'name': 'Textiles', 'description': 'Fabrics, clothing, and textile products'},
            {'name': 'Handicrafts', 'description': 'Handmade decorative items and crafts'},
            {'name': 'Pottery', 'description': 'Ceramic and pottery items'},
            {'name': 'Jewelry', 'description': 'Traditional and contemporary jewelry'},
            {'name': 'Home Decor', 'description': 'Home decoration and furnishing items'},
            {'name': 'Carpets', 'description': 'Handwoven carpets and rugs'},
            {'name': 'Leather Goods', 'description': 'Leather products and accessories'},
            {'name': 'Woodwork', 'description': 'Wooden furniture and carvings'},
            {'name': 'Metalwork', 'description': 'Metal crafts and decorative items'},
            {'name': 'Paintings & Art', 'description': 'Traditional and contemporary artwork'},
            {'name': 'Footwear', 'description': 'Traditional and handcrafted footwear'},
            {'name': 'Accessories', 'description': 'Fashion and decorative accessories'},
        ]

        created_count = 0
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created category: {cat_data["name"]}')
        
        self.stdout.write(f'\n📊 Total: {created_count} categories created')
