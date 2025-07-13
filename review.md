# Code Review

## Incomplete dependencies

- `pip freeze > requirements.total.txt`

## Flask App factory pattern

## Linebot API structure

- [reference](https://github.com/line/line-bot-sdk-python?tab=readme-ov-file#synopsis)
  - Avoid manually parsing request if SDK is available
- Learn to code from digging into src code (eg. `event.source`, deprecated messages)

## store_note function

- consistent naming convention (in python generally snake case for function name)
- Use **early return** to avoid unbalanced if block statement.
- **Explicit** is better than implicit:
  - avoid short-handed if possible (eg. tk = token)
  - Pass keyword-arguments into function if variables' name is not clear enough.

## get_note function

- Transform iterable items with `map`
- Function Expansion: `linebot_reply_message`
  - Extend reply message from pure str to Message instance compatible.
  - 設計 function 時不會一蹴可及，但如何優雅的擴充功能是值得花思考的。
    重點： 保持 `linebot_reply_message` 的功能單純 (核心一樣是 reply message)，但接受非 `TextMessage` 以外的選項
