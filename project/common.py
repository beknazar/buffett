from lxml import html
import datetime
import logging
import logging.handlers
import requests

from django.db import models
from django.utils import timezone


def pick(d, *args):
    keys = args
    if len(keys) == 1 and isinstance(keys[0], (list, tuple)):
        keys = keys[0]
    keys = set(keys)
    return dict([(k, v) for k, v in d.iteritems() if k in keys])


class LogMixin(object):
    LOG_FORMAT = u'{label:25} {msg}'

    def __init__(self, *args, **kwargs):
        super(LogMixin, self).__init__(*args, **kwargs)
        self._logger = None
        self._logger_label = None

    def __unicode__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__unicode__()

    @property
    def logger_label(self):
        return (hasattr(self, '_logger_label') and self._logger_label or
                self.__unicode__())

    @property
    def logger(self):
        if not hasattr(self, '_logger') or self._logger is None:
            self._logger = logging.getLogger(self.__class__.__module__)
        return self._logger

    def set_logger_label(self, label):
        self._logger_label = label

    def debug(self, msg):
        self.logger.debug(self.LOG_FORMAT.format(
            label=self.logger_label, msg=msg))

    def info(self, msg):
        self.logger.info(self.LOG_FORMAT.format(
            label=self.logger_label, msg=msg))

    def warn(self, msg):
        self.logger.warn(self.LOG_FORMAT.format(
            label=self.logger_label, msg=msg))

    def error(self, msg):
        self.logger.error(self.LOG_FORMAT.format(
            label=self.logger_label, msg=msg))

    def critical(self, msg):
        self.logger.critical(self.LOG_FORMAT.format(
            label=self.logger_label, msg=msg))


class Script(LogMixin):
    default_header = {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/48.0.2564.116 Safari/537.36'
    }

    def convert_money(self, st):
        if st == '-':
            return 0.0
        mult = 1
        if st[0] == '(':
            mult = -1
            st = st[1:-1]
        end = st[-1]

        num_part = st[:-1]
        if end == 'B':
            mult *= 10**9
        elif end == 'M':
            mult *= 10**6
        else:
            num_part = st.replace(',', '')
        try:
            return float(num_part) * mult
        except ValueError:
            self.warn('ValueError: {0}'.format(st))
        return None

    def request(self, method, url, data=None, stream=False):
        r = None
        try:
            if method == 'post':
                r = self.client.post(url, data=data,
                                     headers=self.default_header)
            else:
                r = self.client.get(url, headers=self.default_header,
                                    stream=stream)
        except requests.exceptions.ConnectionError as e:
            self.warn('Error inside request: {0}'.format(e))
        return r

    def get_tree(self, url):
        r = self.request('get', url)
        self.default_header = r.request.headers
        return html.fromstring(r.content)


# Base Mixins
# ===========


class UpdateMixin(object):
    def update(self, **kwargs):
        fields = self._meta.fields
        field_dict = dict(reduce(list.__add__, [
            [(field.name, field), (field.get_attname(), field)]
            for field in fields]))
        field_names = set(reduce(list.__add__, [
            [field.name, field.get_attname()] for field in fields], []))

        kwargs = pick(kwargs, *field_names)

        if kwargs:
            update_fields = []
            for key, value in kwargs.iteritems():
                convert = field_dict[key].to_python
                if convert(value) != convert(getattr(self, key)):
                    setattr(self, key, value)
                    update_fields.append(key)
            if update_fields:
                self.save(update_fields=update_fields)
                return True
            else:
                return False


class JSONMixin(object):
    def for_json(self, excludes=None):
        data = {}
        for field in self._meta.local_fields:
            if isinstance(field, RelatedField):
                data[field.attname] = getattr(self, field.attname)
            else:
                name = field.name
                if excludes and name in excludes:
                    continue
                value = getattr(self, name)
                if not isinstance(value, models.Model):
                    data[name] = value
        return data


class IncrementMixin(object):
    def get_incrementer(self, reverse=False):
        return Incrementer(reverse)


class BaseMixin(LogMixin, IncrementMixin, JSONMixin, UpdateMixin):
    def __unicode__(self):
        return unicode(self._meta.verbose_name)

    @classmethod
    def get_model_type(cls):
        return camel_to_underscore(cls.__name__)

    @property
    def model_type(self):
        return self.get_model_type()

    def reload(self):
        return self._default_manager.get(pk=self.pk)

    def patch(self, **update_fields):
        return self._default_manager.filter(pk=self.pk).update(**update_fields)


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True,
                                      editable=False)
    updated_at = models.DateTimeField(default=timezone.now, db_index=True,
                                      editable=False)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def touch(self):
        self.save(update_fields=[])

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.updated_at = timezone.now()
        if update_fields is not None:
            update_fields.append('updated_at')

        super(TimestampMixin, self).save(force_insert, force_update,
                                         using, update_fields)

# Abstract
# ========


class Model(BaseMixin, models.Model):
    class Meta:
        abstract = True


class TimestampedModel(TimestampMixin, Model):
    class Meta(TimestampMixin.Meta, Model.Meta):
        abstract = True
