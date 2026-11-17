# S01 Ingestion 執行反思

## 反思範圍與證據

本文件只根據以下已存在的執行證據撰寫：

- `workflow/execution-log.jsonl` 中 run `S01-20261116T165358+0800` 的 13 筆事件。
- `raw/S01.md` 的來源資訊、正規化章節索引與 K01–K06 知識萃取。
- `wiki/01-introduction.md`、`wiki/05-retrieval.md`、`wiki/06-evaluation.md` 的正式提交內容。
- S01 執行時使用的原 workflow graph。

本文件不把此次沒有獨立執行的檢查寫成既成結果。後文的 `Validator Self-check` 與 `Post-commit Metadata Validation` 是根據 S01 經驗提出並加入未來 graph 的改進節點；其實際效果尚待後續來源執行驗證。

## 實際執行節點與結果

| 順序 | Node | Attempt | 結果 | 實際證據摘要 |
|---:|---|---:|---|---|
| 1 | Preflight | 0 | PASS | 登記資料完整；發布者、URL、標題相符；正文與必要章節可取得。 |
| 2 | Retrieve | 0 | PASS | 取得 Google Cloud HTML 正文；不是搜尋摘要或錯誤頁；頁面未提供可辨識更新日期。 |
| 3 | Normalize | 0 | PASS | 建立 `raw/S01.md`，正規化 7 個章節；來源與 AI 摘要分離；記錄 SHA-256。 |
| 4 | Extract | 0 | PASS | 產生 K01–K06；各項都有 S01、原文章節、URL 與繁體中文摘要。 |
| 5 | Map to Wiki | 0 | PASS | 映射至 `01-introduction.md`、`05-retrieval.md`、`06-evaluation.md`。 |
| 6 | Stage Update | 0 | PASS | 三個候選頁先建立於暫存目錄，正式 Wiki 在此節點未變更。 |
| 7 | Validate | 0 | FAIL | 內部連結測試器發生 `VALIDATION_INTERNAL_ERROR`；不是 Wiki 內容失敗。 |
| 8 | Repair #1 | 1 | PASS | 修正內部連結驗證器的逐行處理；staged Wiki 內容未變更。 |
| 9 | Validate | 1 | PASS | V01–V08、內容 hash、引用與內部連結檢查通過。 |
| 10 | Commit | 1 | PASS | 三個 Wiki 頁正式提交；S01 當時更新為 `INGESTED`；S02–S06 保持原狀。 |
| 11 | Repair #2 | 2 | PASS | 將 `ingested_at` 從 pre-commit 時間修正為正式檔案可觀測的 commit 時間。 |
| 12 | Validate | 2 | PASS | V01–V08、`sources.json`、raw hash、正式連結與 S02–S06 狀態均通過。 |
| 13 | Execution Log | 2 | PASS | JSONL 記錄共 13 筆，沒有合成成功紀錄。 |

## 第一次 Validate 失敗：VALIDATION_INTERNAL_ERROR

第一次 Validate 的失敗點是 `internal_link_test_harness`。執行紀錄顯示，shell 把多個以換行分隔的 Markdown 連結目標合併成一個值，再把合併後的字串當成單一路徑檢查，因此回報錯誤的 `BROKEN` 結果。

這次失敗的性質是驗證器內部錯誤，而不是內容錯誤：

- `content_failure` 明確記為 `false`。
- 三個 staged Wiki 檔案本身沒有因這次失敗而修改。
- 錯誤發生於測試器處理多行輸入的方式，不能用來推論 Wiki 連結真的失效。

## Repair #1：修正內部連結驗證器

Repair #1 將驗證器改為一次處理一個以換行分隔的 Markdown 目標，避免把 `01-introduction.md`、`05-retrieval.md`、`06-evaluation.md` 合併成單一路徑。

已實際執行的修正與結果：

- 修改對象是 validator，不是 staged Wiki。
- `staged_content_changed` 為 `false`，`validator_changed` 為 `true`。
- 修正後重新執行 Validate，V06 確認三個 Markdown 目標都能在 staging set 中解析。
- 同次 Validate 也完成 V01–V08 與 content hash 檢查，結果為 PASS。

## Repair #2：修正 ingested_at

Commit 前先取得的時間被寫入 `ingested_at`，但正式檔案實際寫入完成後，可觀測的 commit file time 為 `2026-11-16T16:57:47+08:00`。Repair #2 將 S01 的 `ingested_at` 校正為該時間。

已實際執行的修正與結果：

- 只修正 S01 的 metadata 時間。
- Wiki 內容沒有改變。
- S02–S06 的來源資料沒有改變。
- 修正後執行 attempt 2 的 Validate，確認 `sources.json` 有效、raw hash 與 registry 相符、正式內部連結可解析，且 S02–S06 仍為 `PLANNED`。

執行紀錄能證明修正後的一致性，但沒有獨立保存 commit 作業開始與完成兩個時間點的完整 transaction trace；因此更細緻的 commit latency 分析尚待驗證。

## 兩次 Repair 與最終結果

| Repair | 類型 | 是否修改 Wiki 內容 | 後續結果 |
|---|---|---|---|
| #1 | Validator 修正 | 否 | Validate attempt 1：PASS |
| #2 | Post-commit metadata 修正 | 否 | Validate attempt 2：PASS |

兩次 Repair 已用完原 workflow 的最多兩次修正額度。最終驗證結果為 PASS，S01 保持 `INGESTED`；raw note、三個正式 Wiki 頁面、`sources.json` 與 execution log 之間的一致性檢查也通過。

## 從 S01 觀察到的 Workflow 問題

### 1. Validator 本身沒有在內容驗證前先做 self-check

第一次 Validate 因測試器錯誤而失敗，並消耗一次 Repair。這表示內容驗證器也可能是失敗來源，不能假設 validator 執行完成就代表結果可信。

### 2. 原 Repair 定義與實際修正範圍不一致

原 graph 將 Repair 描述為修正 staged output，但 S01 的兩次修正分別作用於 validator 與 metadata，兩者都不是 staged Wiki 內容。未來流程需要讓 Repair 明確辨識 `validator`、`content` 與 `metadata` 三種修正目標，並回到相對應的檢查節點。

### 3. 原流程在 Commit 後直接進入 INGESTED，缺少 metadata 完成檢查

S01 在 Commit 後才發現 `ingested_at` 應以正式寫入的可觀測時間校正。這表示 Commit 成功與 metadata 正確是兩件事；若沒有 post-commit 檢查，來源可能帶著不精確的 metadata 被視為完成。

### 4. 同一 Repair 上限同時承擔不同類型錯誤

S01 的兩次額度分別用於 validator 與 metadata，沒有用於 Wiki 內容。是否應為 validator、content、metadata 設定各自的重試額度，目前資料不足，尚待更多來源執行後決定。此次 graph 仍保留共用的最多兩次 Repair 上限，以避免在單一案例後直接擴大自動重試。

### 5. 部分驗證時間只記錄 batch checkpoint

execution log 已明確註記：部分個別檢查沒有各自獨立的命令時間，使用的是 batch validation checkpoint。若未來需要分析每項 validator 的耗時或先後關係，現有時間粒度不足；相關記錄方式尚待實作與驗證。

## 未來 Graph 改進建議（尚未實作於 S01）

### Validator Self-check

在正式 Validate 前，先使用已知正確與已知錯誤的 fixture 檢查 validator：

- 多個換行分隔的有效連結必須逐一解析並通過。
- 指向不存在檔案的連結必須被偵測。
- validator 的非零退出狀態必須能正確傳遞。
- self-check 失敗時，不得把結果歸因於 Wiki 內容。

此節點已加入未來 graph，但 S01 執行時沒有獨立的 `validator_self_check` 事件，因此其實際攔截效果尚待驗證。

### Post-commit Metadata Validation

在 Commit 後、正式標記 `INGESTED` 前檢查：

- 正式檔案與通過驗證的 staged output 一致。
- raw file SHA-256 與 `sources.json.content_hash` 一致。
- `retrieved_at`、`ingested_at` 與狀態完整且時間關係合理。
- `ingested_at` 反映可觀測的 commit 完成時間，而不是 pre-commit 取樣時間。
- 非本次來源的 metadata 沒有被改動。

此節點也已加入未來 graph。S01 曾在 Commit 後人工／程式化發現並修正 metadata，但當時並沒有以獨立的 `post_commit_metadata_validation` node 執行；新節點的自動化行為尚待後續來源驗證。

## 已執行修正與未來建議的界線

### 已實際執行

- 修正內部連結 validator 的逐行處理。
- 重新執行 Validate 並通過 V01–V08。
- 校正 S01 `ingested_at`。
- 執行最終一致性驗證並通過。

### 尚未實作或尚待驗證

- 在 Validate 前自動執行獨立的 Validator Self-check node。
- 使用固定 fixture 驗證 validator 的 true-positive 與 true-negative 行為。
- 在 Commit 後以獨立 node 自動驗證 metadata，再決定是否標記 `INGESTED`。
- 為 validator、content 與 metadata 設定分離的 Repair 額度。
- 為每一個 validator 記錄獨立開始與結束時間。
