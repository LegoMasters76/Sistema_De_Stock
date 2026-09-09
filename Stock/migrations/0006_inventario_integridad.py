from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


def normalizar_tipos(apps, schema_editor):
    Producto = apps.get_model('Stock', 'Producto')
    Producto.objects.filter(stock__lt=0).update(stock=0)
    Movimiento = apps.get_model('Stock', 'MovimientosStock')
    Movimiento.objects.filter(tipo='entrada').update(tipo='ENTRADA')
    Movimiento.objects.filter(tipo='salida').update(tipo='AJUSTE')


class Migration(migrations.Migration):
    dependencies = [
        ('Stock', '0005_configuraciondeposito_contorno'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Stock.categoria'),
        ),
        migrations.AlterField(
            model_name='movimientosstock',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Stock.producto'),
        ),
        migrations.AlterField(
            model_name='movimientosstock',
            name='cantidad',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='movimientosstock',
            name='tipo',
            field=models.CharField(choices=[('VENTA', 'Venta'), ('ENTRADA', 'Entrada'), ('AJUSTE', 'Ajuste'), ('MERMA', 'Merma'), ('TRANSFERENCIA', 'Transferencia')], max_length=20),
        ),
        migrations.AddField(
            model_name='movimientosstock',
            name='referencia',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='movimientosstock',
            name='saldo_resultante',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='movimientosstock',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(normalizar_tipos, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='producto',
            constraint=models.CheckConstraint(condition=Q(('stock__gte', 0)), name='producto_stock_no_negativo'),
        ),
    ]
