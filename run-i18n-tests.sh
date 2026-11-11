# SPDX-FileCopyrightText: 2022-2023 Graz University of Technology.
# SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
# SPDX-License-Identifier: MIT

# Usage:
#   ./run-i18n-tests.sh

pybabel extract -F pyproject.toml invenio_saml --output-file /dev/null
