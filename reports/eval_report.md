# QA Agent Eval Report

Generated: 2026-09-23 04:08 UTC | Model: DeterministicFakeChatModel (offline, no API key)

**10/10 tasks passed**

| Task | Expected tool | Routed tools | Answer check | Pass |
| ---- | ------------- | ------------ | ------------ | ---- |
| calc-1 | `calculator` | `calculator` | ok | ✅ |
| calc-2 | `calculator` | `calculator` | ok | ✅ |
| calc-3 | `calculator` | `calculator` | ok | ✅ |
| calc-4 | `calculator` | `calculator` | ok | ✅ |
| bug-1 | `search_bugs` | `search_bugs` | ok | ✅ |
| bug-2 | `search_bugs` | `search_bugs` | ok | ✅ |
| bug-3 | `search_bugs` | `search_bugs` | ok | ✅ |
| bug-4 | `search_bugs` | `search_bugs` | ok | ✅ |
| sum-1 | `summarize_text` | `summarize_text` | ok | ✅ |
| sum-2 | `summarize_text` | `summarize_text` | ok | ✅ |

## Final answers

### calc-1: Calculate 240 * 16 + 128

```
The answer is 3968.
```

### calc-2: What is (100 - 37) * 2?

```
The answer is 126.
```

### calc-3: Calculate 1024 divided by 32

```
The answer is 32.0.
```

### calc-4: What is 7 * 8 - 6?

```
The answer is 50.
```

### bug-1: Find bugs related to login timeout

```
Here's what I found in the bug tracker:
QA-1042 | Login times out on slow networks (critical, open)
QA-2077 | Login button unresponsive on Safari (major, open)
QA-4150 | Search API timing out under load (major, open)
```

### bug-2: Search open critical defects in the payments flow

```
Here's what I found in the bug tracker:
QA-3301 | Payments: duplicate charge on retry (critical, open)
QA-3090 | Refund webhook not retried on 5xx (major, open)
QA-1042 | Login times out on slow networks (critical, open)
QA-4412 | Mobile app crashes on deep link (critical, in progress)
```

### bug-3: Show me bugs about flaky checkout tests

```
Here's what I found in the bug tracker:
QA-2088 | Checkout E2E tests flaky in CI (major, open)
```

### bug-4: Are there any open issues with the search API timing out?

```
Here's what I found in the bug tracker:
QA-4150 | Search API timing out under load (major, open)
QA-2088 | Checkout E2E tests flaky in CI (major, open)
QA-1042 | Login times out on slow networks (critical, open)
QA-1103 | Password reset email delayed (minor, open)
QA-4412 | Mobile app crashes on deep link (critical, in progress)
```

### sum-1: Summarize this release note: Build 4521 passed all smoke tests. Three flaky tests were quarantined. The release is approved for rollout.

```
Summary:
Build 4521 passed all smoke tests. Three flaky tests were quarantined. The release is approved for rollout.
```

### sum-2: Summarize in 2 sentences: The nightly regression suite ran 1,240 tests. 1,198 passed and 42 failed. Most failures were traced to a stale test-data fixture. The fixture was refreshed and the suite is green again.

```
Summary:
The nightly regression suite ran 1,240 tests. 1,198 passed and 42 failed.
```
