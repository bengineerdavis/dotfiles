# firefox — changelog

This topic's own history. It travels with the directory, so a topic lifted into
another repository arrives with its history and its edge cases intact. See
`docs/TOPICS.md` § "Per-topic changelog and local edge cases".

Section names come from **antsibull-changelog** — the Ansible community's
changelog tool. *antsibull* is the project's real name, not a typo for *ansible*.
Using its vocabulary keeps a later move to `changelogs/changelog.yaml` a
conversion rather than a rewrite.

    release_summary      short prose; a single string, not a list
    breaking_changes     needs user action on upgrade
    major_changes        large changes across several tasks
    minor_changes        a new option, a new behaviour
    deprecated_features  on the way out
    removed_features     gone, deprecated earlier
    security_fixes       security-relevant, with CVE where there is one
    bugfixes             everything else that was broken
    known_issues         not fixed, or will not be fixed
    trivial              too minor to surface

Entries are dated, not versioned. Drop the sections you do not need — an empty
heading is worse than an absent one. Record upstream behaviour you had to work
around under `known_issues`, and keep the *reason* for the workaround in a
comment beside the task that does it.

<!-- Delete everything above this line once the topic has its first entry. -->

## Unreleased

### minor_changes

- Topic created.
