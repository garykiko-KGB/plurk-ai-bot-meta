hello，

這個 AI Bot 最初的目的是想做出一個在 Plurk 生活的 AI。

它永遠知道自己是 AI。

但是它努力通過圖靈測試。

====================

目前進度

☑ 基本架構完成
☑ Plurk OAuth
☑ Gemini 串接
☑ 足球模組
□ 自動發文
□ AI 行為系統
□ 多平台

====================

目前架構

AI Anchor

core/        系統核心
services/    平台服務
ai/          AI 本體
modules/     可選功能模組
behavior/    AI 行為控制
prompts/     Prompt 管理
data/        資料存放

====================

現況問題：
/n
Issue #001：getFriendRequests() 回傳 HTTP 200，但 response body 為空，導致 JSONDecodeError。 /n
狀態：Pending。 /n
下一步備案：研究是否改用 addAllAsFriends() 或其他現行 Friends API。 /n
