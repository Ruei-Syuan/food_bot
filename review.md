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
