# Generated by Django 5.1.6 on 2025-03-14 20:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0009_projectrequest_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('section_key', models.CharField(max_length=50, unique=True)),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('signed_by_client', models.BooleanField(default=False)),
                ('signed_by_developer', models.BooleanField(default=False)),
                ('client_signature_date', models.DateTimeField(blank=True, null=True)),
                ('developer_signature_date', models.DateTimeField(blank=True, null=True)),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='projects.projectrequest')),
            ],
        ),
        migrations.CreateModel(
            name='ContractSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('editable', models.BooleanField(default=True)),
                ('order', models.IntegerField()),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='contracts.contract')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='contracts.contracttemplate')),
            ],
        ),
    ]
