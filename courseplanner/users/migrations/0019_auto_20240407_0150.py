# Generated by Django 3.1.1 on 2024-04-07 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_remove_usercourse_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercourse',
            name='grade',
            field=models.CharField(choices=[('A', 'A'), ('A-', 'A-'), ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'), ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'), ('D+', 'D+'), ('D', 'D'), ('F', 'F'), ('P', 'Pass'), ('W', 'Withdraw'), ('CR', 'Credit'), ('I', 'Incomplete'), ('WF', 'Withdraw Fail'), ('WP', 'Withdraw Pass')], max_length=2, null=True, verbose_name='Grade'),
        ),
    ]
