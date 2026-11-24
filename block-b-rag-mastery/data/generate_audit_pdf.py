"""
Generates a realistic multi-page PDF: Enterprise Security & Auditing Standard
Used as the knowledge ground truth for Block B RAG practice.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak


def generate_audit_standard_pdf(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        spaceAfter=14,
        textColor='#1A365D'
    )
    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
        textColor='#2B6CB0'
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )

    story = []

    # ── Page 1: Governance & Access Control Policy ───────────────────────────
    story.append(Paragraph("GLOBAL CLOUD AUDIT STANDARD: SOC-2 & ISO-27001 COMPLIANCE", title_style))
    story.append(Paragraph("Standard Identifier: AUD-STD-2026-V4 | Classification: Enterprise Confidential", body_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Section 1: Scope and Governance Framework", section_style))
    story.append(Paragraph(
        "This standard governs all production cloud environments, software repositories, and customer data stores. "
        "All engineering personnel, contractors, and third-party vendors must comply with the mandatory controls defined herein. "
        "The Chief Information Security Officer (CISO) and the Internal Audit Committee conduct formal bi-annual compliance reviews.",
        body_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Section 2: Identity, Authentication & Access Control (AC-1 to AC-4)", section_style))
    story.append(Paragraph(
        "2.1 Multi-Factor Authentication (MFA): FIDO2/WebAuthn hardware security keys or approved authenticator apps "
        "are strictly mandatory for all employees accessing corporate networks, code repositories, and production bastions. "
        "SMS-based MFA is strictly prohibited due to SIM-swapping vulnerabilities.",
        body_style
    ))
    story.append(Paragraph(
        "2.2 Principle of Least Privilege: Access permissions must be provisioned strictly on a Need-to-Know basis using "
        "Role-Based Access Control (RBAC). Standing administrative credentials in production are forbidden; all elevated "
        "privileges must utilize Just-In-Time (JIT) access with a maximum time-to-live (TTL) of 4 hours.",
        body_style
    ))
    story.append(Paragraph(
        "2.3 Access Review Cadence: Department leads must perform quarterly entitlement audits (every 90 calendar days). "
        "Accounts of separated employees must be permanently deprovisioned within 60 minutes of HR termination notice.",
        body_style
    ))
    story.append(PageBreak())

    # ── Page 2: Cryptographic Standards & Data Protection ────────────────────
    story.append(Paragraph("Section 3: Cryptographic Controls and Data Encryption (CR-1 to CR-3)", section_style))
    story.append(Paragraph(
        "3.1 Encryption at Rest: All production databases, object storage buckets (S3/GCS), and persistent disk volumes "
        "must be encrypted at rest using AES-256 (Advanced Encryption Standard with 256-bit keys) or ChaCha20-Poly1305. "
        "Unencrypted persistent volumes are subject to automated quarantine within 5 minutes of detection.",
        body_style
    ))
    story.append(Paragraph(
        "3.2 Encryption in Transit: All data transmitted over public networks and between internal service meshes must be "
        "enforced via TLS 1.3 (Transport Layer Security). Legacy protocols including TLS 1.0, TLS 1.1, and SSL v3 are "
        "disabled at the edge load balancers.",
        body_style
    ))
    story.append(Paragraph(
        "3.3 Cryptographic Key Management: Master encryption keys (KMS) must be stored in FIPS 140-3 Level 3 certified "
        "Hardware Security Modules (HSMs). Automated key rotation must be configured to cycle master keys every 90 days. "
        "Exporting raw cryptographic private keys from the HSM is architecturally prevented.",
        body_style
    ))
    story.append(PageBreak())

    # ── Page 3: Incident Management & Escalation Timelines ────────────────────
    story.append(Paragraph("Section 4: Incident Response & Notification Timelines (IR-1 to IR-5)", section_style))
    story.append(Paragraph(
        "4.1 Severity Classification: Incidents are categorized into P1 (Critical - confirmed data exfiltration or total outage), "
        "P2 (High - degraded security controls without known data loss), and P3 (Medium - non-critical anomalies).",
        body_style
    ))
    story.append(Paragraph(
        "4.2 Internal Escalation Thresholds: Upon confirmation of a P1 Critical Incident, the Security Operations Center (SOC) "
        "must declare a Sev-1 war room and notify the Incident Commander and CISO within exactly 15 minutes.",
        body_style
    ))
    story.append(Paragraph(
        "4.3 External Regulatory & Customer Notification: In the event of confirmed unauthorized access to Personal Identifiable "
        "Information (PII) or confidential client data, the enterprise legal counsel must formally notify regulatory authorities "
        "(e.g., EU Data Protection Authorities under GDPR) and affected enterprise customers within no more than 72 hours of verification.",
        body_style
    ))
    story.append(Paragraph(
        "4.4 Post-Incident Review (PIR): A Blameless Post-Mortem and root-cause analysis (RCA) document must be published and "
        "circulated to executive leadership within 5 business days following complete containment.",
        body_style
    ))
    story.append(PageBreak())

    # ── Page 4: Audit Logging, Retention & Continuous Monitoring ─────────────
    story.append(Paragraph("Section 5: Audit Logging and Telemetry Retention (AU-1 to AU-4)", section_style))
    story.append(Paragraph(
        "5.1 Immutable Audit Trails: All user access logs, privileged command invocations, API gateway telemetry, and authentication "
        "attempts must be written to write-once-read-many (WORM) append-only storage buckets.",
        body_style
    ))
    story.append(Paragraph(
        "5.2 Minimum Retention Period: Audit logs and compliance telemetry must be retained online in high-availability storage "
        "for a minimum of 90 days, and archived in cold immutable storage for a minimum total retention of 365 calendar days (1 full year). "
        "Financial transaction audit logs must be preserved for 7 years.",
        body_style
    ))
    story.append(Paragraph(
        "5.3 Continuous Vulnerability Scanning: Production containers and VM images must be scanned for Common Vulnerabilities "
        "and Exposures (CVEs) every 24 hours. Critical CVEs with CVSS score >= 9.0 must be patched and deployed within 48 hours.",
        body_style
    ))
    story.append(Paragraph(
        "5.4 Third-Party Vendor Audits: All SaaS vendors processing Tier-1 data must supply valid SOC 2 Type II reports and ISO 27001 "
        "certifications annually. Failure to provide certifications initiates vendor termination procedures.",
        body_style
    ))

    doc.build(story)
    print(f"--> Successfully generated Audit Standard PDF at: {output_path}")


if __name__ == "__main__":
    out = Path(__file__).parent / "iso27001_soc2_audit_standard.pdf"
    generate_audit_standard_pdf(out)
