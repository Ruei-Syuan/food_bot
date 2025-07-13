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
- `kwargs` to accommodate future dynamic requirements.
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

## search function

## google_command function

- 大部分結構都有使用 early return, Great Job!

- 部分 config 可以抽成 app env
  - GOOGLE_MAP_API_USAGE_FILE
  - GOOGLE_MAP_API_KEY
  - GOOGLE_MAP_API_DAILY_QUOTA

- Highly nested structure 會導致可讀性變差 (eg. flex bubbles)
  -> 用 **generator yielding** 的形式，盡量減少 structure indent

- list item filter, list item transform
  -> 可使用 `filter`, `map` function, 可讀性++ & SRP up
  （說明: why list function is better than for-loop）
