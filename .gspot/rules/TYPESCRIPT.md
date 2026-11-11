# TypeScript

Read this rule when you change TypeScript code.

Error output and process exits stay at executable boundaries.

## Values and shapes

Write `T[]` for arrays, and `Array<T>` or `ReadonlyArray<T>` for complex element types.

Use `unknown` plus narrowing for untrusted values. Casts give way to runtime narrowing, typed helpers, or fixing the
source type. Represent known variants with discriminated unions.

Normalize external empty strings, missing fields, and nulls where they enter the program.

## Errors and async work

Use `Promise.all` for a bounded set of independent calls. Use sequential `await` when order, rate limits, or failure
isolation matter. Use runtime concurrency utilities for large fan-out, provider calls, and batch work. Detach a promise
only deliberately. Log and supervise it; never swallow a rejection.

## Naming

### TypeScript types

- Write a `type` alias. Use an `interface` only to merge with a declaration in a `.d.ts` file.
- Avoid return-type-only generics. When you call an existing one, specify the type argument explicitly.
