import uuid
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,Field,ConfigDict,model_validator
from pymongo.errors import DuplicateKeyError
from database import db,now
from auth import current_wallet,valid_wallet
from ecosystem import require_nexus_token,registry_ids,visible_query
from media_store import owned_image
from social_profiles import public_profile,viewer_wallet,Active
from social_models import PostView,FeedView,CommunityView,CommunityDirectoryItem
router=APIRouter()

class PostCreate(BaseModel):
    model_config=ConfigDict(extra='forbid')
    text:str=Field(default='',max_length=1000)
    media_ids:list[str]=Field(default_factory=list,max_length=4)
    parent_id:str|None=Field(default=None,max_length=64)
    kind:Literal['post','announcement']='post'
    @model_validator(mode='after')
    def nonempty(self):
        self.text=self.text.strip()
        if not self.text and not self.media_ids:raise ValueError('Write a post or add an image')
        if len(set(self.media_ids))!=len(self.media_ids):raise ValueError('Duplicate images are not allowed')
        return self

async def existing_post(id,include_deleted=False):
    query={'id':id}
    if not include_deleted:query['deleted']=False
    post=await db.social_posts.find_one(query,{'_id':0})
    if not post:raise HTTPException(404,'Post not found')
    token=await require_nexus_token(post['token_id'])
    return post,token

async def present(post,token,viewer=None):
    return {**post,'author':await public_profile(post['wallet'],viewer),
            'is_creator':post['wallet']==token['creator'],
            'token':{'id':token['id'],'name':token['name'],'symbol':token['symbol'],'image':token.get('image')},
            'likes':await db.social_likes.count_documents({'post_id':post['id']}),
            'reposts':await db.social_reposts.count_documents({'post_id':post['id']}),
            'replies':await db.social_posts.count_documents({'parent_id':post['id'],'deleted':False}),
            'viewer_liked':bool(viewer and await db.social_likes.find_one({'post_id':post['id'],'wallet':viewer})),
            'viewer_reposted':bool(viewer and await db.social_reposts.find_one({'post_id':post['id'],'wallet':viewer}))}

@router.post('/communities/{token_id}/posts',response_model=PostView)
async def create_post(token_id:str,body:PostCreate,wallet:str=Depends(current_wallet)):
    token=await require_nexus_token(token_id)
    if body.kind=='announcement' and (wallet!=token['creator'] or body.parent_id):raise HTTPException(403,'Only the token creator can publish announcements')
    if body.parent_id:
        parent,_=await existing_post(body.parent_id)
        if parent['token_id']!=token_id:raise HTTPException(400,'Replies must stay in the original token community')
    if await db.social_posts.count_documents({'wallet':wallet,'created_at':{'$gt':now().replace(second=0,microsecond=0).isoformat()}})>=12:raise HTTPException(429,'Please wait before posting again')
    media=[{'id':id,'url':await owned_image(id,wallet,['community'],token_id)} for id in body.media_ids]
    row={'id':uuid.uuid4().hex,'token_id':token_id,'wallet':wallet,'text':body.text,'media':media,
         'parent_id':body.parent_id,'kind':body.kind,'created_at':now().isoformat(),'deleted':False}
    await db.social_posts.insert_one(dict(row))
    if not body.parent_id:
        await db.social_feed.insert_one({'id':f'post:{row["id"]}','token_id':token_id,'post_id':row['id'],'actor':wallet,'kind':'post','created_at':row['created_at']})
    await db.activity.insert_one({'id':f'social:{row["id"]}','token_id':token_id,'wallet':wallet,'kind':'community',
        'text':'Published a creator announcement' if body.kind=='announcement' else 'Replied in the community' if body.parent_id else 'Posted in the community',
        'post_id':row['id'],'created_at':row['created_at']})
    return await present(row,token,wallet)

async def feed_rows(query,viewer,cursor=None,limit=20):
    if cursor:
        last=await db.social_feed.find_one({'id':cursor,**query},{'_id':0})
        if not last:raise HTTPException(400,'Invalid feed cursor')
        query={'$and':[query,{'$or':[{'created_at':{'$lt':last['created_at']}},{'created_at':last['created_at'],'id':{'$lt':last['id']}}]}]}
    events=await db.social_feed.find(query,{'_id':0}).sort([('created_at',-1),('id',-1)]).limit(limit+1).to_list(limit+1)
    items=[]
    for event in events[:limit]:
        post=await db.social_posts.find_one({'id':event['post_id'],'deleted':False},{'_id':0})
        if not post:continue
        token=await require_nexus_token(post['token_id'])
        items.append({**await present(post,token,viewer),'event_id':event['id'],
                      'reposted_by':await public_profile(event['actor'],viewer) if event['kind']=='repost' else None})
    return {'items':items,'next_cursor':events[limit-1]['id'] if len(events)>limit else None}

@router.get('/communities',response_model=list[CommunityDirectoryItem])
async def community_directory():
    tokens=await db.tokens.find({'$and':[await visible_query(),{'community_enabled':True}]},{'_id':0}).sort('name',1).to_list(1000)
    ids=[token['id'] for token in tokens]
    groups=await db.social_posts.aggregate([
        {'$match':{'token_id':{'$in':ids},'deleted':False}},
        {'$group':{'_id':'$token_id','posts':{'$sum':1},'wallets':{'$addToSet':'$wallet'}}},
        {'$project':{'_id':0,'token_id':'$_id','posts':1,'members':{'$size':'$wallets'}}},
    ]).to_list(1000)
    stats={group['token_id']:group for group in groups}
    return [CommunityDirectoryItem(**{**token,'posts':stats.get(token['id'],{}).get('posts',0),
        'members':stats.get(token['id'],{}).get('members',0)}) for token in tokens]

@router.get('/social/feed',response_model=FeedView)
async def world_feed(cursor:str|None=Query(None,max_length=160),viewer=Depends(viewer_wallet)):
    return await feed_rows({'token_id':{'$in':await registry_ids()}},viewer,cursor)

@router.get('/communities/{token_id}/feed',response_model=FeedView)
async def feed(token_id:str,tab:str=Query('all',pattern='^(all|following|announcements)$'),cursor:str|None=Query(None,max_length=160),viewer=Depends(viewer_wallet)):
    token=await require_nexus_token(token_id)
    query={'token_id':token_id}
    if tab=='following':
        if not viewer:return {'items':[],'next_cursor':None}
        following=await db.follows.find({'wallet':viewer},{'_id':0,'target':1}).to_list(5000)
        query['actor']={'$in':[viewer]+[r['target'] for r in following]}
    if tab=='announcements':
        ids=await db.social_posts.find({'token_id':token_id,'kind':'announcement','deleted':False},{'_id':0,'id':1}).to_list(1000)
        query.update({'kind':'post','post_id':{'$in':[r['id'] for r in ids]}})
    return await feed_rows(query,viewer,cursor)

@router.get('/communities/{token_id}',response_model=CommunityView)
async def community_info(token_id:str):
    token=await require_nexus_token(token_id)
    return {'token_id':token_id,'creator':token['creator'],
            'posts':await db.social_posts.count_documents({'token_id':token_id,'deleted':False}),
            'members':len(await db.social_posts.distinct('wallet',{'token_id':token_id,'deleted':False})),
            'announcements':await db.social_posts.count_documents({'token_id':token_id,'kind':'announcement','deleted':False})}

@router.get('/social/posts/{id}',response_model=PostView)
async def post_detail(id:str,viewer=Depends(viewer_wallet)):
    row,token=await existing_post(id,include_deleted=True)
    return await present(row,token,viewer)

@router.get('/social/posts/{id}/replies',response_model=list[PostView])
async def replies(id:str,viewer=Depends(viewer_wallet)):
    parent,token=await existing_post(id,include_deleted=True)
    rows=await db.social_posts.find({'parent_id':id,'deleted':False},{'_id':0}).sort('created_at',1).to_list(100)
    return [await present(r,token,viewer) for r in rows]

@router.post('/social/posts/{id}/like',response_model=PostView)
async def like(id:str,body:Active,wallet:str=Depends(current_wallet)):
    row,token=await existing_post(id)
    if body.active:
        try:await db.social_likes.update_one({'post_id':id,'wallet':wallet},{'$setOnInsert':{'post_id':id,'wallet':wallet,'created_at':now().isoformat()}},upsert=True)
        except DuplicateKeyError:pass
    else:await db.social_likes.delete_one({'post_id':id,'wallet':wallet})
    return await present(row,token,wallet)

@router.post('/social/posts/{id}/repost',response_model=PostView)
async def repost(id:str,body:Active,wallet:str=Depends(current_wallet)):
    row,token=await existing_post(id)
    key={'post_id':id,'wallet':wallet};event_id=f'repost:{id}:{wallet}'
    if body.active:
        stamp=now().isoformat()
        try:await db.social_reposts.update_one(key,{'$setOnInsert':{**key,'created_at':stamp}},upsert=True)
        except DuplicateKeyError:pass
        await db.social_feed.update_one({'id':event_id},{'$setOnInsert':{'id':event_id,'post_id':id,'token_id':row['token_id'],'actor':wallet,'kind':'repost','created_at':stamp}},upsert=True)
    else:
        await db.social_reposts.delete_one(key);await db.social_feed.delete_one({'id':event_id})
    return await present(row,token,wallet)

@router.post('/social/posts/{id}/delete')
async def delete_post(id:str,wallet:str=Depends(current_wallet)):
    row,token=await existing_post(id)
    if row['wallet']!=wallet:raise HTTPException(403,'Only the author can delete this post')
    await db.social_posts.update_one({'id':id,'wallet':wallet},{'$set':{'deleted':True,'text':'','media':[]}})
    await db.social_feed.delete_many({'post_id':id})
    await db.activity.delete_many({'post_id':id})
    return {'deleted':True}

@router.get('/profiles/{wallet}/posts',response_model=FeedView)
async def profile_posts(wallet:str,tab:str=Query('posts',pattern='^(posts|reposts)$'),cursor:str|None=None,viewer=Depends(viewer_wallet)):
    valid_wallet(wallet)
    return await feed_rows({'actor':wallet,'kind':'repost' if tab=='reposts' else 'post','token_id':{'$in':await registry_ids()}},viewer,cursor)