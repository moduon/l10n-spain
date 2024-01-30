# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class L10nEsAeatMod180Report(models.Model):
    _description = "AEAT 180 report"
    _inherit = "l10n.es.aeat.report.tax.mapping"
    _name = "l10n.es.aeat.mod180.report"
    _aeat_number = "180"
    _period_yearly = True
    _period_quarterly = False
    _period_monthly = False

    casilla_01 = fields.Integer(
        string="[01] # Recipients",
        readonly=True,
        compute="_compute_casilla_01",
        help="Number of recipients",
    )
    casilla_02 = fields.Float(
        string="[02] Base retenciones e ingresos a cuenta",
        readonly=True,
        compute="_compute_casilla_02",
        store=True,
    )
    casilla_03 = fields.Float(
        string="[03] Retenciones e ingresos a cuenta",
        readonly=True,
        compute="_compute_casilla_03",
        help="Amount of retentions",
        store=True,
    )
    signo = fields.Selection(
        selection=[(" ", "Positivo"), ("N", "Negativo")],
        string="Signo Casilla 03",
        compute="_compute_casilla_03",
        store=True,
    )
    casilla_04 = fields.Float(
        string="[04] Fees to compensate",
        readonly=True,
        states={"calculated": [("readonly", False)]},
        help="Fee to compensate for prior results with same subject, "
        "fiscal year and period (in which his statement was to return "
        "and compensation back option was chosen).",
        store=True,
    )
    casilla_05 = fields.Float(
        string="[05] Result",
        readonly=True,
        compute="_compute_casilla_05",
        help="Result: ([03] - [04])",
        store=True,
    )
    tipo_declaracion = fields.Selection(
        selection=[
            ("I", "To enter"),
            ("U", "Direct debit"),
            ("G", "To enter on CCT"),
            ("N", "To return"),
        ],
        string="Result type",
        default="N",
        readonly=True,
        states={"draft": [("readonly", False)]},
        required=True,
    )
    tipo_declaracion_positiva = fields.Selection(
        selection=[("I", "To enter"), ("U", "Direct debit"), ("G", "To enter on CCT")],
        string="Result type (positive)",
        compute="_compute_tipo_declaracion",
        inverse="_inverse_tipo_declaracion",
        store=True,
    )
    tipo_declaracion_negativa = fields.Selection(
        selection=[("N", "To return")],
        string="Result type (negative)",
        compute="_compute_tipo_declaracion",
        inverse="_inverse_tipo_declaracion",
        store=True,
    )
    recipient_ids = fields.One2many(
        "l10n.es.aeat.mod180.report.recipient", "report_id", readonly=True
    )
    error_nif_recipient = fields.Boolean(
        string="Errors",
        compute="_compute_error_nif_recipient",
        store=True,
    )
    # move_line_ids = fields.Many2many(
    #     "account.move.line", compute="_compute_move_line_ids"
    # )
    # real_state_ids = fields.Many2many(
    #     "l10n.es.aeat.real_estate", compute="_compute_real_state_ids"
    # )

    # def default_get(self, field_list):
    #     res = super().default_get(field_list)
    #     if res.get("company_id", False):
    #         bank_ids = (
    #             self.env["res.company"]
    #             .browse(res.get("company_id"))
    #             .partner_id.bank_ids
    #         )
    #         if bank_ids:
    #             res.update({"partner_bank_id": bank_ids[0].id})
    #     return res

    @api.depends("tipo_declaracion")
    def _compute_tipo_declaracion(self):
        for rec in self:
            if rec.tipo_declaracion == "N":
                rec.tipo_declaracion_negativa = rec.tipo_declaracion
                rec.tipo_declaracion_positiva = False
            else:
                rec.tipo_declaracion_positiva = rec.tipo_declaracion
                rec.tipo_declaracion_negativa = False

    def _inverse_tipo_declaracion(self):
        for rec in self:
            if rec.casilla_05 > 0.0:
                rec.tipo_declaracion = rec.tipo_declaracion_positiva
            else:
                rec.tipo_declaracion = rec.tipo_declaracion_negativa

    @api.constrains("tipo_declaracion")
    def _check_tipo_declaracion(self):
        for rec in self:
            if rec.casilla_05 <= 0.0 and rec.tipo_declaracion != "N":
                raise ValidationError(
                    _(
                        "The result of the declaration is negative. "
                        "You should select another Result type"
                    )
                )
            elif rec.casilla_05 > 0.0 and rec.tipo_declaracion == "N":
                raise ValidationError(
                    _(
                        "The result of the declaration is positive. "
                        "You should select another Result type"
                    )
                )

    @api.depends("recipient_ids")
    def _compute_casilla_01(self):
        # casillas = (2, 3)
        for report in self:
            # tax_lines = report.tax_line_ids.filtered(
            #     lambda x: x.field_number in casillas
            # )
            report.casilla_01 = len(report.recipient_ids)

    @api.depends("tax_line_ids", "tax_line_ids.amount")
    def _compute_casilla_02(self):
        for report in self:
            tax_lines = report.tax_line_ids.filtered(lambda x: x.field_number == 2)
            report.casilla_02 = sum(tax_lines.mapped("amount"))

    @api.depends("tax_line_ids", "tax_line_ids.amount")
    def _compute_casilla_03(self):
        for report in self:
            tax_lines = report.tax_line_ids.filtered(lambda x: x.field_number == 3)
            report.casilla_03 = sum(tax_lines.mapped("amount"))
            if report.casilla_03 < 0:
                report.signo = "N"
            else:
                report.signo = " "

    @api.depends("casilla_03", "casilla_04")
    def _compute_casilla_05(self):
        for report in self:
            report.casilla_05 = report.casilla_03 - report.casilla_04

    @api.depends("recipient_ids")
    def _compute_error_nif_recipient(self):
        for report in self:
            report.error_nif_recipient = report.recipient_ids and any(
                report.recipient_ids.mapped("error_nif")
            )

    # @api.depends("tax_line_ids", "tax_line_ids.move_line_ids")
    # def _compute_move_line_ids(self):
    #     for report in self:
    #         report.move_line_ids = report.tax_line_ids.filtered(
    #             lambda x: x.field_number == 2
    #         ).mapped("move_line_ids")

    # @api.depends("move_line_ids")
    # def _compute_real_state_ids(self):
    #     for report in self:
    #         report.real_state_ids = report.move_line_ids.mapped(
    #             "l10n_es_aeat_real_estate_id"
    #         )

    def button_confirm(self):
        """Check bank account completion."""
        msg = ""
        for report in self.filtered(lambda x: not x.partner_bank_id):
            if report.tipo_declaracion in ("U", "N"):
                msg = (
                    _("Select an account for making the charge")
                    if report.tipo_declaracion == "U"
                    else _("Select an account for receiving the money")
                )
            if msg:
                raise UserError(msg)
        return super().button_confirm()

    def calculate(self):
        res = super().calculate()
        for rec in self:
            if rec.casilla_05 <= 0.0:
                rec.tipo_declaracion = "N"
            else:
                rec.tipo_declaracion = "I"
            recipients = self.env["l10n.es.aeat.mod180.report.recipient"]
            for line in rec.tax_line_ids.filtered(lambda x: x.field_number == 2).mapped(
                "move_line_ids"
            ):
                # TODO: Si en un futuro la renta fuera en especie habrá que distinguir
                # la modadlidad para que en ese caso la modalidad lleve un 2
                recipients |= self.env["l10n.es.aeat.mod180.report.recipient"].create(
                    {
                        "report_id": rec.id,
                        "move_line_id": line.id,
                        "modalidad": "1",
                    }
                )
            if recipients:
                rec.recipient_ids = [(6, 0, recipients.ids)]
        return res


class L10nEsAeatMod180ReportRecipient(models.Model):
    _name = "l10n.es.aeat.mod180.report.recipient"
    _description = "AEAT 180 report recipient"

    report_id = fields.Many2one("l10n.es.aeat.mod180.report", string="Report")
    move_line_id = fields.Many2one("account.move.line", string="Journal item")
    real_state_id = fields.Many2one(
        "l10n.es.aeat.real_estate", compute="_compute_real_state_id"
    )
    modalidad = fields.Selection(
        selection=[
            ("1", "Si la renta o rendimiento satisfecho es de tipo dinerario."),
            ("2", "Si la renta o rendimiento satisfecho es en especie."),
        ],
        default="1",
    )
    signo = fields.Selection(
        selection=[(" ", "Positivo"), ("N", "Negativo")],
        string="Signo Base Retenciones",
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    base_retenciones = fields.Float(
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    porcentaje_retencion = fields.Float(
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    cuota_retencion = fields.Float(
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    error_nif = fields.Boolean(
        compute="_compute_error_nif",
        store=True,
    )

    @api.depends("move_line_id")
    def _compute_real_state_id(self):
        for rec in self:
            rec.real_state_id = rec.move_line_id.l10n_es_aeat_real_estate_id

    @api.depends("move_line_id")
    def _compute_amount(self):
        for rec in self:
            rec.base_retenciones = rec.move_line_id.debit - rec.move_line_id.credit
            if rec.base_retenciones < 0:
                rec.signo = "N"
            else:
                rec.signo = " "
            rec.porcentaje_retencion = sum(
                rec.move_line_id.tax_ids.mapped("real_amount")
            )
            rec.cuota_retencion = (
                rec.move_line_id.price_total - rec.move_line_id.price_subtotal
            )

    @api.depends("move_line_id.partner_id")
    def _compute_error_nif(self):
        for rec in self:
            rec.error_nif = not bool(rec.move_line_id.partner_id.vat)
