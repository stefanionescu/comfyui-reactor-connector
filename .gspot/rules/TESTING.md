# Testing

Read this rule when you write or change a test.

A useful test fails when the behavior it covers breaks. A test proves a behavior that a user can observe, a security
guarantee, a fixed bug, or a platform difference. One behavior gets one test, at the cheapest level that can fail.

## Assertions

- Test behavior, not private implementation details.
- Assert the values a behavior produces: status codes, exit codes, error codes, IDs, and structured fields.
- Compare message text only when the text itself is the output under test, such as the help of a command.
- Do not pin incidental configuration or internal representation.
- Cover relevant empty and null inputs, limits, expected errors, and unexpected internal ones.
- Assert every changed result: responses, stored rows, outbound requests, side effects, and logs.
- A test has meaningful assertions; it does not only prove that the code called a collaborator. No test asserts a fake's
  own return value.
- Use snapshots only for stable data, and review every change to them.
- Do not add test-only authentication bypasses, magic headers, or bypass routes.
- No test pins a constant, a default, a message, a table, help text, or generated text that no behavior depends on. A
  test runs code and checks its result.
- No test checks a library, the language, a wrapper, or the test setup.
- Before you keep a new test, break the code it covers and see the test fail. A test that expects no finding needs a
  break that makes the check report.
- Add a table row only when you can name a bug that fails it and no other row. A table with one case is a plain test.
- Do not export a function only so that a test can call it. Test it through the public function that uses it.
- Test the behavior that exists. Never write a test that proves the absence of a feature, option, setting, export, or
  file that the project removed or decided against. When you remove a feature, delete its tests.

## Mocks

- Mock only what leaves the process: network, filesystem, subprocesses, clock, and database. Never mock the code under
  test or provider SDK internals.
- Mock the module that calls the network or database. Use dependency injection when the code declares the dependencies.
  Replace that whole module rather than hiding parts of its behavior.
- Keep mocks that affect the result in the arrange step. Reset or redefine shared mocks before each test; do not turn on
  automatic mocking for the whole suite.
- Restore environment variables, globals, fake timers, and spies changed by a test.

## Placement and names

- Put builders, fakes, servers, and database code in one folder beside the tests, named for what it holds, such as
  builders. Never name it `mocks/`, `helpers/`, `utils/`, `support/`, or `shared/`. These files hold no
  assertions or test blocks.
- A test name states the scenario and expected result. Never use `test1`, `works`, `edge cases`, or `happy path`. Group
  tests by unit, then scenario.

## Test data

- Each test creates its records directly or through an explicit builder. It does not depend on execution order, mystery
  seed state, or a globally empty database.
- Use fixed, descriptive names, emails, IDs, and references. Add a per-run suffix only for rows in a shared database.
- Do not share mutable IDs between tests or count unrelated data. Add unrelated records when a test must prove that the
  code leaves them unchanged.
- Test data does not copy the version of the project or of a tool.
- Do not use fixed sleeps. Use bounded polling, fake timers, or a signal that proves completion.

## Network and providers

- Block unexpected external HTTP calls. Allow only the local service under test unless the suite explicitly opts into a
  real provider through an environment variable absent by default.
- Assert outbound URLs, methods, safe headers, timeouts, and bodies. Never assert on secrets or full sensitive payloads.
- Where the module recovers, test timeouts, 5xx, 429, malformed JSON, missing fields, and rejected promises. Fake
  responses fail when a payload lacks required fields.
