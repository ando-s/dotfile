---
name: internal-api-client-skips-parameter-filter
description: 内部APIはRailsのルーターを直接呼ぶためfilter_parametersがリクエストに載らず、Parametersログで何も伏せられない
metadata: 
  node_type: memory
  type: project
  originSessionId: 1073c2dc-37ab-4b85-87ca-88982d60e785
  modified: 2026-08-20T07:33:49.658Z
---

`InternalApiClient`（`packs/nuts/core/lib/internal_api_client.rb`）は `Rack::MockRequest.env_for` で env を組み、`Rails.application.routes.call(env)` を呼ぶ。`Rails.application.call` を経由しないため `Rails::Engine#build_request` の `env.merge!(env_config)` が走らず、env に `action_dispatch.parameter_filter` が入らない。

`ActionDispatch::Http::FilterParameters#parameter_filter` はこのヘッダが無いと `NULL_PARAM_FILTER` を使う（actionpack 8.0.2）。結果、内部APIのリクエストでは ActionController の「Parameters:」ログで**パスワードやメールアドレスすら伏せられない**。

**Why:** `config/initializers/filter_parameter_logging.rb` に伏せたい値を足しても、内部APIの Parameters ログには効かない。「filter_parameters に足したから伏せた」と結論すると、内部API経路の平文が残ったままになる。

**How to apply:**
- 伏せる値を追加する変更では、外側の口（Nuts利用者が受ける口）と内部API（`/nuts/...`）の両方でログを実測して確認する。
- lograge（`config/initializers/lograge.rb`）と Sentry（`config/initializers/sentry.rb`）は `Rails.application.config.filter_parameters` を `ActiveSupport::ParameterFilter` に直接渡すため、env ヘッダとは無関係に一覧が効く。lograge は production/staging のみ有効。
- 内部APIの Parameters ログでも効かせるなら、`InternalApiClient` が env に `action_dispatch.parameter_filter` を載せる必要がある。
- 実測の出所: カード変更のE2E（`PUT /credit_card/v3/customer_info` と `POST /nuts/card/card_change/start` で `token` / `billing_full_name` が平文）。
- 関連: [[escott-sonypayment-primary-source-facts]]（トークンは1回使用または30分で無効）
