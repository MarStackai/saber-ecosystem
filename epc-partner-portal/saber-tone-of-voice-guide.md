# Saber Renewable Energy - Tone of Voice Guides
## Business Operations Apps - EPC Onboarding System

---

## 1. Internal Documentation Voice Guide
*For Saber employees and stakeholders*

### Core Principles
- **Direct and Functional**: Get to the point quickly, focus on what works
- **Process-Oriented**: Clear steps, logical flow, measurable outcomes
- **Collaborative**: Written for teams who need to work together efficiently
- **Technically Accurate**: Precise without being pedantic

### Writing Style

#### Do:
- Start with the purpose: "This system enables..."
- Use numbered steps for processes
- Include clear success criteria
- Reference specific tools and systems by name
- Write in present tense for current state, future tense for planned features
- Use tables for specifications and requirements
- Include version numbers and update dates

#### Don't:
- Add unnecessary context or background
- Use marketing language or fluff
- Explain well-known industry terms
- Write lengthy paragraphs

### Example Content Patterns

**System Overview:**
```
The EPC Onboarding Portal streamlines partner integration through automated 
workflows. It reduces onboarding time from 14 days to 3 days whilst ensuring 
compliance with Saber's quality standards.

Key functions:
1. Partner registration and verification
2. Document collection and validation
3. Compliance checking
4. System access provisioning
```

**Process Documentation:**
```
### Adding a New EPC Partner

Prerequisites:
- Admin access to Business Ops platform
- Partner company number and primary contact details

Steps:
1. Navigate to Partners > Add New EPC
2. Complete mandatory fields (marked with *)
3. Upload required documents (see Document Checklist)
4. Submit for compliance review
5. Monitor status in Dashboard > Pending Approvals

Expected outcome: Partner receives access credentials within 72 hours of approval.
```

**Technical Notes:**
```
API Endpoint: POST /api/v1/partners/epc
Rate limit: 100 requests per hour
Response format: JSON
Authentication: Bearer token (expires 24h)
```

### Vocabulary Guide
- Use "partner" not "vendor" or "supplier" internally
- Use "EPC" not "Engineering, Procurement and Construction" after first mention
- Use "portal" not "platform" for user-facing elements
- Use "workflow" not "process" for automated sequences

---

## 2. External Partner-Facing Voice Guide
*For EPC partners, suppliers, and introducers*

### Core Principles
- **Expert Yet Accessible**: Demonstrate knowledge whilst remaining approachable
- **Partnership-Focused**: Emphasise collaboration and mutual success
- **Clarity First**: Complex renewable energy concepts explained simply
- **Professional Warmth**: Confident and credible, never cold or corporate

### Writing Style

#### Do:
- Lead with benefits to the partner
- Use "we" and "you" to create partnership feel
- Explain technical requirements in business terms
- Provide context for why processes matter
- Celebrate the partnership opportunity
- Use British English consistently (colour, optimise, centre)
- Break complex information into digestible sections

#### Don't:
- Use internal jargon or acronyms without explanation
- Sound bureaucratic or inflexible
- Overwhelm with technical detail upfront
- Use American spellings or punctuation conventions

### Example Content Patterns

**Welcome Messages:**
```
Welcome to the Saber Partner Network

Joining Saber means becoming part of the UK's most innovative renewable 
energy ecosystem. Our streamlined onboarding process gets you operational 
quickly, so we can start delivering transformative energy solutions together.

Your dedicated partner success manager will guide you through three simple stages:
• Registration and verification
• Capability assessment
• Systems integration

Most partners complete onboarding within 72 hours.
```

**Process Explanations:**
```
### Document Requirements

We've streamlined our compliance process to respect your time whilst 
maintaining the high standards our clients expect.

Required documentation includes:
• Company insurance certificates (we accept your existing formats)
• Health and safety policy (your current version is perfect)
• Technical accreditations (MCS, NICEIC, or equivalent)

Why these matter: Our clients trust Saber to deliver excellence. Your 
documentation demonstrates you share our commitment to quality and safety.
```

**Technical Guidance:**
```
### Connecting to Our Systems

Our partner portal gives you real-time visibility of projects, from 
initial enquiry through to commissioning.

You'll be able to:
• View project specifications and timelines
• Submit quotes directly into our workflow
• Track payment milestones
• Access technical resources and training materials

Getting started is straightforward. Once approved, you'll receive secure 
credentials and a 15-minute virtual walkthrough with our team.
```

**Support Communications:**
```
### We're Here to Help

Questions about the onboarding process? Our partner support team specialises 
in getting EPCs operational quickly.

Contact us:
• Portal chat: Instant responses during business hours
• Email: partners@saberrenewables.com (response within 4 hours)
• Phone: 0203 940 3030 (ask for Partner Success)

Remember, your success is our success. We're invested in making this 
partnership work brilliantly.
```

### Key Phrases to Use
- "Streamlined for your convenience"
- "Your expertise, our infrastructure"
- "Partnership in renewable excellence"
- "Clear path to project delivery"
- "Simplified without sacrificing quality"

### Tone Variations by Context

**First Contact**: Welcoming, enthusiastic about partnership potential
**Technical Requirements**: Clear, supportive, explanatory
**Compliance/Legal**: Professional, reassuring, thorough
**Problem Resolution**: Responsive, solution-focused, collaborative
**Success Celebrations**: Warm, appreciative, forward-looking

---

## Implementation Notes

### For Both Guides:
1. Always test content with target audience before full deployment
2. Maintain consistency across all touchpoints
3. Update examples with real success metrics as they become available
4. Review quarterly to ensure alignment with business evolution

### Version Control:
- Current Version: 1.0
- Last Updated: September 2025
- Next Review: December 2025
- Owner: Business Operations Team

### Questions?
Internal: Contact rob@saberrenewables.com
External: Partners contact partners@saberrenewables.com