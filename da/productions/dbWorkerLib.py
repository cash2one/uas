#!/usr/bin/env python
# encoding: utf-8
"""
dbworkerlib.py
"""

import sys
import os
import copy

from sqlalchemy import *
from datetime import *
from types import *





def fieldEncode(field):
	tp = type(field)
	if tp is NoneType :
		return ''
	elif (tp is str) or (tp is unicode) :
		return field.encode('utf8')
	elif (tp is date) or (tp is datetime) :
		return str(field)
	else :
		return field

#### consts

userFieldDefine = { 
'_sys':{
'fields':['basic','nick'],
'class-mutiline':['telephones','emails','addresses','organizations','photos','sounds','educations','geoes'],
'class-oneline':['name','ident'],
'class-list':['im','url'],
'mutiline-key':{
	'telephones':'tel_number',
	'emails':'email',
	'photos':'photo_url',
	'sounds':'sound_url',
	'educations':'education',
	'im':'im_name',
	'url':'url_name',
	'addresses':'',
	'organizations':'',
	'geoes':''
	},
'userinfo':['versign','last_update','source_name','source_id','row_ord','data_class'],
'readonly':['versign_phone','uid','versign_email','user_id','source_ident'],
'realname':{
	'source_name':'origin',
	'source_id':'origin_id'
	}
},

'basic':['birthday','gender','blood','marry'],
'nick':['nick','avatar','sign'],

'name':['FN','family_name','given_name','additional_names','name_prefix','name_suffix'],
'ident':['idcard','key'],

'telephones':['tel_type','tel_number'],
'emails':['email_type','email'],
'addresses':['adr_type','post_office_address','extended_address','street','locality','region','postal_code','country'],
'geoes':['geo_type','record_date','tz','geo_lat','geo_lng'],
'organizations':['org_name','org_unit','org_subunit','title','role','work_field','org_logo','org_into_date','org_leave_date'],
'photos':['photo_class','photo_caption','photo_url'],
'educations':['school_name','school_city','education','school_into_date','school_leave_date'],
'sounds':['sound_class','sound_caption','sound_url'],

'im':['im_name','im'],
'url':['url_name','url']
}


def userDataToSql(userData, user_id, app_id):
	d = extractUserData(userData, userDataFields['basic'])
	sql = userFieldDataToSql(d, 'basic', appid)

def extractUserDataFields(userData):
	ud = userData
	if ud==None:
		return None

	r  = []
	ufs = userFieldDefine['_sys']
	sourceIdent = {}
	if 'source_ident' in userData:
		if (type(userData['source_ident']) is dict) and ('source_id' in userData['source_ident']):
			sourceIdent = userData['source_ident']
		
	udfs = {}
	udls = {}
	for k,v in ud.iteritems():
		if type(v) in (str,unicode,int,long,float):
			udfs[k]=v
		else:
			udls[k]=v
	for f in ufs['fields']:
		rd = extractUserFieldData(dict(udfs.items()+sourceIdent.items()),userFieldDefine[f],f)
		if len(rd['data'])>0: 
			r.append(rd)
	for f,uf in udls.iteritems():
		if f in ufs['class-mutiline']:
			if type(uf) is list: # ������������
				i=0
				for uitem in uf:
					i = i + 1
					uitem['row_ord']=i
					r.append(extractUserFieldData(uitem,userFieldDefine[f],f))
			if type(uf) is dict: # ������Ӧ�ô�����ֻ��һ��
				r.append(extractUserFieldData(dict(uf.items()+sourceIdent.items()),userFieldDefine[f],f))
		elif f in ufs['class-oneline']: # �϶�ֻ��һ��
			r.append(extractUserFieldData(dict(uf.items()+sourceIdent.items()),userFieldDefine[f],f))
		elif f in ufs['class-list']:
			kn = ufs['mutiline-key'][f]
			kf = userFieldDefine[f][1]
			for k,v in uf.iteritems():
				ul={kn:k,kf:v}
				r.append(extractUserFieldData(dict(ul.items()+sourceIdent.items()),[kn,kf],f))
		else:
			if f in ufs['readonly']:
				pass
			elif type(uf) is dict:
				r.append(extractUserFieldData(dict(uf.items()+sourceIdent.items()),['*'],f))
			elif type(uf) is list:
				for uitem in uf:
					r.append(extractUserFieldData(uitem,['*'],f))
			elif type(uf) in (str,unicode,int,long):
				r.append(extractUserFieldData(dict({f:uf}.items()+sourceIdent.items()),['*'],''))
	return r



def extractUserFieldData(userDataField, fieldList, fieldClass):
	d = {'data':{},'info':{},'class':''}
	u = userDataField;
	if u==None:
		return d

	realname = userFieldDefine['_sys']['realname']
	if 'data_id' in u:
		d['data_id'] = u['data_id']

	for k in u:
		if k in userFieldDefine['_sys']['userinfo']:
			d['info'][realname.get(k,k)] = u[k]
		if '*' in fieldList:
			d['data'][k] = u[k]
		elif k in fieldList:
			d['data'][realname.get(k,k)] = u[k]
	d['class']=fieldClass
	return d
	

def userFieldDataToExistsSql(user_id, app_id, userFieldData):
	sql = ''
	param = []
	if userFieldData==None:
		return ('',[])

	ufs = userFieldDefine['_sys']
	ud  = userFieldData['data']
	ui  = userFieldData['info']
	fieldClass = userFieldData['class']
	if 'data_id' in userFieldData: # �Ѿ�ָ���ض����ݼ�¼ /ͬʱУ���û���Ӧ�õĹ����ĺϷ���
		sql = "select info_id from userinfo where user_id=%s  and app_id=%s and info_id=%s ;"
		param = [user_id, app_id, userFieldData['data_id']]
		return (sql,param)
	if fieldClass in userFieldDefine:
		sqlpf = "select u.info_id from userinfo u inner join userinfo_"+fieldClass+" d on u.info_id=d.info_id where user_id=%s and app_id=%s "
		if 'source_id' in ui: # ָ�����ⲿ������ƥ��ļ�¼/ͬʱУ���û���Ӧ�ã����ݹ��࣬
			sql = sqlpf + " and origin=%s and origin_id=%s ;"
			param = [user_id, app_id, ui['origin'],ui['origin_id']]
			return (sql,param)
		else: # ���չ������ֶ��߼���Ψһ��Ҫ����ƥ��
			if (fieldClass in (ufs['fields']+ufs['class-oneline'])) or (
				fieldClass in ufs['class-mutiline'] and 'row_ord' not in ui ): ## ��һ��¼�ģ���ѯ֮ userid/appid/class/one
				sql = sqlpf + " ;"
				param = [user_id, app_id]
				return (sql,param)
				print '****', sql
			elif fieldClass in (ufs['class-mutiline']+ufs['class-list']): #����������ٸ��Ӽ��ؼ��ֶΣ�
				k = ufs['mutiline-key'][fieldClass]
				if (k!='') and (k in ud):
					sql =sqlpf + " and "+k+"=%s ;"
					param = [user_id, app_id, ud[k]]
					return (sql,param)
				else:
					sql = " and ".join(str(f)+"=%s" for f in userFieldDefine[fieldClass])
					sql = sqlpf + " and " + sql +';'
					param = [user_id, app_id] + [ud.get(f,'') for f in userFieldDefine[fieldClass]] 
					return (sql,param)
	else:  # userinfo_data data
		sqlpf = "select u.info_id from userinfo u inner join userinfo_data d on u.info_id=d.info_id where user_id=%s and app_id=%s and data_class=%s "
		param = [user_id, app_id, fieldClass]
		if 'source_id' in ui: # ָ�����ⲿ������ƥ��ļ�¼/ͬʱУ���û���Ӧ�ã����ݹ��࣬
			sql =  sqlpf + " and origin=%s and origin_id=%s ;"
			param = param + [ui['source_name'],ui['source_id']]
			return (sql,param)
		else: 
			if (fieldClass!=''):
				return (sqlpf+" limit 1 ;", param)
			else:
				if len(ud)==1: 
					sql   = sqlpf + " and "+ud.keys()[0]+"=%s ;"
					param = param + [ud.values()[0]]
					return (sql, param)


	return (sql,param)


# ���±����ҵ� info_id, 
def userFieldDataToUpdateSql(user_id, app_id, data_id, userFieldData):
	sqld = ''
	sqli = ''
	parami = []
	paramd = []
	if userFieldData==None:
		return ('',[])
	ufs = userFieldDefine['_sys']
	ud  = userFieldData['data']
	ui  = userFieldData['info']
	fieldClass = userFieldData['class']
	# ���ֶζ����
	sqli = "update userinfo set last_update=now() "
	if len(ui) >0:
		sqli = sqli +', '+ ', '.join(f+"=%s" for f in ui.keys())
		parami = ui.values()
	sqli = sqli + " where info_id=%s and user_id=%s and app_id=%s ; set @cnt=row_count();"
	parami = parami + [data_id, user_id, app_id]
	if fieldClass in (ufs['fields']+ufs['class-oneline']+ufs['class-mutiline']+ufs['class-list']):
		if len(ud) >0:
			sqld = "update userinfo_"+fieldClass+" set "
			sqld = sqld + ','.join(f+"=%s" for f in ud.keys())
			paramd = ud.values() 
			sqld = sqld + " where info_id=%s and @cnt=1;"  # �ٴα�֤��¼����Ч��
			paramd = paramd + [data_id]
	# ���ֶζ����
	else :
		for f in ud:
			sqld=sqld+ "replace userinfo_data values (%s,%s,%s) where @cnt=1;"
			paramd = paramd + [data_id, f, ud[f]]
	return (sqli+sqld, parami+paramd)
	

def userFieldDataToInsertSql(user_id, app_id, userFieldData):
	sqld = ''
	sqli = ''
	parami = []
	paramd = []
	if userFieldData==None:
		return ('',[])
	ufs = userFieldDefine['_sys']
	ud  = userFieldData['data']
	ui  = userFieldData['info']
	fieldClass = userFieldData['class']

	#if len(ui)>0:
	sqli = "insert into userinfo (" +", ".join(f for f in ['user_id', 'app_id']+ ui.keys()) +") values (" \
		+ ", ".join('%s' for f in ['','']+ui.keys())+"); set @cnt=row_count();  set @dataid = LAST_INSERT_ID(); "
	parami = [user_id, app_id]+ui.values()
	if fieldClass in (ufs['fields']+ufs['class-oneline']+ufs['class-mutiline']+ufs['class-list']):
		if len(ud) >0:
			sqld = "insert userinfo_"+fieldClass+" (info_id, "+', '.join(f for f in ud.keys()) \
				+") select * from (select @dataid, "+', '.join('%s as '+f for f in ud)+") d where @cnt=1;"
			paramd = ud.values()
	else:
		for f in ud:
			sqld=sqld+ "replace userinfo_data select * from (select @dataid,%s,%s) d where @cnt=1;"
			paramd = paramd + [f, ud[f]]
	return (sqli+sqld, parami+paramd)
