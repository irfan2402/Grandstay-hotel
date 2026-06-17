from django.db import migrations, models
import rooms.models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=rooms.models.room_image_upload_path,
                help_text='Optional room photo (JPEG/PNG/WebP, max 5 MB)',
            ),
        ),
    ]
