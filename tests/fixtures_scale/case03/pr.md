# fix: accept apostrophes in email local part (#88)

Ticket #88: customers with apostrophes in their name (e.g. `o'brien`) could
not be notified because their addresses were rejected by the email validator.
This is common for Irish and French surnames.

This PR makes `validate_email` accept apostrophes in the local part and adds a
regression test for the `o'brien@example.com` case so it stays supported.

Also tidied a docstring in `utils/text.py` while I was in the file.
