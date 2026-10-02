# NEXUS — Living Solana World

## LATEST AUTHORITATIVE SCOPE — 2026-10-02, homepage and primary navigation

This section supersedes the prior root-to-world requirement and all conflicting historical sections below.

### Original latest problem statement

IMPORTANT — RESTRUCTURE THE NEXUS ENTRY EXPERIENCE

The current result is not correct.
The NEXUS World should NOT be the first page users see when opening the website.
The World is a core product section, but it is NOT the homepage.

1. CREATE A REAL NEXUS HOMEPAGE
When users open NEXUS, show a dedicated Homepage / Landing Page first.
The homepage should feel like the entrance to NEXUS, not the World itself.
It should introduce what NEXUS is and let users choose where they want to go.
Keep it visually minimal and premium.
Include: NEXUS branding; Short positioning statement; Enter World / Explore CTA; Launch Token CTA; About; Community / Social; Docs; Social links.
Use visual mockups / preview images of the NEXUS World and product features inside the homepage sections.
Do NOT immediately open the World when visiting the root homepage.
The homepage should explain and visually showcase NEXUS first, then users can enter the World.

2. ADD SIMPLE PRIMARY NAVIGATION
Create a simple persistent navigation bar inspired by the usability of modern crypto platforms such as Pump.fun, but do NOT copy its exact design.
The navigation should use simple icons + short labels and provide access to the main NEXUS sections.
Suggested structure: Home | World | Launch | Community | About
Keep the navigation extremely simple.
Do NOT use radial menus. Do NOT use weapon-wheel interfaces. Do NOT use game inventory menus. Do NOT create complicated HUD navigation.
The navigation should feel like a normal, easy-to-use product interface.
On mobile, use a fixed bottom navigation bar with clear icons and labels.
On desktop, adapt the same navigation into a clean persistent navigation system.

3. FIX THE WORLD PAGE
The current World page contains unnecessary interface text and controls.
Remove unnecessary elements such as: “LIVE WORLD 001”; Large unnecessary introductory text over the map; “A world of tokens”; “Find your people. Build your place.”; Any decorative copy that does not provide actual functionality; Unnecessary neighborhood/category selectors.
The World should primarily be the interactive map and token buildings.
Keep the existing buildings and world visual.
Users should be able to: Explore → Find Building → Click Building → Open Token.
That is the core interaction. Do not overload the World with website-style content.

4. KEEP THE PRODUCT SIMPLE
NEXUS has a small number of core concepts:
Home: Introduction and product overview.
World: Explore token buildings.
Launch: Launch a token through NEXUS.
Community: Discover and interact with token communities.
About: Understand the NEXUS concept.
Do not invent additional navigation categories just to make the interface feel more complex.
NEXUS should feel like a simple crypto product with an immersive world, NOT like a complicated video game UI.
The World is the experience. The navigation should stay simple.

### Latest explicit choices
- Built-in Docs and verified repo links; “Buat aja dulu untuk linknya nanti menyusul”. Official social URLs are to follow, not invented.
- Both a live token community directory AND a combined feed of posts from all live token communities.
- “Tolong buatnya jangan terlalu simple dan jangan terlalu rumit, buat kenyamanan user agar tidak bingung dan mudab di gunakan”.

### Architecture / personas / static requirements
- Same explorer, creator and community personas. Preserve original geometry, token identities, real data, wallet auth, official launch integration and social mutations.
- `/` renders Home, not a redirect and not an interactive canvas. `/world` renders original Three.js scene. `/launch`, `/community`, `/about` are the only other primary destinations. `/docs` is supporting content, accessible through header/footer, not a sixth primary navigation item.
- Sticky icon+label desktop navigation; fixed five-destination mobile bottom navigation with safe-area and page-content clearance.
- All old `/showcase/*` bookmarks only redirect to corresponding live pages; no showcase API/mode is reintroduced.
- Directory API `GET /api/communities` uses Pydantic contracts, real per-community post/member counts, Mongo aggregation with `_id` projected out. Combined `GET /api/social/feed` uses existing authenticated-viewer support and cursor-based feed rows, scoped only to live world tokens. Existing signed-wallet mutation rules unchanged.
- Actual product imagery generated from the app using `/app/scripts/capture_product_assets.py`, stored as static assets under `frontend/public/previews`. No external stock city or fabricated product screenshots. No uploaded user files stored locally.

### Implemented — 2026-10-02, latest revision
- Dedicated premium homepage: large NEXUS positioning, Enter World and Launch Token, real static world background, existing token links, three authentic product previews, About introduction, Community and Docs links, shared footer.
- Simple persistent Home/World/Launch/Community/About navigation. Active state, direct destinations, mobile bottom bar. Logo now returns Home; explicit Back to world links still open `/world`.
- Removed World intro block, LIVE WORLD001, marketing text, neighborhood selector and decorative network readout. Retained map, buildings, token search, small token count, zoom/reset/top-view controls.
- Added About with product concept, original world image, fee/wallet transparency and social area.
- Added built-in Docs with five chapters covering getting started, tokens/world, communities, launching, and wallet safety. Desktop chapter navigation and mobile select.
- Added searchable community directory with real contributor/post counts and combined All posts tab. Existing post/reply/like/repost/delete/profile flows reused. Empty feed is honest; no fake posts seeded.
- GitHub links use supplied repository URL. X/Telegram/Discord are explicitly disabled with Soon labels until official URLs arrive from user.
- Reduced static scenery draw calls via material batching, preserved original geometry, and replaced deprecated THREE.Clock with THREE.Timer. World remains animated and clickable.
- Desktop screenshot: Home remains `/`, image loaded at1920px, CTA enters `/world`, no World intro. Mobile iframe388px: Home and World `scrollWidth === innerWidth`, visible fixed bottom nav, all five buildings visible, direct Community directory navigation passes.
- Final testing iteration2:41/41 backend tests passed, including cross-community feed, actual signed-wallet posts, like/repost/delete, invalid cursor and pagination. No blocking or minor app defects reported.
- Browser regression passed desktop1920 and mobile390/375/320: homepage-only root, all real preview assets, five nav destinations and active state, map-only World, animated canvas pixel changes, map controls, building-to-token, directory search, feed tab/history, docs chapters, social pending states. Main self screenshots at1920x800 and mobile388 also passed.
- Test agent added only `/app/backend/tests/test_community_feed_regression.py` and test report; inspected by main agent. Test-authored posts/engagements cleaned. Final report: `/app/test_reports/iteration_2.json`.
- Wallet chooser confirmed. Full external-wallet extension connect/disconnect and paid transactions were not executed in-browser; API-level signed-message authentication and social mutations passed. Source-map/GPU-readback/preview-overlay warnings are tooling noise, not product failures.

### Current limitations and prioritized backlog
- P0: none outstanding in the tested latest scope.
- P1: user will supply official X/Telegram/Discord links. Paid mainnet launch/trade/payout verification still requires explicit user-controlled wallet execution and is not claimed complete.
- P2: bookmark favorite communities, shareable community invites, pinned creator announcements. Do not add extra primary navigation categories.

---

## Current authoritative scope — 2026-10-02, simple Live World redesign

This section supersedes ALL historical design, showcase and membership requirements below where they conflict.

### Original current request

Clone repo ini perbaiki bug kalau ada https://github.com/unclebiki7-bot/Teser lalu edit ui nya
The current redesign has gone too far into launchpad-style UI and has become unnecessarily complicated.
Do NOT use radial menus, weapon-wheel interfaces, circular navigation, game inventory wheels, or complex game HUD systems.
NEXUS is inspired by world and exploration, not through complicated game controls.
The product should remain extremely easy to understand.
NEXUS has only a few core actions:
1. Explore the World
2. Click a Token Building
3. View the Token
4. Join its Community
5. Launch a Token
The interface should make these actions obvious within seconds.
Do not create additional navigation systems just to make the product feel like a game.
Keep the world immersive, but keep the interface simple.
Avoid: Radial menus; Weapon wheels; Circular navigation systems; Complex HUDs; Multiple layers of navigation; Excessive icons; Game inventory-style menus; Complicated dashboard panels; Unnecessary interaction steps.
The goal is: Token world. Simple product.
NEXUS should feel like an open world that happens to be a launchpad, not a complicated game that happens to launch tokens.
Prioritize clarity over spectacle.
“Don't add UI complexity unless it represents a real NEXUS function.”

### Explicit user choices
- Preserve repo functionality, fix discovered bugs and simplify UI into the five core actions.
- Use existing wallet/launch integrations; report anything requiring configuration.
- “Hapus showcase jangan gunakan showcase, pindahkan token showcase ke live world aja”.
- Communicate in Indonesian, retain the repository's English product labels.

### Architecture, personas, static requirements
- Source cloned from `unclebiki7-bot/Teser`; pristine clone at `/root/nexus-source`. Source imported into `/app` without overwriting protected environment variables or workspace git metadata.
- React 19 / FastAPI / MongoDB retained; original `world/geometry.js` retained, Three.js full-bleed city, Shadcn dialogs/buttons and Sonner. No replacement game controls.
- Personas: explorers click buildings, community participants authenticate with their own wallet, creators launch via official Pump.fun SDK.
- Single Live World. Fixed five-token allowlist plus confirmed NEXUS registry entries. Migrated identities retain exact mint, coordinates, district, independent origin; no forged NEXUS registry or creator ownership.
- No guest API/app or guest WalletProvider override. Auth stays Ed25519 challenge + wallet session. Public browsing does not require a wallet; all mutations retain real wallet authentication.
- Community data is live. Do not migrate former guest credentials, unverified guest posts or guest ownership. Existing real wallet-authenticated live content is preserved.
- Existing official Pump SDK 2.0.0, creator fees, transactions, verification, image object storage, social functions and bounty functions retained.

### Implemented — 2026-10-02
- Removed radial SpatialMenu component, portal navigation, showcase backend app/config and guest frontend context. Old `/showcase/*` bookmarks redirect to corresponding live routes only; old API endpoints return 404.
- New simple header: NEXUS, Explore, token/address search, Launch token, Connect wallet. Full-bleed original 3D city, one neighborhood select, four direct map controls. No new dashboard, wheel or alternate navigation layer.
- Migrated FARTCOIN, ARC, BAN, JELLYJELLY, ANSEM into live Mongo records idempotently. Market caps/prices/images fetched from real DEX Screener; Pump provenance checked against on-chain accounts. Missing metrics remain unavailable.
- Clean token page with direct Back to world and Join community. Existing overview/chart/about/activity/trades and community preserved, with honest independent token origin.
- Fixed right-click triggering token selection while rotating; responsive orthographic camera framing and label collision against intro; map state resets consistently on returning from interior pages.
- Fixed former null-creator equality displaying owner actions to disconnected visitors; announcements now explicitly require an authenticated matching creator.
- Added missing runtime configuration without changing MONGO_URL, DB_NAME, REACT_APP_BACKEND_URL. Installed repository dependencies; object storage startup successful.
- Smoke checks: live world API contains five identities with real market values and Pump verification; real historical chart returned 24 candles; community API returns valid null creator; unauthenticated post rejected 401; retired guest endpoint 404. Desktop screenshot confirms WebGL and direct building-to-token routing.

### Validation and limitations
- Comprehensive testing pending; results to be appended after testing agent.
- No actual paid launch, swap or payout has been performed. Those require user wallet approval/funds. Do not claim otherwise.
- Real wallet testing instructions in `/app/memory/test_credentials.md`; no permanent test account.

### Prioritized remaining work / next tasks
- P0: finish desktop/mobile and API regression tests and resolve their defects.
- P1: user-controlled funded launch verification; enhanced community moderation/reporting when requested.
- P2: shareable neighborhood invitations, saved favorite token locations, pinned creator announcements.

---
## Historical record (superseded by the section above)

## Current authoritative scope — 2026-10-02, repository continuation

**This section supersedes the historical catalog/import/redirect requirements below.**

### Original current user request (verbatim)

Clone repo ini full jangan ada yg ketinggalan https://github.com/lasvegasworld20-max/Nexs, lalu fixin lanjutkan

Do NOT rebuild, redesign, or modify the existing World, Map, Token Buildings, Territories, Token Hub, or current visual design. Those parts are already built and working correctly.

1. PUMP.FUN INTEGRATION — CRITICAL

NEXUS is a launchpad integrated with Pump.fun.

Only tokens launched through the NEXUS launchpad should become NEXUS tokens and appear inside the NEXUS ecosystem.

Correct flow:

User → NEXUS Launchpad → Launch Token → Pump.fun → Successful Launch → NEXUS registers the token → Token appears in NEXUS

Do NOT import, fetch, or automatically display all tokens from Pump.fun.

A token launched directly on Pump.fun without using the NEXUS launchpad must NOT appear on the NEXUS map, buildings, token list, or NEXUS ecosystem.

NEXUS must maintain its own registry/database of tokens launched through NEXUS.

Pump.fun is only the underlying launch/trading infrastructure. NEXUS controls which tokens belong to the NEXUS ecosystem.

Do not modify or recreate Pump.fun's existing creator fee mechanics.

2. TOKEN COMMUNITY — ONLY FOR NEXUS TOKENS

Add/finish the Community social feature for each token launched through NEXUS.

Every NEXUS-launched token should have its own token-specific social community.

The community should feel like a lightweight social network similar to X:

Text posts

Image uploads

Replies

Likes

Reposts

User profiles

Follow users

Token/community feed

Creator announcements

Community activity

The Community should be directly accessible from the existing Token Hub.

IMPORTANT: Community is only created for tokens launched through NEXUS. Do not create communities for random Pump.fun tokens that were not launched through NEXUS.

Keep the existing NEXUS World, buildings, Token Hub, layout, and visual identity exactly as they are. Only implement the Pump.fun launchpad integration correctly and add the token-specific Community social layer.

### Explicit continuation choices
- Follow existing repository wallet/network configuration (official Pump SDK 2.0.0, Solana mainnet, Phantom/Solflare). Actual transactions require user wallet approval.
- Focus on launchpad and Community; fix other discovered bugs without changing visual design.
- Communicate in Indonesian; preserve existing English UI.

### Architecture / personas / static requirements
- Existing creator, trader/explorer, and community-participant personas remain unchanged.
- Complete source cloned from commit `39aaa8ea5ab677522e3df6ddf1d949ad6224734d`; pristine source retained in `/root/nexs-source`. All source file paths exist in `/app` (verified). Keep workspace git and configured environment intact.
- Preserve React/FastAPI/Mongo architecture, original Three.js renderer/geometry, core CSS and existing Token Hub. Backend module boundaries extended, not rebuilt.
- Only confirmed `nexus_registry` membership plus NEXUS token status determines public visibility. No token discovery/import/listing endpoint grants membership. Legacy catalog source is preserved but is never seeded into the ecosystem or shown on world/token/chart/trade routes.
- Official SDK builder executes unsigned on server; mint keypair stays in browser memory. Session stores exact serialized message/hash, wallet, mint and metadata URI BEFORE signing. Both wallet and mint signatures, exact message and independently verified successful Pump chain creation are required before registration. Registration completes token/community/activity records before confirming registry visibility.
- Creator fees/fee recipients remain entirely Pump-controlled. NEXUS does not collect, replace, redirect or implement creator fee mechanics.
- Mongo collections include `launch_sessions`, `nexus_registry`, `communities`, `social_posts`, `social_feed`, `social_likes`, `social_reposts`, `profiles`, `follows`, `files`, plus preserved economy/auth collections. Public social responses use Pydantic contracts; Mongo `_id` is excluded.
- Real object storage serves normalized images and launch JSON metadata via backend public media routes. Validate size/type/pixel bounds, wallet ownership and token-specific media binding. No fake runtime APIs or success shortcuts.
- Community remains embedded in the existing Token Hub tab with a standalone `/community/:id` and `/community/:id/post/:postId`; `/profile/:wallet` supports identity and connections.

### Implemented in this continuation — 2026-10-02
- Restored full repository, installed dependencies and configured missing service URLs/storage access while preserving `MONGO_URL` and `REACT_APP_BACKEND_URL`.
- Removed incorrect visual-catalog exception from registry filtering and disabled catalog seeding. Arbitrary imports and independent mint route return 410 authenticated. All public token surfaces use registry visibility, including trading activity.
- Retained/finalized session-bound SDK launch; improved preparation expiry, processed-versus-expired checks, registration order and idempotent confirmed status reads. No RPC needed to read an already-confirmed session.
- Added per-wallet pending-session recovery, automatic status checks for authenticated pending launches, exact signed-transaction retry, failure/expiry clearing and wallet-change protection. Private mint keys are never persisted.
- Completed token-specific Community text/image posting, replies, like/unlike, repost/undo, profiles/avatars, follow/unfollow, following/community/announcement feeds, contributor/post counts and activity. Pagination and cross-token permissions validated.
- Preserved replies after root deletion using a deleted-post tombstone; removed author/like/repost actions from tombstones. Async stale data and duplicate-page loading protections added to community/thread/profile views.
- Fixed hidden file inputs overriding visually-hidden widths (390px mobile overflow), malformed PNG errors (400, not 500), and wallet disconnect/reconnect state/listener cleanup.
- Original `World.jsx`, `geometry.js`, `TokenDashboard.jsx`, `App.css`, `index.css`, and `catalog.py` remain byte-for-byte identical to cloned source. Only renderer change is removing the one-line `!tokens.length` early-return guard so the ORIGINAL city renders before the first legitimate NEXUS launch. No visual redesign.

### Validation and honest limitations
- `/app/test_reports/iteration_4.json`: 30/30 backend cases passed. Real RPC + object storage + official SDK transaction PREPARATION passed. Successful on-chain registration/failure/idempotency branches tested with isolated test-only RPC fixtures, not actual financial execution.
- `/app/test_reports/iteration_5.json`: authenticated creator browser flow passed real image upload/post, creator announcement and profile/avatar editing; subsequent participant reconnect failure identified and fixed.
- Main-agent browser follow-up: creator→participant→creator reconnect, like/unlike, repost/undo, reply, follow, following feed, activity tab, root deletion and retained replies all passed. Evidence console `/root/.emergent/automation_output/20261002_203040/console_20261002_203040.log` and browser screenshots `social-interactions-verified.jpg`, `social-tombstone-verified.jpg`.
- Mobile follow-up used a real 390px embedded browser viewport inside required 1920×800 screenshot viewport: header CTA→launch, profile editor and Community activity all had `innerWidth=scrollWidth=390`. Evidence console `/root/.emergent/automation_output/20261002_203144/console_20261002_203144.log`.
- Corrupt PNG upload independently checked via external API with an ephemeral real auth session: HTTP 400 with safe-image validation message.
- All temporary fixture tokens, registry/community/social/profile/session records cleaned; final world/registry contain zero tokens because no genuine NEXUS launch has occurred. Decorative city scenery remains intact. Do NOT reseed external tokens to make the city seem populated.
- **No funded mainnet launch, trade or payout has been executed.** Actual wallet approval/funding is required; never claim financial end-to-end execution is verified. No production database/content was present in the public Git repository.
- No application runtime APIs are mocked. Test-only ephemeral wallet providers and isolated RPC fixtures are documented, cleaned up, and not part of application code.

### Prioritized remaining work / next actions
- P0: user-controlled funded mainnet launch verification remains unexecuted; use official wallet confirmation and existing session recovery. No remaining known blocking app defect from the completed checks.
- P1: community reporting/moderation and stronger API abuse controls; reliable indexed holder counts/full trade-history coverage if needed. Existing unsupported market values remain explicitly unavailable rather than fabricated.
- P2: community notifications, pinned announcements, shareable community/territory invitation links.
- Suggested next product enhancement: pinned creator announcements plus community invite links for easier member onboarding.

---
## Historical project record (superseded where it conflicts with current scope)

## Original problem statement

Build a crypto launchpad that feels like a living open-world game, not a traditional token launchpad.

Use Ingress (https://ingress.com/) for its open-world map, locations, territories, exploration and map-based interaction. Use GitCity (https://gitcity.xyz/) for a world made from buildings, where entities are represented as buildings.

Every token launched through the platform becomes part of a persistent crypto world. The primary experience is an interactive open-world map containing token buildings, not token cards. The world should feel like a real place, continuously changing as the crypto market changes.

The homepage opens directly into a large, explorable map with different territories/locations, roads/areas, token buildings, different building sizes, points of interest, community activity, territory boundaries, zoom and movement. The world itself is the main interface.

Every token gets a building. Building height is determined by market cap: $500K is a small building, $5M medium, $50M a skyscraper. Heights grow/shrink with market cap. Buildings have visual token identity. Clicking a building navigates to its Token Dashboard, not a popup. Dashboard: token name/ticker/image, market cap, price, volume, holders, price chart, buy, sell, token information, community activity, active bounties and history.

Creators define custom bounties, not fixed quests: bounty name, reward, objective, rules/conditions, duration, eligibility, winner/reward distribution. Creator creates the game; community plays for the bounty. Bounties belong to token territories. Territories should read as actual locations, not rectangular UI cards.

Launch flow: a token receives a world location and building; building reflects market cap; creator customizes token presence and creates bounties; community interacts with territory; building always leads to dashboard.

Design: Crypto + Open World + City + Game, not crypto dashboard + map background. World is the hero, modern game-like interface, depth and scale, different building heights/silhouettes, clean functional overlays. Full-screen primary world map with top logo/search/connect wallet/explore and side/bottom map controls/world information/bounties/leaderboard/activity. No landing page. Core loop: Launch → World → Building → Territory → Bounty → Community → Token Dashboard → Trade. Intuitive without long explanations.

## Explicit user choices

- **Real wallet connection and on-chain trading; Solana chain.**
- **Top-down territory map featuring 3D token buildings; Stylized 3D crypto city with explorable districts and a dynamic skyline; Let me choose the best direction based on the concept.**
- **“Jangan ada tulisan demo atau simulate semacamnta buat sudah produk jadi walaupun masih belum public.”**
- Communicate with user in Indonesian. Interface is polished English, following original brief. No fabricated market data, holders, balances, rewards or successful transactions.

## Personas

1. Explorer/trader: discover tokens spatially, inspect live market data, swap non-custodially, return to the world.
2. Token creator: mint a token, establish a territory, customize its presence, publish custom bounties, approve and pay winners.
3. Community participant: sign in with wallet, post messages, discover bounties and submit work.

## Architecture decisions

- React 19 / CRA + CRACO, React Router; Shadcn primitives, Sonner, Lucide, Recharts. Route pages `/`, `/token/:id`, `/launch`, `/bounties`, `/leaderboard`.
- Imperative Three.js orthographic world with OrbitControls. Full-screen live canvas, deterministic city scenery via instancing, irregular district boundaries, roads/canal/bridges/Genesis Plaza, ambient traffic, token towers and collision-aware projected labels. Decorative low-rise scenery does not represent extra tokens.
- Market cap determines smoothly interpolated tower height using logarithmic visual scaling. Heights update with real market snapshots, not random movement.
- FastAPI modular routers, Motor/MongoDB. Models/data in `tokens`, `activity`, `bounties`, `submissions`, `challenges`, `sessions`. Queries exclude BSON `_id`; ISO UTC dates for world records, native UTC datetimes for TTL authentication.
- Real catalog: 16 Solana token identities cross-checked against CoinGecko platform registry, exact mint addresses. Do not discover identities by ticker alone because cloned tokens can appear in DEX search.
- DEX Screener token snapshots, request-driven 60-second cache; GeckoTerminal actual OHLCV candles with 120-second cache. Missing/stale data retained explicitly with timestamp; no invented values. No background job/scheduler was introduced.
- Four districts: Meme Quarter (green), DeFi Heights (amber), Neural District (lavender), The Waterfront (cyan). Dark neutral technical palette, Unbounded + Manrope + JetBrains Mono.
- Non-custodial Phantom/Solflare injected wallet integration. Ed25519, origin-bound, one-use, 5-minute challenges. Hashed random bearer sessions expire after 12 hours. No seed/private keys persisted.
- Solana mainnet RPC proxied through `/api/rpc` using a method allowlist. Protected `MONGO_URL` and `REACT_APP_BACKEND_URL` preserved. Service URLs stored in environment.
- Official keyless Jupiter Plugin integrated on token dashboard, actual SOL/token swap routing, explicit buy/sell defaults, official external Jupiter deep link fallback. Plugin handles its own wallet connection. POSIX locale normalization avoids Intl crash in embedded browsers.
- **Superseded by the Pump.fun integration below:** the initial independent SPL mint flow is removed. No client-side independent token creation remains; authenticated `/api/launches` now returns 410.
- Pump token name/symbol/metadata URI come from independently verified Pump creation instructions/events. Off-chain image/description are read from the referenced metadata, subject to safe URL and payload bounds. NEXUS only controls its world representation.
- Bounties: creator-only creation; custom text conditions/eligibility/distribution; SOL reward, deadline. Entries are wallet-authenticated, one per wallet; owner cannot self-enter. Winner payout requires a real wallet-signed SOL transfer and backend verifies source/destination/amount before award. Rewards creator-managed, not escrow; UI explicitly states this. Pending payout signature stored for safe retry.

## Implemented — 2026-10-02

- Full-screen navigable city, 16 real token buildings, market-cap heights, colored territories, minimap, camera coordinates, zoom/pan/rotate/recenter/top-down/fullscreen, map layers and district focus.
- Search by name/symbol/mint, Ctrl/Cmd+K, routed dashboard, global wallet connection and launch access (including mobile).
- World pulse, real market cap/volume, token ranking, honest empty activity/bounty states.
- Token dashboard: live metrics, real historical chart/periods, Jupiter buy/sell, mint address/copy/explorer, community posts, bounties/history, creator presence customization.
- Leaderboard with filters/search/sort and token navigation.
- Wallet-authenticated real token-creation flow and verified persistent world registration. Mainnet acknowledgement and cost/liquidity disclosures.
- Creator bounty publishing, participant submissions, public entries, verified single-winner SOL payout flow, creator-only ownership checks.
- Responsive layouts tested at desktop 1920px and mobile 390px, no body horizontal overflow.
- Chart sizing warning fixed after testing by measuring positive dimensions via ResizeObserver before rendering Recharts; sub-dollar price precision and intraday chart axes improved.
- Expired/invalid wallet sessions clear on HTTP 401 so the next authenticated attempt requests a fresh wallet signature.
- Initial screenshot showed labels overlapping; collision logic now uses measured DOM dimensions. Map control/bounty footer collision fixed; header launch remains available when sidebar launch is hidden on shorter screens.

## Validation

- `/app/test_reports/iteration_1.json`: 21/21 backend tests passed; frontend flows passed except chart sizing warning subsequently fixed.
- Automated coverage: real data APIs, token/404/chart, wallet malformed/invalid/replay rejection, session login with ephemeral signing keys, creator-only bounties/presence, entry validation/duplicates/closed states, community persistence, payout authorization rejection, launch rejection. Temporary world fixtures removed after tests.
- Browser: canvas rendered, controls/district/layers, search/Ctrl+K, token routing, real chart, wallet modal, launch validation, leaderboard, mobile overflow. Jupiter rendered after locale normalization.
- Final self-check showed explicit chart size 854×295 and real chart SVG, period switches, rendered Jupiter SOL→JUP form, launch form and return to world.
- **No real funds were spent and no funded wallet mint/swap/payout was executed by the agent.** Those branches require the user's own wallet approval. Never label their success as verified until confirmed on-chain.
- Test auth guidance: `/app/memory/test_credentials.md`, `/app/auth_testing.md`. No passwords or permanent funded test wallets.

## Known limitations and prioritized backlog

### P0 — Before accepting public real-money use
- User-authorized launch on official Pump.fun, then creator-authenticated verify/import in the browser. Read-only verification of a real successful Pump mainnet creation has passed; no launch/trade funds were spent. Non-Pump legacy catalog swaps and bounty payout remain wallet-approved external financial flows.
- Dedicated production-grade Solana RPC configuration. Current public mainnet RPC is functional but rate-limited and unsuitable for sustained heavy traffic.
- Transaction lifecycle hardening: recovery for rejected/dropped/expired transactions, deeper adversarial on-chain validation, concurrency control around payout finalization, API anti-abuse limits.
- Formal security audit before public financial usage (not performed; no audit was requested).

### P1 — Complete market/launch ecosystem
- Optional direct official Pump SDK launch only with a verified supported metadata-publication pipeline and current pinned instruction compatibility. Never reintroduce independent SPL minting or alter Pump fee fields.
- Liquidity, bonding curve, graduation and creator fees remain Pump infrastructure, not an independently implemented NEXUS subsystem.
- Holder analytics/indexer integration. Current upstream does not provide holder totals; UI says Not available.
- Confirmed on-chain trade history/indexer; existing history covers world launches, bounties, community milestones.
- Multi-winner reward distribution and/or audited escrow. Current supported payout is one winner receiving the stated SOL reward.
- Creator claim mechanism for curated external tokens; these correctly have no NEXUS creator and cannot have bounties issued by arbitrary wallets.
- Backend pagination / large-world chunks for thousands of actual tokens beyond initial catalog. Current API caps world token queries at 1000 and dynamic city plotting should gain occupancy management for scale.

### P2 — World/community depth
- Token-specific custom 3D silhouettes, more landmarks, expanded navigable territories and persistent camera position.
- Shareable territory deep links and community invite/referral links.
- Moderation/reporting, notifications, bounty search and more filters.
- Optional wallet-adapter passthrough to eliminate separate Jupiter wallet connect step.

## Next suggested product enhancement

Shareable territory URLs with token/camera focus and a community invite would make each token's location easy to circulate.

## Pump.fun integration layer — 2026-10-02

### User request and explicit choice

Preserve the existing website, concept, map, buildings, territory system and visual direction. Add only the real Pump.fun integration layer. Pump.fun owns token launches and underlying trading infrastructure; NEXUS owns the visual/game/community layer. Do not create independent tokens, fake launches/trades, or a separate creator-fee system. Do not replace, redirect, recreate or modify Pump.fun creator fees.

Creator loop: Launch Token → Pump.fun → Token Appears in World → Building Created → Height Follows MC → Create Bounty. User loop: Explore → Building → Dashboard → Buy/Sell → Bounty. Use real token address/name/symbol/image/cap/price/volume/holders/activity where available, plus Pump.fun link, chart and community.

Explicit choice: **“Utamakan SDK/API resmi; jika tidak tersedia, gunakan halaman resmi Pump.fun lalu verifikasi token untuk memasukkannya ke dunia.”** No third-party transaction provider authorized.

### Delivered architecture

- Official SDK/IDL researched. Current Pump creation supports evolving Token-2022/mayhem/cashback/holder-reward/fee options; direct hosted metadata publication was not established as a supported public end-to-end API. Implemented the authorized official-page handoff, not a private frontend endpoint or third-party transaction service. Direct SDK transaction launch is not enabled.
- `/launch` retains prior style and building preview, replacing standalone mint form with official `https://pump.fun/create` link, mint + original creation signature fields, creator wallet, verification, existing district/color picker, then registration. Draft persists across visiting Pump.fun. Opening Pump.fun is not counted as a successful launch; no automatic callback is claimed.
- Removed frontend `createToken`, Keypair mint generation, initializeMint/mintTo/revoke mint instruction assembly. Retained independent SOL transfer solely for community bounty rewards, unrelated to creator fees.
- New authenticated `/api/pump/verify` and `/api/pump/import`, plus public `/api/pump/config`. Client cannot submit authoritative name/symbol/creator/verified fields. Import adds or claims one persistent token representation; an existing catalog location/district/color is preserved.
- Verification modules pin official `pump-fun/pump-public-docs` IDL commit `e0687ae9b7e064a0f54efc7297c65eecfbba3a8f`. Supports official create/create_v2 compatible prefixes with bounded Borsh readers. Checks confirmed successful transaction, exact program/discriminator/mint, create-user account equals authenticated signer, mint authority/curve/ATA/global/metadata-or-mayhem/event/program PDAs, successful runtime-attributed CreateEvent and matching fields, mint owner/initialized flag/decimals and Pump-owned curve.
- Runtime event stack ignores foreign nested Program data and failed invocation subtrees. Creator world ownership is original signed creation user; Pump's creator/fee destination is read-only and never changed, including supported fee-beneficiary variations.
- Metadata: allowlisted HTTPS/IPFS hosts, 256KiB streaming limit, timeout, no redirects. Unknown metadata URLs safely yield unavailable image/description; token identity remains on-chain name/symbol.
- Periodic world refresh is still request-driven/polled, no scheduler. Adds read-only batched curve/mint checks. Pump provenance is from the actual PDA owner/discriminator, never a `pump` suffix.
- Active native-SOL curves use real reserves + mint supply/decimals and sourced SOL/USD to display a clearly labeled reserve-derived price/cap. Graduated curves do not determine current market price; DEX data is used and obsolete curve quotes are cleared if no graduated market quote is available. MC still feeds the existing unmodified tower-height renderer.
- Recent observed USD curve quotes stored as snapshots for chart fallback; not reconstructed historical candles. Up to 7 days retained, max 1000 returned. Existing GeckoTerminal charts remain.
- Pump-proven tokens route to a new panel in the existing dashboard slot. Buy/Sell links open exact official `/coin/{mint}` page; UI explicitly tells user to select Buy/Sell there. No invented side deep-link or execution claim. Existing non-Pump catalog entries retain functioning Jupiter swaps.
- Pump token dashboard adds provenance, Pump link, source/method text, official chart/activity link and Trades tab. Activity endpoint decodes confirmed Pump TradeEvent logs from bounded last-eight curve transactions; explicitly not a comprehensive 24-hour feed or PumpSwap indexer.
- Holders remain `Not available` because existing public sources do not provide a reliable indexed total; never estimate/fabricate it. Graduated PumpSwap trades can be viewed on the official Pump token page; native bounded event decoding only covers Pump bonding-curve activity.
- Existing creator bounty, submission, community and presence authorization continue to use the verified creator wallet. No fee collection/claiming/sharing/redirection functions added.

### Preservation and verification evidence

- `git diff --exit-code -- frontend/src/world/ frontend/src/pages/World.jsx frontend/src/App.css backend/catalog.py` passed: these existing visual/map/territory files unchanged.
- World remained 16 original tokens and the same four territory coordinates; no test/public-example tokens retained.
- Successful **read-only real-mainnet creation verification**: mint `2mh3b9fhXhkjqNrUjNqSbR1czsy6sz4Xh3WJkKYvpump`, original creation signature `4T9picqmw7jgntdFJYFGvN3woMqCAcWVM7eF5Zv3bARYjhvCoVXQwyaUjB9DoZTWWPvsguUcQguLVDrC2iXiXB9A`, public creator `JNpVNLrY5b1wkHBx6grNmHge6Zi8K5uqAbZGFBxLSmv`. Token was not imported into the world and no wallet authority/private key was available or invented.
- `/app/test_reports/iteration_2.json`: 34/34 pytest tests passed, zero skipped/failed, frontend desktop/mobile validated. Tests cover auth, malformed/spoofed fields, wrong-wallet rejection on a real Pump creation, mismatched mint/signature, deprecated independent launch410, provenance, activity scope, previous community/bounty behavior. Legacy launch test expectation updated intentionally. Full positive wallet-authorized browser import not executed; no real-user wallet provided.
- Screenshots verified unchanged world, updated launch page with exact official URL, and FARTCOIN Pump panel/Buy-Sell external handoff. FARTCOIN's provenance is verified from actual program-owned graduated curve; other catalog tokens are not falsely labeled Pump.

### Next priorities

P0: creator-authorized browser verify→import validation with an actual owned Pump launch; dedicated RPC/anti-abuse/concurrency hardening before heavy public traffic. P1: reliable holder indexer, fuller confirmed trading history, safe additional metadata hosts if needed, optional supported official SDK metadata+launch. P2: shareable territory links. Do not build an independent mint, liquidity or creator-fee system.
