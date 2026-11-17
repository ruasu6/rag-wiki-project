# S02 Ingest 執行反思

## 證據範圍

本文件依據 `workflow/execution-log.jsonl` 中 run `S02-20261116T172751+0800` 的 16 筆 S02 事件、目前的 `sources.json`、`raw/S01.md`、`raw/S02.md` 與六份 Wiki 文件撰寫。它不代表重新 ingest S01 或 S02，也沒有為 S03 建立任何執行結果。

## 實際執行結果

| 節點 | Attempt | 實際結果 | 證據摘要 |
|---|---:|---|---|
| Preflight | 0 | PASS | AWS 登記資料、發布者、URL、標題、正文及指定內容均確認可用。 |
| Retrieve | 0 | PASS | 取得 AWS 正文、四步驟流程與 production-level components；頁面未提供可辨識更新日期。 |
| Normalize | 0 | PASS | 建立 `raw/S02.md`；整份 UTF-8 檔案 SHA-256 為 `fb251323176df17c8fa1eddd7cf239a77dd2f5f63597ac7bd555203f6a66f3a9`。 |
| Extract | 0 | PASS | K01–K06 均具有 source ID、原文章節、URL 與繁體中文摘要。 |
| Map to Wiki | 0 | PASS | 映射至 01、02、03、04；02 為主要頁面。 |
| Stage Update | 0 | PASS | 四份候選頁建立於暫存目錄；正式 Wiki 在 staging 期間未變。 |
| Validator Self-check | 0 | PASS | 單一有效、多個／多行有效、單一無效連結 fixture 得到當時預期結果。 |
| Validate Wiki | 0 | FAIL | `VALIDATION_INTERNAL_ERROR`；predicate 未把 `cmp` 的非零狀態傳回上層。不是 Wiki 內容失敗。 |
| Repair #1 | 1 | PASS | 修 validator；staged Wiki 未改。 |
| Validator Self-check | 1 | PASS | 有效連結 exit 0、無效連結 exit 1、exit probe 預期及觀察值皆為 7。 |
| Validate Wiki | 1 | PASS | V01–V09 通過，包含語意審查與程式檢查。 |
| Commit | 1 | PASS | 四份 Wiki 寫入，且 staged 與 committed 檔案一致。 |
| Post-commit Metadata Validation | 1 | FAIL | `VALIDATION_INTERNAL_ERROR`；錯誤的 hard-coded S01 prefix byte count 造成假性 hash mismatch。不是 metadata 實際不一致。 |
| Repair #2 | 2 | PASS | 修 post-commit validator；Wiki 與 source metadata 均未改。 |
| Post-commit Metadata Validation | 2 | PASS | S02 status/hash/time、正式頁面、S01 保存、S03–S06 狀態及內部連結均通過。 |
| Execution Log | 2 | PASS | 保留 13 筆 S01 事件並新增 16 筆 S02 事件，合計 29 筆。 |

S02 最終成功標記為 `INGESTED`，但已用完每個來源最多兩次 Repair 的額度。

## 兩次實際 Repair

### Repair #1：exit code 與 prefix predicate

第一次 Validate 的失敗不是候選 Wiki 有錯，而是驗證 harness 在 `cmp` 回報 EOF／非零狀態後仍繼續輸出 PASS。實際修正包含：

- 要求每個 validation predicate 明確傳遞非零 exit code。
- 以明確的 byte-prefix SHA-256 comparison 取代原本的 `cmp` prefix 比對。
- 不修改 staged Wiki 內容。
- 修正後以 exit-status probe 驗證：預期 7，實際觀察 7；再執行 Validate，結果 PASS。

### Repair #2：動態段落邊界

第一次 post-commit 檢查使用錯誤的 hard-coded S01 prefix byte count，因此把已保存的 S01 內容誤判為 hash mismatch。實際修正包含：

- 移除固定 prefix byte count。
- 依 `## S02 補充` 標記尋找 S02 區段起點，再計算前段的 SHA-256。
- 推導出的 S01 prefix 長度為 2572 bytes。
- 修正時沒有改動 Wiki 內容或 `sources.json` metadata。
- 修正後 post-commit metadata validation PASS。

## Workflow 問題與改進原因

1. **早期 self-check 覆蓋不足。** Attempt 0 只測連結 fixture，沒有測 predicate 的 exit code、SHA-256 正反例及動態 boundary，因此 self-check PASS 後仍發生兩次 validator internal error。
2. **臨時 Shell 驗證不適合作為長期核心。** 驗證邏輯散落於一次性命令時，shell 狀態傳遞、引用、byte count 與不同節點的實作容易不一致，也欠缺固定的輸出 schema。
3. **失敗類型需要先分類。** S02 兩次失敗都屬於 validator，而非 Wiki 或 metadata；若未區分，可能錯改已正確的內容。
4. **段落保存不能依硬編碼長度。** Wiki 增補後 byte offset 會改變。唯一且格式正確的段落標記比固定 byte count 可維護；標記缺失、重複或格式異常時應停止，而非猜測。
5. **兩次 Repair 是整個來源共用的風險預算。** Validator、內容與 metadata 修正均計入同一上限。S02 已用完兩次；若最終檢查仍失敗，依新流程應停止並標記 `NEEDS_REVIEW`。

## 本次已實作的 Workflow 改進

- 更新 `workflow/graph.md`，分開 `VALIDATOR_INTERNAL_ERROR`、`WIKI_CONTENT_VALIDATION_FAILURE` 與 `METADATA_INCONSISTENCY` 的修正路徑。
- 明定每個來源共用最多 2 次 Repair：實際修改 validator、staged content 或 metadata 才增加一次；驗證重跑本身不增加。Repair 自身失敗仍消耗額度。
- 新增可重複使用的 `workflow/validate_ingest.py`（本次測試版本 SHA-256：`5231e4a4d5d35b6874151d4fc37d6d5654e6fa52e394457c28d57c2efad2199b`），統一結構化 JSON 結果及非零 exit code。
- Self-check 現在涵蓋：exit code 傳遞、正確／錯誤 Markdown 連結、多個與換行連結、SHA-256 相符／不相符、動態段落邊界，以及缺失、格式異常、重複標記。
- 新工具另提供正式 Wiki link、source/raw hash、JSONL 結構、既有 log prefix 與動態 Wiki prefix 檢查。

這些是本次工作新增的流程與工具，不應誤寫成 S02 ingest 當時已存在的完整工具鏈。

## 本次實際相容性測試

測試日期為 2026-11-16（Asia/Taipei）。以下命令在目前 S01、S02 檔案上實際執行；沒有重新 ingest，也沒有修改 Wiki：

| 測試 | 實際結果 | 證據 |
|---|---|---|
| Validator self-check | PASS（10/10） | 包含 exit code、連結、SHA-256、boundary、缺失／異常／重複標記。 |
| 正式 Wiki 內部連結 | PASS | 檢查 6 檔、17 個連結、0 個 broken link。 |
| S01 registry/raw 一致性 | PASS | `INGESTED`；raw SHA-256 `3941157a19fbc106add6d5c6b273cf0c4bc936cfcd2e9c97451ee5eeda2e08e8` 與登記相符。 |
| S02 registry/raw 一致性 | PASS | `INGESTED`；raw SHA-256 `fb251323176df17c8fa1eddd7cf239a77dd2f5f63597ac7bd555203f6a66f3a9` 與登記相符。 |
| S01 introduction prefix 保存 | PASS | 由完整標記 `## S02 補充：從生命週期看 RAG` 動態求得 2572 bytes；prefix SHA-256 為 `ce51a7521510ac6ee367bcc6763b4d2d908d69c897be3a232f7390e09f644def`。 |
| Execution log 結構 | PASS | 29 筆有效 JSONL，source IDs 僅 S01、S02。 |
| S01 log prefix 保存 | PASS | 前 13 行 SHA-256 為 `1f7533a8516628305eb0247c88eadc6da939c03a3618354c560df69e708c0691`。 |

測試只證明目前工具對既有檔案的結構與一致性相容；它不能單獨重新證明所有 Wiki 知識主張的語意正確性。S01、S02 ingest 當時已留下的語意審查證據仍以原 execution log 為準。

## 尚待驗證

- 新 validator 尚未用於 S03 的完整 Ingest → Validate → Repair → Commit 流程，因此它能否在新來源端到端避免相同錯誤，尚待 S03 實際執行驗證。
- 動態 boundary 依賴唯一且格式正確的二級標題；工具會拒絕缺失、異常或重複標記，但不同 Wiki 合併策略是否需要其他 boundary schema，尚待後續來源驗證。
- 來源支持程度、AWS／通用能力界線、初學者可讀性與跨來源矛盾仍需要人工／語意審查，不能只用程式測試取代。

在開始 S03 前，應先固定本次 validator 版本或 hash、執行 self-check，並在 execution log 記錄 fixture 與 exit code 結果。就目前 S01、S02 的結構相容性與流程文件而言，已具備開始 S03 preflight 的條件；S03 尚未執行。
