# Writing and proving tests

Mechanics for the two test kinds beyond plain examples: mutation proving,
properties, and fuzzing. `AGENTS.md` § Tests carries the rules that bind;
this file carries the how.

### Prove the test fails

`spec.md` § Verification says a test is not finished until it has been seen to
fail. This is how: break the code on purpose and watch the suite go red. It is
mutation testing done by hand, and it is cheap.

```bash
cp home/bin/executable_thing /tmp/thing.good          # keep the original
# edit the target: invert a guard, neuter a mechanism, make an error
# path return a positive value instead of "unknown"
uv run --with pytest pytest tests/thing -q       # MUST fail, and on the right test
cp /tmp/thing.good home/bin/executable_thing     # restore
uv run --with pytest pytest tests/thing -q       # green again
```

Mutations worth trying, in rough order of what has actually bitten here:

- **make the guard unconditional** — `if ordered and not cleared:` -> `if True:`
- **make it never fire** — the same line -> `if False:`
- **turn "unknown" into a claim** — `return None` -> `return set()` on an error
  path. This one skipped every case that declared a requirement and reported a
  clean run
- **move a definition below its first use** — bash resolves at call time, so the
  helper becomes "command not found", returns 127, and a fail-closed guard passes
  for the wrong reason

Read WHICH tests fail, not just how many. Of four regressions injected across the
eval harness, three were caught and the fourth was not — and that fourth revealed
the TEST was wrong: its fixture had no blank line inside the prompt, so
`rfind("\n\n")` landed on the seam by accident and the assertion passed either
way. A mutation that survives is either a coverage gap or a broken test, and both
are worth the two minutes.

Where a mechanism can decline, the mutation that matters is the one that makes it
decline ALWAYS — because refusing looks identical to not running. Same reason
`tests/policy/test_policy_callers.py` flips the policy to permit and asserts the
behaviour changes.

**A stub that writes nothing cannot test that nothing was written.** When the
assertion is `assert not path.exists()` or `read_state() == {}`, any fake that
declines to write satisfies it — including one that ignores the behaviour under
test entirely. Pointed at a no-write stub, such a test passes whether or not the
code honours its guard. Reduce it to a property instead: assert the state the
code *should* have written, then that this run wrote none of it. Measured
2026-11-09 while triaging DOT-329's six gita tests: two of the six looked
hermetic-replaceable, but only `test_missing_work_root` survived the check —
the other needed a state-writing fake, so skipping it was correct. The
conclusion held; the reasoning that produced it did not.

Two harness traps found here, worth checking for in any suite you touch:

- A test path pointing at a file that does not exist. `tests/clipped.bats` used
  `$BATS_TEST_DIRNAME/../clipped` — the repo root — so every case ran against a
  missing binary, and the one case that "passed" did so because a nonexistent
  command also exits nonzero.
- GNU-only syntax in a portability test. `script -qec` is GNU; BSD `script` has no
  `-c`, so two TTY tests could never pass on macOS whatever the code did. Use
  `pty.openpty()`.

Record the evidence on the commit as trailers, not prose: `Mutation: <what was
broken>` and `Failing-test: <the test that went red>`. `spec.md` § Verification
makes this a SHALL. The mutation state is never committed, so the proof can only
live in the trailer, and only trailers are greppable — `git log --grep`
over the history yields every mutation ever proven; a prose sentence in a body
yields nothing.

### Properties and fuzzing

Most tests here are examples: a specific input, a specific expected result. Two
other kinds earn their place in specific situations.

**Write a property test when a rule holds for every input, not just the one you
thought of.** Pure functions with algebraic structure are the candidates — merge,
path-set, set-difference, normalisation, formatting. `spec.md` § Verification —
invariants are tested as properties says when this is required.

The rule is the test. State it without reference to how the code works: if your
property recomputes the function under test, it only proves the code equals
itself. Good properties look like "content survives", "the result is a subset of
what was asked for", "running it twice gives the same answer", "it never
mutates its input".

House examples: `tests/ollama_evals/test_harness_property.py` and
`tests/binned/test_binned_property.py`. Add `--with hypothesis` to the run
command; it is already in the one under § Commands.

Two things to watch:

- **A property that passes immediately may be testing nothing.** An `assume()`
  that is too tight filters away every generated input and hypothesis still
  reports a pass. This is the generated-input version of grepping an empty
  string. Check that the property is seeing real data before you trust it.
- **When a property fails, keep the counterexample.** Hypothesis shrinks the
  failure to its smallest form. Commit that as its own example test alongside
  the fix. It is the cheapest regression test you will ever get for that bug,
  and the generator is under no obligation to produce it again.
  `test_set_path_names_the_path_when_a_segment_is_not_a_mapping` is one: the
  property found that a mis-typed sweep path died with a bare `'int' object does
  not support item assignment`, naming neither the case nor the field.

**Fuzz where input arrives that you did not produce.** In this repo that means
model output, hand-edited YAML cases, and policy layer files. Model output is the
sharpest of the three, because the producer is a sampling process rather than a
program — empty responses, truncation mid-token, echoed prompts and control
characters are all normal. A harness that raises on those reports its own defect
as a model failure, which is the worst thing a discriminator can do.

Fuzz the data, not the code path that executes it. `run_check` runs `exec()` on
the check source, so the tests generate hostile *responses* and draw broken
*sources* from a fixed list. Generating source text to `exec()` would be running
arbitrary generated code.

Properties and fuzzing do not replace the mutation check above. Break the code
and watch the property go red, the same as any other test.

