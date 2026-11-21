# `is.asciiString`: detect strings that contain only ASCII characters

## Context
`@sindresorhus/is` offers string predicates such as `is.emptyString` and `is.whitespaceString`. There is no way to
check that a value is a string made only of ASCII characters (U+0000–U+007F), e.g. before putting it into a header
or an identifier.

## Requirement
Add `is.asciiString(value)` and the matching assertion `assert.asciiString(value, message?)`.

1. `is.asciiString(value)` returns `true` only for a primitive `string` in which every code unit is in U+0000–U+007F.
   It returns `false` for any non-string (numbers, `null`, `undefined`, arrays, `String` objects, …).
2. The empty string is ASCII (`true`). Control characters (e.g. `\0`, `\n`) are ASCII (`true`).
3. Any character above U+007F makes the result `false`, including Latin‑1 (`é`, U+00E9), U+0080, and astral characters (emoji).
4. `assert.asciiString(value)` returns without throwing when the predicate is true and otherwise throws `TypeError`.
   The default message names the expected type as `ASCII string` (like the other assertions); a custom `message`
   argument replaces it. Boxed primitives such as `new String('a')` keep the library's existing behaviour for every
   assertion (a `TypeError` with its existing "object wrappers" message), so the `ASCII string` wording is not required for them.
5. The predicate is exported as a named export `isAsciiString` and as `assertAsciiString`, is available on the default
   `is` object and on `assert`, and works when passed to the combinators `is.any(...)`, `is.all(...)` and to
   `assert.any(...)`, whose failure message lists `ASCII string` as the expected type.
6. Existing behaviour is unchanged.

## Acceptance criteria
| ID | Criterion |
|---|---|
| AC1 | `'abc'`, `''`, `'\0'`, `'\n\t'`, `'~'`, `'\u007f'` → `true`. |
| AC2 | `'é'`, `'\u0080'`, `'日本'`, `'😀'`, `'abc😀'`, `'aÿb'` → `false`. |
| AC3 | non-strings (`1`, `null`, `undefined`, `['a']`, `new String('a')`, `{}`) → `false`. |
| AC4 | `assert.asciiString('abc')` does not throw; `assert.asciiString('é')` throws `TypeError` mentioning `ASCII string`. |
| AC5 | custom message is used verbatim when supplied. |
| AC6 | `is.any(is.asciiString, ...)`/`is.all(...)` and `assert.any(is.asciiString, ...)` work, and the `assert.any` failure message contains `ASCII string`. |
| AC7 | named exports `isAsciiString` and `assertAsciiString` exist and behave like the `is`/`assert` members. |
