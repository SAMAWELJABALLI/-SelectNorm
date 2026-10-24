# Security

This is research code; it runs no service and handles no user data. Two kinds of report are still welcome and should be sent privately to the repository owner through GitHub rather than as public issues:

- a credential, token or private file committed by mistake;
- corpus text or personal data that should not be in the repository (several corpora are user-generated social-media text without a redistribution licence).

`scripts/verify_repository.py --check` scans every text file for common credential patterns and restricted artefacts; CI runs it on every push.
