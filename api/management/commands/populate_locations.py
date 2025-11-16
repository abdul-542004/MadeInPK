from django.core.management.base import BaseCommand
from api.models import Province, City


class Command(BaseCommand):
    help = 'Populate database with Pakistan provinces and cities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force repopulation even if data exists',
        )

    def handle(self, *args, **options):
        self.stdout.write('Populating provinces and cities...')

        # Check if data already exists
        if Province.objects.exists() and not options['force']:
            self.stdout.write(
                self.style.WARNING('⚠️  Provinces already exist. Use --force to repopulate.')
            )
            return

        if options['force']:
            self.stdout.write(self.style.WARNING('Clearing existing provinces and cities...'))
            Province.objects.all().delete()
            City.objects.all().delete()

        # Create provinces and cities
        self.create_locations()

        self.stdout.write(
            self.style.SUCCESS('✓ Successfully populated provinces and cities!')
        )

    def create_locations(self):
        """Create Pakistan provinces and cities"""
        
        # Provinces data
        provinces_data = [
            'Punjab',
            'Sindh',
            'Khyber Pakhtunkhwa',
            'Balochistan',
            'Islamabad Capital Territory',
            'Gilgit-Baltistan',
            'Azad Jammu and Kashmir'
        ]

        provinces = []
        for name in provinces_data:
            province, created = Province.objects.get_or_create(name=name)
            provinces.append(province)
            if created:
                self.stdout.write(f'  ✓ Created province: {name}')

        # Cities data organized by province
        cities_data = {
            'Punjab': [
                'Lahore', 'Faisalabad', 'Rawalpindi', 'Multan', 'Gujranwala',
                'Sialkot', 'Bahawalpur', 'Sargodha', 'Sheikhupura', 'Jhang',
                'Gujrat', 'Kasur', 'Rahim Yar Khan', 'Sahiwal', 'Okara',
                'Wah Cantonment', 'Dera Ghazi Khan', 'Mirpur Khas', 'Chiniot',
                'Kamoke', 'Mandi Burewala', 'Jhelum', 'Sadiqabad', 'Khanewal',
                'Hafizabad', 'Khanpur', 'Muzaffargarh', 'Vehari', 'Gojra',
                'Mandi Bahauddin'
            ],
            'Sindh': [
                'Karachi', 'Hyderabad', 'Sukkur', 'Larkana', 'Nawabshah',
                'Mirpur Khas', 'Jacobabad', 'Shikarpur', 'Khairpur', 'Dadu',
                'Thatta', 'Badin', 'Tando Adam', 'Tando Muhammad Khan',
                'Umerkot', 'Sanghar', 'Jamshoro', 'Naushahro Feroze',
                'Matiari', 'Ghotki'
            ],
            'Khyber Pakhtunkhwa': [
                'Peshawar', 'Mardan', 'Mingora', 'Kohat', 'Abbottabad',
                'Mansehra', 'Dera Ismail Khan', 'Swabi', 'Charsadda',
                'Nowshera', 'Bannu', 'Haripur', 'Karak', 'Lakki Marwat',
                'Tank', 'Hangu', 'Chitral', 'Dir', 'Battagram', 'Shangla'
            ],
            'Balochistan': [
                'Quetta', 'Turbat', 'Sibi', 'Khuzdar', 'Zhob', 'Gwadar',
                'Chaman', 'Loralai', 'Hub', 'Pishin', 'Dera Murad Jamali',
                'Dera Allah Yar', 'Kalat', 'Mastung', 'Nushki', 'Kharan',
                'Panjgur', 'Awaran', 'Lasbela', 'Jhal Magsi'
            ],
            'Islamabad Capital Territory': [
                'Islamabad'
            ],
            'Gilgit-Baltistan': [
                'Gilgit', 'Skardu', 'Chilas', 'Hunza', 'Ghanche', 'Khaplu',
                'Shigar', 'Astore', 'Gahkuch', 'Diamir'
            ],
            'Azad Jammu and Kashmir': [
                'Muzaffarabad', 'Mirpur', 'Rawalakot', 'Kotli', 'Bagh',
                'Bhimber', 'Palandri', 'Hattian Bala', 'Hajira', 'Poonch'
            ]
        }

        # Create cities
        total_cities = 0
        for province_name, cities in cities_data.items():
            province = Province.objects.get(name=province_name)
            for city_name in cities:
                city, created = City.objects.get_or_create(
                    name=city_name,
                    province=province
                )
                if created:
                    total_cities += 1

        self.stdout.write(f'\n  ✓ Created {total_cities} cities across {len(provinces_data)} provinces')
        
        # Summary
        self.stdout.write('\n📊 Summary:')
        for province in provinces:
            city_count = province.cities.count()
            self.stdout.write(f'  • {province.name}: {city_count} cities')
