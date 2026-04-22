"""
create_sample_policy.py — Generate a sample company policy PDF for demo purposes.

Creates a comprehensive policy document without requiring external dependencies
beyond what's in requirements.txt.
"""

import os


def create_sample_policy_text() -> str:
    """Return sample company policy text."""
    return """
ACME CORPORATION — CUSTOMER SUPPORT POLICIES
Version 3.2 | Effective Date: January 1, 2024
============================================

SECTION 1: REFUND POLICY
------------------------

1.1 General Refund Terms
Customers may request a full refund within 30 days of purchase for any software product.
Hardware products are eligible for refund within 14 days of delivery, provided the item
is returned in its original packaging and unused condition.

1.2 Refund Processing
- Refund requests must be submitted through the support portal or by contacting customer support.
- Refunds are processed within 5-7 business days after approval.
- Original payment method will be credited. If original payment method is unavailable,
  a store credit will be issued.

1.3 Non-Refundable Items
- Subscription fees for consumed billing periods
- Custom or personalized products
- Products marked as "Final Sale"
- Setup or installation service fees

1.4 Partial Refunds
If a product has been used for more than 14 days but less than 30 days, a partial refund
of 50% may be offered at management discretion for software products only.


SECTION 2: WARRANTY POLICY
--------------------------

2.1 Hardware Warranty
All hardware products come with a standard 12-month manufacturer warranty covering
defects in materials and workmanship.

2.2 Extended Warranty
Premium and Business plan customers receive an automatic 24-month extended warranty
on all hardware purchases at no additional cost.

2.3 Warranty Exclusions
- Damage caused by misuse, accidents, or unauthorized modifications
- Normal wear and tear
- Water damage (unless product is rated water-resistant)
- Cosmetic damage that does not affect functionality


SECTION 3: SUPPORT TIERS
-------------------------

3.1 Basic Plan Support
- Email support only
- Response time: within 48 business hours
- Access to knowledge base and FAQ
- Community forum access

3.2 Business Plan Support
- Email and live chat support
- Response time: within 24 business hours
- Priority queue for ticket resolution
- Dedicated onboarding session

3.3 Premium Plan Support
- Email, live chat, and phone support
- Response time: within 4 business hours
- Dedicated account manager
- 24/7 emergency support line
- Quarterly business reviews
- Custom integration assistance


SECTION 4: ESCALATION POLICY
-----------------------------

4.1 Escalation Levels
- Level 1: Front-line support agent (standard issues)
- Level 2: Senior support specialist (complex technical issues)
- Level 3: Engineering team (product bugs, system outages)
- Level 4: Management (policy exceptions, major incidents)

4.2 Automatic Escalation Triggers
- Ticket unresolved for more than 72 hours → escalate to Level 2
- Critical priority ticket → immediate Level 2 assignment
- Customer satisfaction score below 3/5 → management notification
- Repeat issue (3+ tickets on same topic) → Level 2 with pattern review


SECTION 5: DATA PRIVACY POLICY
-------------------------------

5.1 Data Collection
We collect only the minimum data necessary to provide our services:
- Name, email, phone number for account management
- Payment information (processed by PCI-compliant third-party processors)
- Usage data for service improvement
- Support interaction history

5.2 Data Retention
- Active account data: retained for the duration of the account plus 12 months
- Support tickets: retained for 36 months after resolution
- Payment records: retained for 7 years per regulatory requirements
- Usage analytics: anonymized after 24 months

5.3 Data Rights
Customers have the right to:
- Request a copy of their personal data
- Request deletion of their personal data (subject to legal retention requirements)
- Opt out of marketing communications
- Update or correct their personal information

5.4 Data Security
- All data encrypted at rest (AES-256) and in transit (TLS 1.3)
- Multi-factor authentication available for all accounts
- Annual third-party security audits
- SOC 2 Type II certified


SECTION 6: SERVICE LEVEL AGREEMENTS (SLA)
-----------------------------------------

6.1 Uptime Guarantees
- Basic Plan: 99.5% uptime
- Business Plan: 99.9% uptime
- Premium Plan: 99.99% uptime

6.2 SLA Credits
If uptime falls below the guaranteed level in any calendar month:
- 99.0% - 99.5%: 10% service credit
- 98.0% - 99.0%: 25% service credit
- Below 98.0%: 50% service credit

6.3 Scheduled Maintenance
- Maintenance windows: Sundays 2:00 AM - 6:00 AM UTC
- 72-hour advance notice for planned maintenance
- Emergency maintenance exempt from SLA calculations


SECTION 7: ACCEPTABLE USE POLICY
---------------------------------

7.1 Prohibited Activities
Users may not:
- Share account credentials with unauthorized parties
- Use the service for illegal activities
- Attempt to reverse-engineer or decompile our software
- Store content that violates intellectual property rights
- Use automated tools to scrape or overload our systems

7.2 Account Suspension
We reserve the right to suspend accounts that violate our acceptable use
policy. Suspended accounts will receive:
- Email notification with reason for suspension
- 7-day grace period for first offense
- Immediate suspension for severe violations

---
Document ID: POL-2024-001
Last Updated: January 1, 2024
Approved by: Chief Operations Officer
Next Review Date: July 1, 2024
"""


def create_policy_pdf():
    """Create a simple text-based policy file.

    We save as .txt first and then note that for a real demo,
    you'd want to use reportlab or similar to create a proper PDF.
    For this demo, we create a PDF-like text file that PyPDFLoader can handle.
    """
    policies_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "policies")
    os.makedirs(policies_dir, exist_ok=True)

    # Create a simple PDF using minimal PDF spec
    policy_text = create_sample_policy_text()
    filepath = os.path.join(policies_dir, "acme_company_policies.pdf")

    # Build a minimal valid PDF
    lines = policy_text.strip().split('\n')
    # We'll create a single-page PDF with the text
    content_stream = "BT\n/F1 10 Tf\n"
    y = 780
    for line in lines:
        # Escape special PDF characters
        safe_line = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        content_stream += f"1 0 0 1 40 {y} Tm\n({safe_line}) Tj\n"
        y -= 14
        if y < 40:
            break
    content_stream += "ET\n"

    # Since creating a proper PDF programmatically without libs is complex,
    # let's save as a well-formatted text file and use a simpler approach
    # We'll create the file that our system can index as text
    txt_path = os.path.join(policies_dir, "acme_company_policies.txt")
    with open(txt_path, "w") as f:
        f.write(policy_text)

    print(f"✅ Sample policy document created at: {txt_path}")
    return txt_path


if __name__ == "__main__":
    create_policy_pdf()
