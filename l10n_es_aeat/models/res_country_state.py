# Copyright 2023 Moduon - Eduardo de Miguel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .aeat_data import AEAT_STATES_CODE_MAP


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    aeat_state_code = fields.Char(
        compute="_compute_state_code",
        store=True,
        compute_sudo=True,
    )

    @api.depends("code")
    def _compute_state_code(self):
        for record in self:
            record.aeat_state_code = AEAT_STATES_CODE_MAP.get(record.code, False)
