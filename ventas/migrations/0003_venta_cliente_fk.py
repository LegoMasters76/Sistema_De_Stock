from django.db import migrations, models
import django.db.models.deletion


def convertir_clientes(apps, schema_editor):
    Cliente = apps.get_model('ventas', 'Cliente')
    Venta = apps.get_model('ventas', 'Venta')
    for venta in Venta.objects.all().iterator():
        nombre = (venta.cliente or '').strip() or 'Consumidor final'
        cliente, _ = Cliente.objects.get_or_create(nombre=nombre)
        Venta.objects.filter(pk=venta.pk).update(cliente_fk=cliente.pk)


class Migration(migrations.Migration):
    dependencies = [
        ('ventas', '0002_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='cliente_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ventas_migracion', to='ventas.cliente'),
        ),
        migrations.RunPython(convertir_clientes, migrations.RunPython.noop),
        migrations.RemoveField(model_name='venta', name='cliente'),
        migrations.RenameField(model_name='venta', old_name='cliente_fk', new_name='cliente'),
        migrations.AlterField(
            model_name='venta',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ventas', to='ventas.cliente'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='vendedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='account.perfil'),
        ),
        migrations.AlterField(
            model_name='detalle_venta',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Stock.producto'),
        ),
    ]
