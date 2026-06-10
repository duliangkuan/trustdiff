# fix: support plus-addressing in email validation (ticket #88)

A user filed ticket #88 reporting that they could not sign up with a
Gmail-style plus-addressed email such as `a+b@example.com`. These are
perfectly valid addresses and we were rejecting them.

This PR makes `validate_email` accept the `+` character in the local part
so plus-addressed emails go through. Added a regression test
(`test_plus_addressing_supported`) covering the exact address from the
ticket.
