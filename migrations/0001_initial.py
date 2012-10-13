# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Language'
        db.create_table('yacon_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('identifier', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25)),
        ))
        db.send_create_signal('yacon', ['Language'])

        # Adding model 'GroupOfGroups'
        db.create_table('yacon_groupofgroups', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
        ))
        db.send_create_signal('yacon', ['GroupOfGroups'])

        # Adding M2M table for field users on 'GroupOfGroups'
        db.create_table('yacon_groupofgroups_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('groupofgroups', models.ForeignKey(orm['yacon.groupofgroups'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('yacon_groupofgroups_users', ['groupofgroups_id', 'user_id'])

        # Adding M2M table for field groups on 'GroupOfGroups'
        db.create_table('yacon_groupofgroups_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('groupofgroups', models.ForeignKey(orm['yacon.groupofgroups'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('yacon_groupofgroups_groups', ['groupofgroups_id', 'group_id'])

        # Adding M2M table for field group_of_groups on 'GroupOfGroups'
        db.create_table('yacon_groupofgroups_group_of_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_groupofgroups', models.ForeignKey(orm['yacon.groupofgroups'], null=False)),
            ('to_groupofgroups', models.ForeignKey(orm['yacon.groupofgroups'], null=False))
        ))
        db.create_unique('yacon_groupofgroups_group_of_groups', ['from_groupofgroups_id', 'to_groupofgroups_id'])

        # Adding model 'OwnedGroupOfGroups'
        db.create_table('yacon_ownedgroupofgroups', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ownedgroupofgroups_owner_set', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('yacon', ['OwnedGroupOfGroups'])

        # Adding M2M table for field users on 'OwnedGroupOfGroups'
        db.create_table('yacon_ownedgroupofgroups_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ownedgroupofgroups', models.ForeignKey(orm['yacon.ownedgroupofgroups'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('yacon_ownedgroupofgroups_users', ['ownedgroupofgroups_id', 'user_id'])

        # Adding M2M table for field groups on 'OwnedGroupOfGroups'
        db.create_table('yacon_ownedgroupofgroups_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ownedgroupofgroups', models.ForeignKey(orm['yacon.ownedgroupofgroups'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('yacon_ownedgroupofgroups_groups', ['ownedgroupofgroups_id', 'group_id'])

        # Adding M2M table for field group_of_groups on 'OwnedGroupOfGroups'
        db.create_table('yacon_ownedgroupofgroups_group_of_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ownedgroupofgroups', models.ForeignKey(orm['yacon.ownedgroupofgroups'], null=False)),
            ('groupofgroups', models.ForeignKey(orm['yacon.groupofgroups'], null=False))
        ))
        db.create_unique('yacon_ownedgroupofgroups_group_of_groups', ['ownedgroupofgroups_id', 'groupofgroups_id'])

        # Adding model 'PageType'
        db.create_table('yacon_pagetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('dynamic', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('yacon', ['PageType'])

        # Adding M2M table for field block_types on 'PageType'
        db.create_table('yacon_pagetype_block_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pagetype', models.ForeignKey(orm['yacon.pagetype'], null=False)),
            ('blocktype', models.ForeignKey(orm['yacon.blocktype'], null=False))
        ))
        db.create_unique('yacon_pagetype_block_types', ['pagetype_id', 'blocktype_id'])

        # Adding model 'BlockType'
        db.create_table('yacon_blocktype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25)),
            ('module_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('content_handler_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('content_handler_parms', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('yacon', ['BlockType'])

        # Adding model 'Block'
        db.create_table('yacon_block', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('block_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.BlockType'])),
            ('parameters', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('content', self.gf('sanitizer.models.SanitizedTextField')()),
        ))
        db.send_create_signal('yacon', ['Block'])

        # Adding model 'Page'
        db.create_table('yacon_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['yacon.Language'])),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('metapage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.MetaPage'])),
        ))
        db.send_create_signal('yacon', ['Page'])

        # Adding unique constraint on 'Page', fields ['slug', 'metapage']
        db.create_unique('yacon_page', ['slug', 'metapage_id'])

        # Adding M2M table for field blocks on 'Page'
        db.create_table('yacon_page_blocks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('page', models.ForeignKey(orm['yacon.page'], null=False)),
            ('block', models.ForeignKey(orm['yacon.block'], null=False))
        ))
        db.create_unique('yacon_page_blocks', ['page_id', 'block_id'])

        # Adding model 'MetaPage'
        db.create_table('yacon_metapage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.Node'])),
            ('_page_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.PageType'], null=True, blank=True)),
            ('alias', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.MetaPage'], null=True, blank=True)),
            ('is_node_default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('yacon', ['MetaPage'])

        # Adding model 'Node'
        db.create_table('yacon_node', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('depth', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('numchild', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.Site'])),
        ))
        db.send_create_signal('yacon', ['Node'])

        # Adding model 'NodeTranslation'
        db.create_table('yacon_nodetranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['yacon.Language'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.Node'])),
        ))
        db.send_create_signal('yacon', ['NodeTranslation'])

        # Adding model 'MenuItem'
        db.create_table('yacon_menuitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('depth', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('numchild', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('metapage', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['yacon.MetaPage'], unique=True, null=True, blank=True)),
            ('menu', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.Menu'])),
        ))
        db.send_create_signal('yacon', ['MenuItem'])

        # Adding model 'Menu'
        db.create_table('yacon_menu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.Site'])),
        ))
        db.send_create_signal('yacon', ['Menu'])

        # Adding model 'MenuItemTranslation'
        db.create_table('yacon_menuitemtranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['yacon.Language'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('menuitem', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.MenuItem'])),
        ))
        db.send_create_signal('yacon', ['MenuItemTranslation'])

        # Adding model 'Site'
        db.create_table('yacon_site', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25)),
            ('domain', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('doc_root', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['yacon.Node'])),
            ('default_language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['yacon.Language'])),
        ))
        db.send_create_signal('yacon', ['Site'])

        # Adding M2M table for field menus on 'Site'
        db.create_table('yacon_site_menus', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('site', models.ForeignKey(orm['yacon.site'], null=False)),
            ('node', models.ForeignKey(orm['yacon.node'], null=False))
        ))
        db.create_unique('yacon_site_menus', ['site_id', 'node_id'])

        # Adding M2M table for field alternate_language on 'Site'
        db.create_table('yacon_site_alternate_language', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('site', models.ForeignKey(orm['yacon.site'], null=False)),
            ('language', models.ForeignKey(orm['yacon.language'], null=False))
        ))
        db.create_unique('yacon_site_alternate_language', ['site_id', 'language_id'])

        # Adding model 'SiteConfig'
        db.create_table('yacon_siteconfig', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yacon.Site'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('yacon', ['SiteConfig'])

        # Adding model 'UserProfile'
        db.create_table('yacon_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('yacon', ['UserProfile'])


    def backwards(self, orm):
        # Removing unique constraint on 'Page', fields ['slug', 'metapage']
        db.delete_unique('yacon_page', ['slug', 'metapage_id'])

        # Deleting model 'Language'
        db.delete_table('yacon_language')

        # Deleting model 'GroupOfGroups'
        db.delete_table('yacon_groupofgroups')

        # Removing M2M table for field users on 'GroupOfGroups'
        db.delete_table('yacon_groupofgroups_users')

        # Removing M2M table for field groups on 'GroupOfGroups'
        db.delete_table('yacon_groupofgroups_groups')

        # Removing M2M table for field group_of_groups on 'GroupOfGroups'
        db.delete_table('yacon_groupofgroups_group_of_groups')

        # Deleting model 'OwnedGroupOfGroups'
        db.delete_table('yacon_ownedgroupofgroups')

        # Removing M2M table for field users on 'OwnedGroupOfGroups'
        db.delete_table('yacon_ownedgroupofgroups_users')

        # Removing M2M table for field groups on 'OwnedGroupOfGroups'
        db.delete_table('yacon_ownedgroupofgroups_groups')

        # Removing M2M table for field group_of_groups on 'OwnedGroupOfGroups'
        db.delete_table('yacon_ownedgroupofgroups_group_of_groups')

        # Deleting model 'PageType'
        db.delete_table('yacon_pagetype')

        # Removing M2M table for field block_types on 'PageType'
        db.delete_table('yacon_pagetype_block_types')

        # Deleting model 'BlockType'
        db.delete_table('yacon_blocktype')

        # Deleting model 'Block'
        db.delete_table('yacon_block')

        # Deleting model 'Page'
        db.delete_table('yacon_page')

        # Removing M2M table for field blocks on 'Page'
        db.delete_table('yacon_page_blocks')

        # Deleting model 'MetaPage'
        db.delete_table('yacon_metapage')

        # Deleting model 'Node'
        db.delete_table('yacon_node')

        # Deleting model 'NodeTranslation'
        db.delete_table('yacon_nodetranslation')

        # Deleting model 'MenuItem'
        db.delete_table('yacon_menuitem')

        # Deleting model 'Menu'
        db.delete_table('yacon_menu')

        # Deleting model 'MenuItemTranslation'
        db.delete_table('yacon_menuitemtranslation')

        # Deleting model 'Site'
        db.delete_table('yacon_site')

        # Removing M2M table for field menus on 'Site'
        db.delete_table('yacon_site_menus')

        # Removing M2M table for field alternate_language on 'Site'
        db.delete_table('yacon_site_alternate_language')

        # Deleting model 'SiteConfig'
        db.delete_table('yacon_siteconfig')

        # Deleting model 'UserProfile'
        db.delete_table('yacon_userprofile')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'yacon.block': {
            'Meta': {'object_name': 'Block'},
            'block_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.BlockType']"}),
            'content': ('sanitizer.models.SanitizedTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.blocktype': {
            'Meta': {'object_name': 'BlockType'},
            'content_handler_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'content_handler_parms': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'module_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.groupofgroups': {
            'Meta': {'object_name': 'GroupOfGroups'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group_of_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['yacon.GroupOfGroups']", 'symmetrical': 'False', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'yacon.language': {
            'Meta': {'object_name': 'Language'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.menu': {
            'Meta': {'object_name': 'Menu'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.Site']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.menuitem': {
            'Meta': {'object_name': 'MenuItem'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.Menu']"}),
            'metapage': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['yacon.MetaPage']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.menuitemtranslation': {
            'Meta': {'object_name': 'MenuItemTranslation'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['yacon.Language']"}),
            'menuitem': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.MenuItem']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.metapage': {
            'Meta': {'object_name': 'MetaPage'},
            '_page_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.PageType']", 'null': 'True', 'blank': 'True'}),
            'alias': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.MetaPage']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_node_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.Node']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.node': {
            'Meta': {'object_name': 'Node'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.Site']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.nodetranslation': {
            'Meta': {'object_name': 'NodeTranslation'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['yacon.Language']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.Node']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.ownedgroupofgroups': {
            'Meta': {'object_name': 'OwnedGroupOfGroups'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group_of_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['yacon.GroupOfGroups']", 'symmetrical': 'False', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ownedgroupofgroups_owner_set'", 'to': "orm['auth.User']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'yacon.page': {
            'Meta': {'unique_together': "(('slug', 'metapage'),)", 'object_name': 'Page'},
            'blocks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['yacon.Block']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['yacon.Language']"}),
            'metapage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.MetaPage']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.pagetype': {
            'Meta': {'object_name': 'PageType'},
            'block_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['yacon.BlockType']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dynamic': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.site': {
            'Meta': {'object_name': 'Site'},
            'alternate_language': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': "orm['yacon.Language']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['yacon.Language']"}),
            'doc_root': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['yacon.Node']"}),
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menus': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yacon.Node']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yacon.siteconfig': {
            'Meta': {'object_name': 'SiteConfig'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yacon.Site']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'yacon.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['yacon']