# Legacy mail migration notes (LabDelivery / old Outlook)

**Scope:** This document is about a **separate** legacy email/Outlook situation. It is **not** part of the current OrigenLab website or the Titan email setup for contacto@origenlab.cl.

---

## Context

- **Old context:** LabDelivery / labdelivery.cl and related business email.
- **Risk:** Important historical sent emails and quote information may exist only on old machines or in old Outlook profiles.
- **Observed:** On a newer machine, Outlook showed Inbox but not historical Sent mail for the old setup. This points to local storage (e.g. PST, POP-style, or old Outlook profile data) rather than a centralised mailbox that syncs.

---

## Preservation-first strategy

Do **not** change or retire old accounts or machines until backups are done.

1. **Export full Outlook mailbox to PST** on each old machine that holds relevant mail.
2. **Copy original Outlook data files** from each machine (paths and method depend on Outlook version; document per machine).
3. **Store backups** in organised folders and **duplicate** them to at least one other safe location.
4. **Only after backups are verified**, consider migration, cleanup, or decommissioning.

---

## Checklist (before touching old accounts)

- [ ] Identify every machine that has/had the old LabDelivery (or related) mail.
- [ ] On each machine: export full Outlook mailbox to PST; note where the PST is saved.
- [ ] On each machine: copy Outlook data files (e.g. PST/OST location) to a documented path.
- [ ] Organise backups in named folders (e.g. by machine and date).
- [ ] Duplicate the full backup set to at least one other safe location.
- [ ] Verify that backups open (e.g. open PST in Outlook or a viewer) before any migration or cleanup.

---

## Relationship to OrigenLab

- **OrigenLab:** New static site and Titan-based contacto@origenlab.cl. Documented in `email-setup.md` and `deployment-status.md`.
- **Legacy:** Old LabDelivery/Outlook history and any future migration are a **separate project**. Do not mix credentials, DNS, or procedures for OrigenLab with the legacy migration work.
