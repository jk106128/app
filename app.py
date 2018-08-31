 # -*- coding:utf-8 -*- 
import logging; logging.basicConfig(level=logging.INFO)
import time, uuid
from orm import Model, StringField, IntegerField

def next_id():
	return'%015d%s000'
class User(Model):
	__table__ = 'users'
	
	id = IntegerField(primary_key=True)
	name = StringField()

user = User(id=123, name='Colin')
user.insert()
user = User.findAll()

class Model(dict, metaclass=ModelMetaclass):
	@asyncio.coroutine
	@classmethod
	def save(self):
		args = list(map(self.getValueOrDefault, self.__fields__))
		args.append(self.getValueOrDefault(self.__primary_key__))
		rows = yield from execute(self.__insert__, args)
		if rows != 1:
			loggins.warn('failed to insert record: affected rows: %s' % rows)
	def find(cls, pk):
		'find object by primary key.'
		rs = yield from select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
		if len(rs) ==0:
			return None
		return cls(**rs[0])
	
	def __init__(self, **kw):
		super(Model, self).__init__(**kw)
		
	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Model' object has no attribute '&s'" % key)
		
	def __setattr__(self, key, value):
		self[key] = value
		
	def getValue(self, key):
		return getattr(self, key, None)
	
	def getValueOrDefault(self, key):
		value = getattr(self, key, None)
		if value is None:
			field = self.__mappings__[key]
			if field.default is not None:
				value = field.default() if callable(field.default) else field.default
				logging.debug('using default value for %s: %s' %(key, str(value)))
				setattr(self, key, value)
		return value
class Field(object):
	def __init__(self, name, column_type, primary_key, default):
		self.name = name
		self.column_type = column_type
		self.primary_key = primary_key
		self.default = default
	
	def __str__(self):
		return'<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):
	def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
		super().__init__(name, ddl, primary_key, default)
		
class ModelMetaclss(type):
	
	def __new__(cls, name, bases, attrs):
		#排除Model类本身
		if name=='Model':
			return type.__new__(cls, name, bases, attrs)
		#获取table名称：
		tablename = attrs.get('__table__', None) or name
		logging.info('found model: %s (table: %s)' % (name, tableName))
		#获取所有的Field和主键名：
		mappings = dict()
		fields = []
		primaryKey = None
		for k,v in attrs.iterms():
			if isinstance(v, Field):
				logging.info('	found mapping: %s ==> %s' %(k, v))
				mappings[k] = v
				if v.primary_key:
					#找到主键：
					if  primaryKey:
						raise RuntimeError('Duplicate primary key for field: %s' % k)
					primaryKey = k
				else:
					fields.append(k)
		if not primaryKey:
			raise RuntimeError('Primary key not found.')
		for k in mappings.keys():
			attrs.pop(k)
		escape_fields = list(map(lambda f: '`%s`' % f, fields))
		attrs['__mappings__'] = mappings #保存属性和列的映射关系
		attrs['__table__'] = tableName
		attrs['__primary_key__'] = primaryKey #主键属性名
		attrs['__field__'] =fields #除主键外的属性名	
		# 构造默认的Select, Insert , Update和Delete语句：
		attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ','.join(escaped_fields), tableName)
		attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ','.join(escaped_fields),
			primaryKey, create_args_string(len(escaped_fields) + 1))
		attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ','.join(map(lambda f: '`%s`=?'
			% (mappings.get(f).name or f), fields)), primaryKey)
		attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
		return type.__new__(cls, name, bases, attrs)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

def index(request):
	return web.Response(body=b'<h1>Awesome</h1>', content_type='text/html')



def execute(sql, args):
	log(sql)
	with (yield from __pool) as conn:
		try:
			cur = yield from conn.cursor()
			yield from cur.execute(sql.replace('?', '%s'), args)
			affected = cur.rowcount
			yield from cur.close()
		except BaseException as e:
			raise
		return affected
		
def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows returned: %s' % len(rs))
        return rs

def init(loop):
	app = web.Application(loop=loop)
	app.router.add_route('GET', '/', index)
	srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
	logging.info('server started at http://127.0.0.1:9000...')
	return srv

def create_pool(loop, **kw):
	logging.info('create database connection pool...')
	global __pool
	__pool = yield from aiomysql.create_pool(
			host=kw.get('host', 'localhost'),
			port=kw.get('port', 3306),
			user=kw['user'],
			password=kw['password'],
			db=kw['db'],
			charset=kw.get('charset', 'utf8'),
			autocommit=kw.get('autocommit', True),
			maxsize=kw.get('maxsize', 10),
			minsize=kw.get('minsize', 1),
			loop=loop
		)

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
	
