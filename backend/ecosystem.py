"""Confirmed NEXUS launches plus the owner's explicit five-token Live World migration."""
from fastapi import HTTPException
from database import db
from live_catalog import curated_query

async def confirmed_ids():
    rows = await db.nexus_registry.find({'status':'confirmed'}, {'_id':0,'token_id':1}).to_list(10000)
    return [r['token_id'] for r in rows]

async def registry_ids():
    rows = await db.tokens.find(curated_query(), {'_id':0,'id':1}).to_list(5)
    return list(dict.fromkeys(await confirmed_ids() + [r['id'] for r in rows]))

async def visible_query():
    return {'$or':[
        {'id':{'$in':await confirmed_ids()},'nexus_launched':True,'registry_status':'nexus'},
        curated_query(),
    ]}

async def require_nexus_token(token_id):
    token = await db.tokens.find_one({'$and':[{'id':token_id}, await visible_query()]}, {'_id':0})
    if not token:
        raise HTTPException(403,'This token is not part of the NEXUS world')
    if token.get('nexus_launched'):
        entry = await db.nexus_registry.find_one({'token_id':token_id,'mint':token['mint'],'status':'confirmed'}, {'_id':0})
        if not entry:
            raise HTTPException(403,'Token launch registry does not match')
    return token

async def classify_existing_tokens():
    ids = await registry_ids()
    await db.tokens.update_many({'id':{'$nin':ids}}, {'$set':{
        'nexus_launched':False,'community_enabled':False,'registry_status':'external'}})