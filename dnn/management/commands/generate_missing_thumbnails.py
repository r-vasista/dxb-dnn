import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from PIL import Image

from post_management.models import NewsPost


THUMBNAIL_SIZE = (400, 300)  # adjust if needed


class Command(BaseCommand):
    help = "Generate WEBP thumbnails for old NewsPosts (post_date >= 2026) where thumbnail is missing"

    def handle(self, *args, **kwargs):
        start_date = make_aware(datetime(2026, 1, 1))

        queryset = NewsPost.objects.filter(
            post_date__gte=start_date,
            post_image__isnull=False
        )

        total = queryset.count()
        created_count = 0
        skipped_count = 0

        self.stdout.write(f"Processing {total} posts...")

        for post in queryset.iterator():  # memory efficient
            try:
                original_path = post.post_image.path

                if not os.path.exists(original_path):
                    skipped_count += 1
                    continue

                root = os.path.dirname(original_path)
                filename = os.path.basename(original_path)

                thumb_dir = os.path.join(root, "thumbnails")
                os.makedirs(thumb_dir, exist_ok=True)

                base_name, _ = os.path.splitext(filename)
                webp_thumb_path = os.path.join(thumb_dir, f"{base_name}.webp")

                # Skip if already exists
                if os.path.exists(webp_thumb_path):
                    skipped_count += 1
                    continue

                # Generate thumbnail
                with Image.open(original_path) as img:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    img.thumbnail(THUMBNAIL_SIZE)

                    img.save(webp_thumb_path, "WEBP", quality=85, method=6)

                created_count += 1

                if created_count % 50 == 0:
                    self.stdout.write(f"Created {created_count} thumbnails...")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error on post {post.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone!\nCreated: {created_count}\nSkipped: {skipped_count}"
        ))