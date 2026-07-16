..
    SPDX-FileCopyrightText: 2021 CERN.
    SPDX-FileCopyrightText: 2019-2024 Esteban J. Garcia Gabancho.
    SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
    SPDX-FileCopyrightText: 2025 KTH Royal Institute of Technology.
    SPDX-FileCopyrightText: 2026 TU Wien.
    SPDX-License-Identifier: MIT

Changes
=======

Version v5.0.1 (released 2026-07-16)

- chore(setup): migrate from setuptools to hatchling

Version v5.0.0 (released 2026-06-16)

- chore(setup): bump dependencies
- chore(git-blame): ignore the SPDX license header commit
- chore(licenses): update license headers to use SPDX

Version v4.0.0 (released 2026-05-28)

- chore(setup): bump dependencies

Version v3.0.0 (released 2026-04-17)

- fix: use TRUSTED_HOSTS
    BREAKING CHANGE: flask>=3.1.0 introduced a new configuration variable
    ``TRUSTS_HOSTS`` and Invenio-App has already deprecated ``APP_ALLOWED_HOSTS``
    usage since.

Version v2.0.0 (released 2026-02-10)

- tests: remove pinned packages from deps
- chore(setup): bump dependencies

Version v1.2.1 (released 2025-10-22)

- i18n: pulled translations

Version v1.2.0 (released 2025-07-17)

- i18n: pulled translations
- changes: spacing typo

Version 1.1.0 (release 2025-05-08)

- updates version requirements to support newer invenio module versions
- handlers: allow user lookup customizing in factory
- profile: add affiliations profile value
- adds test version restrictions to minimize xmlsec issues

Version 1.0.1 (release 2024-11-30)

- setup: change to reusable workflows
- setup: pin dependencies
- docs: explicitly add python requirements

Version 1.0.0 (released 2024-04-10)

- Initial stable release.

Version 1.0.0a4 (released 2022-12-15)

- Migrate Flask-SSO-SAML code #31
- Check before linking user #35
- Add translations tests #36

Version 1.0.0a2 (released 2022-09-12)

- Add auto_confirm, confirm user email address

Version 1.0.0a1 (released 2021-07-15)

- Marking strings for translation
- Adds german translation

Version 1.0.0a0 (released 2021-05-27)

- Module refactoring.

Version 0.1.0 (released TBD)

- Initial public release.
