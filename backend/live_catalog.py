"""The five existing token identities explicitly moved into Live World by its owner.

This is a fixed allowlist, not discovery and not proof of a NEXUS launch.
Guest identities, permissions and social content are intentionally not migrated.
"""
from database import db, now

TOKENS = [
    {'id':'fartcoin','name':'Fartcoin','symbol':'FARTCOIN','mint':'9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump','district':'meme','color':'#b6f36e','x':-23,'z':-17},
    {'id':'arc','name':'AI Rig Complex','symbol':'ARC','mint':'61V8vBaqAGMpgDQi4JcAwo1dmBGHsyhzodcPqnEVpump','district':'ai','color':'#bca4f7','x':33,'z':27},
    {'id':'ban','name':'Comedian','symbol':'BAN','mint':'9PR7nCP9DpcUotnDPVLUBUZKu5WAYkwrCUx9wDnSpump','district':'defi','color':'#f1bd6c','x':34,'z':-23},
    {'id':'jellyjelly','name':'Jelly-My-Jelly','symbol':'JELLYJELLY','mint':'FeR8VBqNRSUD5NtXAj2n3j1dAHkZHfyDktKuLXD4pump','district':'culture','color':'#68d5df','x':-29,'z':35},
    {'id':'ansem','name':'The Black Bull','symbol':'ANSEM','mint':'9cRCn9rGT8V2imeM2BaKs13yhMEais3ruM3rPvTGpump','district':'meme','color':'#fb8194','x':-51,'z':-38},
]

def curated_query():
    return {'curated_live':True, '$or':[{'id':t['id'],'mint':t['mint']} for t in TOKENS]}

async def migrate_live_tokens():
    for item in TOKENS:
        existing = await db.tokens.find_one({'mint':item['mint']}, {'_id':0})
        if existing and existing.get('nexus_launched'):
            continue  # Never overwrite a real confirmed launch or its creator.
        legacy = await db.database['showcase_tokens'].find_one({'mint':item['mint']}, {'_id':0})
        market_fields = ('price','market_cap','image','volume_24h','change_24h','liquidity',
                         'pair','market_source','market_updated_at','pump_verified','pump_complete')
        seed = {k:legacy[k] for k in market_fields if legacy and k in legacy}
        defaults = {'price':None,'market_cap':None,'image':None,'holders':None,
                    'listed_at':now().isoformat(), **seed}
        updates = {**item,'curated_live':True,'nexus_launched':False,
                   'registry_status':'curated','community_enabled':True,'creator':None,
                   'description':f'{item["name"]} is an independently launched token, now part of the NEXUS world.'}
        await db.tokens.update_one({'mint':item['mint']},
            {'$set':updates,'$setOnInsert':defaults,'$unset':{'showcase':''}},upsert=True)
        await db.communities.update_one({'token_id':item['id']},{'$setOnInsert':{
            'token_id':item['id'],'scope':'live','created_at':now().isoformat()}},upsert=True)