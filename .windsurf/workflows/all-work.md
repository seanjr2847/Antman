---
description: All workflow
---

# AI Development Automation Instructions

## 1. Direction
'''
Present an overview of what you will do.
Do not generate any code until I tell you to proceed.
All answer should be in Korean.
'''

## 2. Complete Workflow Execution
**AI Instruction:**
```
Execute steps 3-8 in sequence automatically:
- Auto-proceed to next step when current step completes
- Handle errors at each step before continuing
- Minimize user intervention throughout the process
- Provide comprehensive summary report upon completion
- Include metrics: time taken, iterations needed, success rate
- Flag any issues that require human attention
```

## 3. Unit Test Creation
**AI Instruction:**
```
Write comprehensive unit tests for the following functionality:
- Include happy path, edge cases, and error handling
- Use [Jest/PyTest/etc] testing framework
- Mock all external dependencies
- Achieve 80%+ test coverage
- Follow testing best practices and naming conventions
```

## 4. Cursor Code Generation
**Cursor Instruction:**
```
@test-file.test.js Write code that passes all these tests.
- Understand the full codebase context before writing
- Maintain consistency with existing code style
- Consider error handling and type safety
- Add appropriate code comments
- Ensure clean, readable, and maintainable code
```

## 5. CI/CD Pipeline Setup
**AI Instruction:**
```
Set up a CI/CD pipeline with the following requirements:
- Auto-trigger on Git push
- Output detailed logs on test failures
- Send failure notifications via email
- Save test results as artifacts
- Include build status badges
```

## 6. Composer Error Fixing
**Composer Instruction:**
```
The CI/CD pipeline failed with the following test logs. Analyze all errors and fix them at once:

[Paste logs here]

Please:
- Explain the root cause of each error
- Provide the fix strategy
- Implement the actual code fixes
- Verify no other functionality is affected
- Test the fixes locally if possible
```

## 7. Iterative Execution
**AI Instruction:**
```
Repeat the following process until all tests pass:
1. Execute step 6 error fixing
2. Git commit and push changes
3. Check CI/CD results
4. If failed, return to step 1
5. Maximum 5 iterations before stopping

Provide a progress summary after each iteration.
Stop if infinite loop detected.
```

## 8. Final Verification
**AI Instruction:**
```
Perform final verification by:
1. Retrieving the backup original test files
2. Verifying current code passes original tests
3. Comparing test files for any unauthorized changes (diff)
4. Creating a final validation report

If original tests fail, fix the code accordingly.
Ensure no test tampering occurred during the process.
```