from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from decimal import Decimal
from urllib.request import urlopen
from urllib.parse import quote_plus

from store.models import Category, Product


class Command(BaseCommand):
    help = 'Seed sample products with images downloaded from placeholder service'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=3, help='Number of sample products to create')

    def handle(self, *args, **options):
        count = options['count']
        category, _ = Category.objects.get_or_create(name='Sample', slug='sample')

        for i in range(1, count + 1):
            name = f'Sample Product {i}'
            slug = f'sample-product-{i}'
            defaults = {
                'category': category,
                'name': name,
                'description': f'Sample product {i} description',
                'price': Decimal('9.99') + Decimal(i),
                'stock': 10 + i,
            }

            product, created = Product.objects.get_or_create(slug=slug, defaults=defaults)

            # Attach or generate an image if missing
            if not product.image:
                image_url = f'https://via.placeholder.com/800x600.png?text={quote_plus(name)}'
                try:
                    data = urlopen(image_url, timeout=10).read()
                    product.image.save(f'{slug}.png', ContentFile(data), save=True)
                    self.stdout.write(self.style.SUCCESS(f'Created {name} with downloaded image'))
                except Exception as e:
                    # Try to generate a simple image with PIL, else fall back to a tiny transparent PNG
                    try:
                        from PIL import Image, ImageDraw, ImageFont
                        import io
                        img = Image.new('RGB', (800, 600), color=(200, 200, 200))
                        draw = ImageDraw.Draw(img)
                        try:
                            font = ImageFont.truetype('arial.ttf', 40)
                        except Exception:
                            font = None
                        text = name
                        w, h = draw.textsize(text, font=font)
                        draw.text(((800 - w) / 2, (600 - h) / 2), text, fill=(20, 20, 20), font=font)
                        buf = io.BytesIO()
                        img.save(buf, format='PNG')
                        product.image.save(f'{slug}.png', ContentFile(buf.getvalue()), save=True)
                        self.stdout.write(self.style.SUCCESS(f'Created {name} with generated image (PIL)'))
                    except Exception:
                        # tiny 1x1 transparent PNG as a last-resort fallback
                        transparent_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'
                        product.image.save(f'{slug}.png', ContentFile(transparent_png), save=True)
                        self.stdout.write(self.style.SUCCESS(f'Created {name} with fallback transparent image'))
            else:
                self.stdout.write(f'{name} already exists and has an image')
