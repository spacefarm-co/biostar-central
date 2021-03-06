# Generated by Django 2.2.7 on 2019-11-11 18:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_shareable'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='root',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='recipes.Analysis'),
        ),
        migrations.AddField(
            model_name='data',
            name='file_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='access',
            name='access',
            field=models.IntegerField(choices=[(1, 'No Access'), (2, 'Read Access'), (3, 'Write Access'), (4, 'Share Access')], db_index=True, default=1),
        ),
        migrations.AlterField(
            model_name='project',
            name='privacy',
            field=models.IntegerField(choices=[(3, 'Private'), (2, 'Shared'), (1, 'Public')], default=3),
        ),
    ]
