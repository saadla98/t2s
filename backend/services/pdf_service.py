"""PDF Report Generation Service."""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# Brand colors
PRIMARY = HexColor("#0EA5E9")
DARK_BG = HexColor("#0F172A")
CARD_BG = HexColor("#1E293B")
SUCCESS = HexColor("#10B981")
WARNING = HexColor("#F59E0B")
DANGER = HexColor("#EF4444")
TEXT_LIGHT = HexColor("#E2E8F0")
TEXT_MUTED = HexColor("#94A3B8")


def _get_risk_color(risk_level: str):
    if risk_level == "Low":
        return SUCCESS
    elif risk_level == "Medium":
        return WARNING
    return DANGER


def generate_prediction_report(prediction_data: dict) -> bytes:
    """Generate a PDF report for a risk prediction."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=22, textColor=PRIMARY, spaceAfter=6 * mm,
        fontName="Helvetica-Bold"
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle", parent=styles["Heading2"],
        fontSize=14, textColor=HexColor("#334155"), spaceAfter=4 * mm,
        fontName="Helvetica-Bold"
    )
    body_style = ParagraphStyle(
        "CustomBody", parent=styles["Normal"],
        fontSize=10, textColor=HexColor("#475569"), leading=14
    )
    header_style = ParagraphStyle(
        "Header", parent=styles["Normal"],
        fontSize=8, textColor=TEXT_MUTED, alignment=TA_RIGHT
    )

    elements = []

    # ── Header ──
    header_text = f"T2S Predictive Maintenance Platform — Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
    elements.append(Paragraph(header_text, header_style))
    elements.append(Spacer(1, 8 * mm))

    # ── Title ──
    elements.append(Paragraph("Rapport d'Analyse de Risque", title_style))
    elements.append(Paragraph("Scanner CT — Estimation du Risque de Panne", subtitle_style))
    elements.append(Spacer(1, 6 * mm))

    # ── Scanner Info ──
    elements.append(Paragraph("Informations du Scanner", subtitle_style))

    scanner_data = prediction_data.get("scanner_data", {})
    
    def _safe_float(val, default=0.0):
        try:
            if val is None or val == "":
                return default
            return float(val)
        except (ValueError, TypeError):
            return default
            
    info_data = [
        ["Paramètre", "Valeur"],
        ["ID Scanner", str(scanner_data.get("Device_ID", prediction_data.get("device_id", "N/A")))],
        ["Âge (années)", str(scanner_data.get("Age", "N/A"))],
        ["Coût Maintenance (€)", f"{_safe_float(scanner_data.get('Maintenance_Cost')):,.2f}"],
        ["Temps d'arrêt (jours)", f"{_safe_float(scanner_data.get('Downtime')):.2f}"],
        ["Fréquence Maintenance", str(scanner_data.get("Maintenance_Frequency", "N/A"))],
        ["Nb. Événements de Panne", str(scanner_data.get("Failure_Event_Count", "N/A"))],
        ["MTBF", f"{_safe_float(scanner_data.get('MTBF')):.2f}"],
        ["Taux de Panne", f"{_safe_float(scanner_data.get('Failure_Rate')):.4f}"],
        ["Module Affecté", str(scanner_data.get("Affected_Module", "N/A"))],
    ]

    info_table = Table(info_data, colWidths=[60 * mm, 100 * mm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8 * mm))

    # ── Risk Result ──
    risk_level = prediction_data.get("predicted_risk", "N/A")
    health_score = prediction_data.get("health_score", 0)
    risk_color = _get_risk_color(risk_level)

    elements.append(Paragraph("Résultat de l'Analyse", subtitle_style))

    risk_label = {"Low": "Faible", "Medium": "Modéré", "High": "Élevé"}.get(risk_level, risk_level)

    result_data = [
        ["Indicateur", "Valeur"],
        ["Niveau de Risque", risk_label],
        ["Score de Santé", f"{health_score}/100"],
    ]

    proba = prediction_data.get("risk_probabilities", {})
    if proba:
        result_data.append(["Probabilité — Faible", f"{_safe_float(proba.get('Low')):.1f}%"])
        result_data.append(["Probabilité — Modéré", f"{_safe_float(proba.get('Medium')):.1f}%"])
        result_data.append(["Probabilité — Élevé", f"{_safe_float(proba.get('High')):.1f}%"])

    result_table = Table(result_data, colWidths=[60 * mm, 100 * mm])
    result_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(result_table)
    elements.append(Spacer(1, 8 * mm))

    # ── Recommendation ──
    elements.append(Paragraph("Recommandation", subtitle_style))
    recommendation = prediction_data.get("recommendation", {})
    if isinstance(recommendation, dict):
        rec_text = recommendation.get("message", "Aucune recommandation disponible.")
        rec_actions = recommendation.get("actions", [])
        rec_urgency = recommendation.get("urgency", "")
    else:
        rec_text = str(recommendation)
        rec_actions = []
        rec_urgency = ""

    elements.append(Paragraph(f"<b>Diagnostic :</b> {rec_text}", body_style))
    elements.append(Spacer(1, 3 * mm))

    if rec_actions:
        elements.append(Paragraph("<b>Actions recommandées :</b>", body_style))
        for action in rec_actions:
            elements.append(Paragraph(f"  • {action}", body_style))
        elements.append(Spacer(1, 3 * mm))

    if rec_urgency:
        elements.append(Paragraph(f"<b>Urgence :</b> {rec_urgency}", body_style))
    elements.append(Spacer(1, 8 * mm))

    # ── Technician Info ──
    tech_name = prediction_data.get("technician_name")
    tech_role = prediction_data.get("technician_role")
    if tech_name or tech_role:
        elements.append(Paragraph("Informations du Technicien", subtitle_style))
        if tech_name:
            elements.append(Paragraph(f"<b>Nom :</b> {tech_name}", body_style))
        if tech_role:
            role_label = {"technician": "Technicien", "manager": "Responsable Maintenance"}.get(tech_role, tech_role)
            elements.append(Paragraph(f"<b>Rôle :</b> {role_label}", body_style))
        notes = prediction_data.get("notes")
        if notes:
            elements.append(Paragraph(f"<b>Notes :</b> {notes}", body_style))
        elements.append(Spacer(1, 8 * mm))

    # ── Footer ──
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontSize=7, textColor=TEXT_MUTED, alignment=TA_CENTER
    )
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph("─" * 80, footer_style))
    elements.append(Paragraph(
        "T2S Predictive Maintenance Platform • Système d'aide à la décision pour scanners CT",
        footer_style
    ))
    elements.append(Paragraph(
        "Ce rapport est généré automatiquement. Les recommandations sont basées sur l'analyse IA et ne remplacent pas le jugement expert.",
        footer_style
    ))

    doc.build(elements)
    return buffer.getvalue()
