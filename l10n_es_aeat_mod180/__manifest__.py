# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "AEAT modelo 180",
    "summary": "TODO: Fill later",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Localization",
    "website": "https://github.com/OCA/l10n-spain",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "l10n_es_aeat",
    ],
    "data": [
        "data/aeat_export_mod180_sub01_data.xml",
        "data/aeat_export_mod180_main_data.xml",
        "data/tax_code_map_mod180_data.xml",
        "security/ir.model.access.csv",
        "security/l10n_es_aeat_mod180_security.xml",
        "views/l10n_es_aeat_mod180_report.xml",
    ],
}
