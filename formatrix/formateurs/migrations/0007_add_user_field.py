# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('formateurs', '0006_alter_formateur_adresse_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='formateur',
            name='user',
            field=models.OneToOneField(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.CASCADE, 
                related_name='formateur_profile', 
                to='auth.user'
            ),
        ),
    ] 