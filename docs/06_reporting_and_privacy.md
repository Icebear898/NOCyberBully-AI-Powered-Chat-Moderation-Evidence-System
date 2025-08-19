# Reporting & Privacy

## Reporting
- Dashboard `/dashboard` lists incidents
- Download report `/report?offender=&victim=` generates a zip:
  - `incidents.csv` with structured details
  - `/screenshots/*.png` captured at the time of abuse

## Privacy Principles (MVP)
- Data stored locally in SQLite and `evidence/`
- No external sharing or tracking
- Configurable sensitivity reduces over-collection

## Future Enhancements
- Encryption at rest for evidence and DB
- Role-based access control (RBAC) for dashboard
- Data retention policies and secure deletion
- Redaction of PII in reports
