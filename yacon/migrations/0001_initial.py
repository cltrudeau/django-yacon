# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-17 13:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import yacon.sanitizer


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parameters', models.TextField(blank=True, null=True)),
                ('content', yacon.sanitizer.SanitizedTextField()),
            ],
        ),
        migrations.CreateModel(
            name='BlockType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=25, unique=True)),
                ('key', models.CharField(max_length=25, unique=True)),
                ('module_name', models.CharField(max_length=100)),
                ('content_handler_name', models.CharField(max_length=50)),
                ('content_handler_parms', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GroupOfGroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=80, unique=True)),
                ('group_of_groups', models.ManyToManyField(blank=True, to='yacon.GroupOfGroups')),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Group Of Groups',
                'verbose_name_plural': 'Group Of Groups',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=25)),
                ('identifier', models.CharField(max_length=25, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('link', models.TextField(blank=True)),
                ('requires_login', models.BooleanField(default=False)),
                ('requires_admin', models.BooleanField(default=False)),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.Menu')),
            ],
        ),
        migrations.CreateModel(
            name='MenuItemTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='yacon.Language')),
                ('menuitem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.MenuItem')),
            ],
        ),
        migrations.CreateModel(
            name='MetaPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_node_default', models.BooleanField(default=False)),
                ('permission', models.CharField(choices=[('inh', 'Inherit'), ('log', 'Login'), ('own', 'Owner'), ('pub', 'Public')], default='inh', max_length=3)),
                ('hidden', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'MetaPage',
            },
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('permission', models.CharField(choices=[('inh', 'Inherit'), ('log', 'Login'), ('pub', 'Public')], default='inh', max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='NodeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30)),
                ('slug', models.CharField(max_length=25)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='yacon.Language')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.Node')),
            ],
        ),
        migrations.CreateModel(
            name='OwnedGroupOfGroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=80)),
                ('group_of_groups', models.ManyToManyField(blank=True, to='yacon.GroupOfGroups')),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ownedgroupofgroups_owner_set', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'MetaPage',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('slug', models.CharField(max_length=25)),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('blocks', models.ManyToManyField(to='yacon.Block')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='yacon.Language')),
                ('metapage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.MetaPage')),
            ],
        ),
        migrations.CreateModel(
            name='PageType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=25, unique=True)),
                ('template', models.CharField(blank=True, max_length=50)),
                ('dynamic', models.CharField(blank=True, max_length=100)),
                ('block_types', models.ManyToManyField(to='yacon.BlockType')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=25, unique=True)),
                ('domain', models.CharField(max_length=100, unique=True)),
                ('alternate_language', models.ManyToManyField(related_name='_site_alternate_language_+', to='yacon.Language')),
                ('default_language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='yacon.Language')),
                ('doc_root', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='yacon.Node')),
                ('menus', models.ManyToManyField(blank=True, related_name='_site_menus_+', to='yacon.Node')),
            ],
        ),
        migrations.CreateModel(
            name='SiteConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=100)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.Site')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.Site')),
            ],
        ),
        migrations.CreateModel(
            name='TagTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('text', models.CharField(max_length=30)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='yacon.Language')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='node',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.Site'),
        ),
        migrations.AddField(
            model_name='metapage',
            name='_page_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='yacon.PageType'),
        ),
        migrations.AddField(
            model_name='metapage',
            name='alias',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='yacon.MetaPage'),
        ),
        migrations.AddField(
            model_name='metapage',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.Node'),
        ),
        migrations.AddField(
            model_name='metapage',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='metapage',
            name='tags',
            field=models.ManyToManyField(to='yacon.Tag'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='metapage',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='yacon.MetaPage'),
        ),
        migrations.AddField(
            model_name='menu',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.Site'),
        ),
        migrations.AddField(
            model_name='block',
            name='block_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yacon.BlockType'),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('slug', 'metapage')]),
        ),
    ]
