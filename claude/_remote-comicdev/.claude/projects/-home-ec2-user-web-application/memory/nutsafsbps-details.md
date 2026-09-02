# NUTSAFSBPS Ticket Structure (2026-02-06)

## Epic: NUTSAFSBPS-218「継続日に継続決済の請求を発生させる（退会日以降は発生しない）」

### 完了済み (20 SP)
| Key | Summary | SP |
|-----|---------|-----|
| 219 | モックで与信・売上確定フロー動作 | 12 |
| 220 | 店舗ごとに決済対象の契約を抽出 | 3 |
| 221 | 決済可否をPolicyで判定 | 4 |
| 92 | AIコンテキスト自動更新 | 1 |

### 未完了 (33 SP) - rank優先度順
| Key | Summary | SP | Status |
|-----|---------|-----|--------|
| 222 | Spicaレコード復元（設計再検討含む） | 10 | 進行中 |
| 230 | 強制退会用Policy（ADR-032） | 3 | To Do |
| 223 | Writer本実装（Spicaに結果反映） | 5 | To Do |
| 224 | SBPS API DI切替（Mock→本番） | 2 | To Do |
| 225 | FeatureFlag切替（Spicaバッチ連携） | 2 | To Do |
| 226 | バッチ結果通知 | 2 | To Do |
| 227 | データ移行スクリプト（1ヶ月分復元） | 1 | To Do |
| 229 | 受け入れ準備（手順書等） | 1 | To Do |
| 228 | STG統合テスト・デバッグ | 5 | To Do |
| 231 | AF本番デプロイ・FeatureFlag有効化 | 2 | To Do |

## Key Decisions
- 継続課金決済 + 強制解約を一気に切り替え（段階的ではない）
- NutsFeatureFlagで店舗単位のトグル（カナリアリリースではない）
- AF限定（CFはNotImplementedError）
- Spica ContinueSummaryのContinue（サービス側購入）はSpicaに残す
- ADR-032: SBPS リトライルール - 選択肢2採用（L2-L4早期解約、86/96/L0/L1は翌継続日前日まで）
