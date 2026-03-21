"""
Config-driven rules for email business filtering.
Inspectable and maintainable: domain lists and keyword patterns.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Category precedence (first match wins for primary_category)
# ---------------------------------------------------------------------------
CATEGORY_PRECEDENCE = [
    "bounce_ndr",
    "spam_suspect",
    "social_notification",
    "newsletter",
    "logistics",
    "marketplace",
    "institution",
    "internal",
    "supplier",
    "customer",
    "business_core",
    "unknown",
]

# ---------------------------------------------------------------------------
# Sender / from patterns (substring match, lowercased)
# ---------------------------------------------------------------------------

# Bounce / NDR: mailer-daemon, postmaster, delivery failed, undelivered, etc.
BOUNCE_SENDER_PATTERNS = [
    "mailer-daemon",
    "mail delivery subsystem",
    "postmaster@",
    "postmaster ",
    "mail delivery failed",
    "delivery status notification",
    "returned mail",
    "undeliverable",
    "failure delivery",
    "delivery failure",
]

BOUNCE_SUBJECT_PATTERNS = [
    "delivery status",
    "undeliverable",
    "mail delivery failed",
    "returned to sender",
    "returning message to sender",
    "delivery failure",
    "failure notice",
    "notificación de estado de entrega",
    "mensaje no entregado",
]

BOUNCE_BODY_PATTERNS = [
    "returning message to sender",
    "notificación de estado de entrega",
    "delivery has failed",
    "could not be delivered",
]

# Social platforms
SOCIAL_DOMAINS = [
    "facebookmail.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "instagram.com",
    "tiktok.com",
    "pinterest.com",
    "youtube.com",
    "snapchat.com",
    "whatsapp.com",
    "messenger.com",
    "mail.instagram.com",
    "notifications.linkedin.com",
]

SOCIAL_SUBJECT_PATTERNS = [
    "facebook",
    "linkedin",
    "twitter",
    "instagram",
    "has sent you a connection",
    "wants to connect",
    "new follower",
    "mentioned you",
]

# Newsletter / marketing
NEWSLETTER_SENDER_PATTERNS = [
    "newsletter@",
    "noreply@",
    "no-reply@",
    "mailer@",
    "marketing@",
    "promo@",
    "offers@",
    "unsubscribe",
]

NEWSLETTER_SUBJECT_PATTERNS = [
    "unsubscribe",
    "newsletter",
    "suscripción",
    "promo",
    "offer",
    "ofertas",
    "descuento",
    "black friday",
    "cyber monday",
]

# Spam suspects (subject/body hints)
SPAM_SUBJECT_PATTERNS = [
    "viagra",
    "casino",
    "lottery",
    "winner",
    "inheritance",
    "nigeria",
    "prince ",
    "adult ",
    "porn",
    "crypto investment",
    "bitcoin investment",
    "urgent action required",
    "account suspended",
    "verify your account",
]

# Logistics / couriers
LOGISTICS_DOMAINS = [
    "dhl.com",
    "dhl.de",
    "fedex.com",
    "ups.com",
    "correos.cl",
    "chilexpress.cl",
    "blueexpress.cl",
    "starken.cl",
    "correoschile.cl",
    "cargo.com",
    "tracking.",
]

LOGISTICS_SUBJECT_PATTERNS = [
    "shipment",
    "tracking",
    "envío",
    "delivery",
    "entrega",
    "paquete",
    "package",
    "seguimiento",
]

# Marketplace / tenders
MARKETPLACE_DOMAINS = [
    "mercadopublico.cl",
    "wherex.com",
    "wherex.cl",
    "chilecompra.cl",
    "mercadopublico.cl",
]

MARKETPLACE_SUBJECT_PATTERNS = [
    "licitación",
    "licitacion",
    "tender",
    "mercado público",
    "mercadopublico",
]

# Institutions (universities, etc.)
INSTITUTION_DOMAINS = [
    "uach.cl",
    "udec.cl",
    "uc.cl",
    "uchile.cl",
    "usach.cl",
    "utfsm.cl",
    "unab.cl",
    "ucn.cl",
    "puc.cl",
    "ucv.cl",
    "ufro.cl",
    "usm.cl",
    "umayor.cl",
    "uandes.cl",
    "med.puc.cl",
    "edu.cl",
    ".edu.",
    ".edu",
]

INSTITUTION_BODY_PATTERNS = [
    "universidad",
    "facultad",
    "departamento",
    "investigación",
]

# Internal (company's own domains)
INTERNAL_DOMAINS = [
    "labdelivery.cl",
    "origenlab.cl",
    "origenlab.com",
]

# Supplier/customer: optional allowlists (extend per client)
SUPPLIER_DOMAINS: list[str] = []
CUSTOMER_DOMAINS: list[str] = []

# Second-level commercial subtype (when primary is business_core)
COMMERCIAL_SUBTYPE_PATTERNS = {
    "quote": ["cotiz", "cotización", "quote", "presupuesto"],
    "order": ["pedido", "orden de compra", "purchase order", " oc ", "orden"],
    "invoice": ["factura", "invoice", "boleta"],
    "support": ["soporte", "support", "reclamo", "garantía", "garantia"],
    "followup": ["seguimiento", "follow-up", "follow up", "recordatorio"],
}

# Business-core keywords (subject + body) for generic commercial
BUSINESS_CORE_PATTERNS = [
    "cotiz",
    "cotización",
    "quote",
    "proveedor",
    "factura",
    "invoice",
    "pedido",
    "orden de compra",
    "purchase order",
    " oc ",
    "adjunto",
    "plazo",
    "stock",
    "entrega",
    "envío",
    "incoterm",
]
