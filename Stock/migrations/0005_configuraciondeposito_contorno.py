from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stock', '0004_alter_configuraciondeposito_ancho_px_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuraciondeposito',
            name='contorno',
            field=models.JSONField(blank=True, default=list),
        ),
    ]