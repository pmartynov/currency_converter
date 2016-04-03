# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Currency'
        db.create_table(u'converter_app_currency', (
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=3, primary_key=True)),
            ('long_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'converter_app', ['Currency'])

        # Adding model 'ExchangeRate'
        db.create_table(u'converter_app_exchangerate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('currency_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['converter_app.Currency'])),
            ('currency_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['converter_app.Currency'])),
            ('rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=24, decimal_places=12, blank=True)),
        ))
        db.send_create_signal(u'converter_app', ['ExchangeRate'])

        # Adding unique constraint on 'ExchangeRate', fields ['currency_from', 'currency_to']
        db.create_unique(u'converter_app_exchangerate', ['currency_from_id', 'currency_to_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ExchangeRate', fields ['currency_from', 'currency_to']
        db.delete_unique(u'converter_app_exchangerate', ['currency_from_id', 'currency_to_id'])

        # Deleting model 'Currency'
        db.delete_table(u'converter_app_currency')

        # Deleting model 'ExchangeRate'
        db.delete_table(u'converter_app_exchangerate')


    models = {
        u'converter_app.currency': {
            'Meta': {'ordering': "('short_name',)", 'object_name': 'Currency'},
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '3', 'primary_key': 'True'})
        },
        u'converter_app.exchangerate': {
            'Meta': {'ordering': "('currency_from', 'currency_to')", 'unique_together': "(('currency_from', 'currency_to'),)", 'object_name': 'ExchangeRate'},
            'currency_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['converter_app.Currency']"}),
            'currency_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['converter_app.Currency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '24', 'decimal_places': '12', 'blank': 'True'})
        }
    }

    complete_apps = ['converter_app']