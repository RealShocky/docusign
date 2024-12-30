from database import Session, init_db
from models import Template, Tag

# Initialize database
init_db()
db = Session()

# Templates data
templates = [
    {
        'name': 'Non-Disclosure Agreement (NDA)',
        'description': 'A comprehensive NDA for protecting confidential information',
        'category': 'Legal',
        'tags': ['confidentiality', 'legal', 'business'],
        'content': '''NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement (the "Agreement") is entered into as of [DATE] by and between:

[PARTY A NAME], located at [PARTY A ADDRESS] ("Disclosing Party")
and
[PARTY B NAME], located at [PARTY B ADDRESS] ("Receiving Party")

1. CONFIDENTIAL INFORMATION
   Confidential Information shall include, but is not limited to:
   - Trade secrets, proprietary information, and know-how
   - Business strategies and marketing plans
   - Customer and supplier lists
   - Financial information and projections
   - Technical data and research
   - Product development and designs

2. OBLIGATIONS OF RECEIVING PARTY
   The Receiving Party agrees to:
   a) Maintain the confidentiality of the information
   b) Use the information only for the business purpose
   c) Not disclose the information to any third party
   d) Take reasonable security measures to protect the information
   e) Return or destroy all materials containing confidential information upon request

3. EXCLUSIONS
   This Agreement does not apply to information that:
   - Is already in the public domain
   - Was known to the Receiving Party before disclosure
   - Is independently developed by the Receiving Party
   - Is disclosed with the Disclosing Party's written consent

4. TERM AND TERMINATION
   This Agreement shall remain in effect for [DURATION] years from the date of execution.

5. GOVERNING LAW
   This Agreement shall be governed by the laws of [JURISDICTION].

SIGNATURES:

Disclosing Party: _______________ Date: _______________
Name: [PARTY A NAME]
Title: [TITLE]

Receiving Party: _______________ Date: _______________
Name: [PARTY B NAME]
Title: [TITLE]'''
    },
    {
        'name': 'Service Agreement',
        'description': 'A detailed contract for service providers and clients',
        'category': 'Business',
        'tags': ['services', 'business', 'professional'],
        'content': '''SERVICE AGREEMENT

This Service Agreement (the "Agreement") is made on [DATE] between:

[SERVICE PROVIDER NAME] ("Provider")
Address: [PROVIDER ADDRESS]

and

[CLIENT NAME] ("Client")
Address: [CLIENT ADDRESS]

1. SERVICES
   The Provider agrees to perform the following services:
   [DETAILED DESCRIPTION OF SERVICES]

2. COMPENSATION
   2.1 Service Fees: [AMOUNT] per [PERIOD]
   2.2 Payment Terms: [PAYMENT SCHEDULE]
   2.3 Late Payment: [LATE PAYMENT TERMS]

3. TERM AND TERMINATION
   3.1 Term: This Agreement begins on [START DATE] and continues until [END DATE]
   3.2 Termination: Either party may terminate with [NOTICE PERIOD] written notice
   3.3 Early Termination Fee: [AMOUNT]

4. DELIVERABLES
   4.1 The Provider shall deliver:
       [LIST OF DELIVERABLES AND DEADLINES]

5. WARRANTIES
   The Provider warrants that:
   - Services will be performed in a professional manner
   - Will comply with all applicable laws and regulations
   - Has the necessary skills and expertise

6. INTELLECTUAL PROPERTY
   6.1 Ownership of Work Product
   6.2 Pre-existing IP
   6.3 License Grants

7. CONFIDENTIALITY
   [CONFIDENTIALITY TERMS]

8. LIMITATION OF LIABILITY
   [LIABILITY TERMS]

9. INSURANCE
   [INSURANCE REQUIREMENTS]

10. GOVERNING LAW
    This Agreement is governed by [JURISDICTION] law.

SIGNATURES:

Provider: _______________ Date: _______________
Name: [PROVIDER NAME]
Title: [TITLE]

Client: _______________ Date: _______________
Name: [CLIENT NAME]
Title: [TITLE]'''
    },
    {
        'name': 'Employment Contract',
        'description': 'A comprehensive employment agreement template',
        'category': 'HR',
        'tags': ['employment', 'hr', 'legal'],
        'content': '''EMPLOYMENT AGREEMENT

This Employment Agreement (the "Agreement") is made between:

[EMPLOYER NAME] ("Employer")
Address: [EMPLOYER ADDRESS]

and

[EMPLOYEE NAME] ("Employee")
Address: [EMPLOYEE ADDRESS]

1. POSITION AND DUTIES
   1.1 Position: [JOB TITLE]
   1.2 Duties: [DETAILED JOB RESPONSIBILITIES]
   1.3 Work Location: [WORKPLACE ADDRESS]
   1.4 Reporting To: [SUPERVISOR'S TITLE]

2. COMPENSATION AND BENEFITS
   2.1 Base Salary: [AMOUNT] per [PERIOD]
   2.2 Bonus: [BONUS STRUCTURE]
   2.3 Benefits:
       - Health Insurance
       - Retirement Plan
       - Paid Time Off
       - [OTHER BENEFITS]

3. WORK SCHEDULE
   3.1 Hours: [WORK HOURS]
   3.2 Overtime: [OVERTIME POLICY]
   3.3 Remote Work: [REMOTE WORK POLICY]

4. TERM OF EMPLOYMENT
   4.1 Start Date: [START DATE]
   4.2 Term: [EMPLOYMENT TERM]
   4.3 Probation Period: [DURATION]

5. TERMINATION
   5.1 Notice Period: [NOTICE PERIOD]
   5.2 Severance: [SEVERANCE TERMS]
   5.3 Grounds for Termination

6. CONFIDENTIALITY
   6.1 Confidential Information
   6.2 Non-Disclosure Obligations
   6.3 Return of Materials

7. INTELLECTUAL PROPERTY
   7.1 Work Product Ownership
   7.2 Assignment of Rights

8. NON-COMPETE AND NON-SOLICITATION
   8.1 Non-Compete Terms
   8.2 Non-Solicitation Terms
   8.3 Duration and Scope

9. GOVERNING LAW
   This Agreement is governed by [JURISDICTION] law.

SIGNATURES:

Employer: _______________ Date: _______________
Name: [EMPLOYER NAME]
Title: [TITLE]

Employee: _______________ Date: _______________
Name: [EMPLOYEE NAME]'''
    }
]

try:
    # Add templates
    for template_data in templates:
        # Create or get tags
        tags = []
        for tag_name in template_data['tags']:
            tag = db.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            tags.append(tag)
        
        # Create template
        template = Template(
            name=template_data['name'],
            description=template_data['description'],
            content=template_data['content'],
            category=template_data['category']
        )
        template.tags = tags
        db.add(template)
    
    db.commit()
    print("Templates added successfully!")

except Exception as e:
    print(f"Error adding templates: {e}")
    db.rollback()

finally:
    db.close()
