# Affordable Housing with Bandhu

**Community Involved**

* Bandhu: Affordable housing platform focusing on migrant workers.
* Microsoft Research: Providing technical expertise and support.
* Glyphic: WhatsApp chatbot service provider.
* Agami: Facilitated the initial connection between Bandhu and Jugalbandi.

**Problem Statement**

Migrant workers in India often face significant challenges in finding affordable housing when they move to new cities for work. The lack of accessible information and support systems makes it difficult for them to secure safe and affordable accommodation.

**How Was the Problem Addressed?**

Bandhu developed a platform to help migrant workers discover and avail affordable housing. The solution involves integrating housing options, support services, and relevant information into a user-friendly platform. Through an API, Jugalbandi accesses housing registries compiled by Bandhu along with other third-party services like payment gateways to streamline the process of securing accommodation.

**User Journey**

1. **Query Input:** Migrant workers enter their housing requirements and preferred locations into the platform.
2. **Information Retrieval:** The system searches Bandhu’s database of affordable housing options and related support services.
3. **Result Display:** The user receives a list of available housing options, complete with details about rent, location, amenities, and additional services.
4. **Payment & Confirmation:** The Jugalbandi-enabled service facilitates secure transactions and official registrations.

**What’s Happening in the Backend?**

* **Query Processing:** User queries from workers are processed to understand the specific housing requirements.
* **Third-Party Integrations:** Integration with payment portals allows users to make secure payments. Bandhu’s services help with the discovery of resources, official documentation, and registration.
* **Search and Retrieval:** The system retrieves the most relevant housing options based on the user's query.
* **Response Generation:** The platform generates a list of suitable housing options, providing users with detailed information.

**Implementation Requirements**

Tools:

* Database of affordable housing options.
* Payment Gateway.

Team:

* Developers for technical development and maintenance.
* Housing/migration experts to verify the accuracy of the integrated information.
* Quality assurance team for testing and validating the platform.

**Status**

* Limited implementation with small groups; still running usability experiments and improving the prompts and APIs.

**Roadblocks and Learnings**

1. **Complexity in Data Integration:** Integrating various third-party services like payment portals and housing registries was challenging. Ensuring seamless communication between these services and the Bandhu platform required significant effort.
2. **Query Processing:** Ensuring the chatbot responds intelligently, accurately, and relevantly to user inputs was a challenge. It required refining the length and accuracy of the backend queries to improve response relevance.
3. **User Engagement:** Migrant workers were pleasantly surprised by a voice-based solution designed specifically for them, indicating a positive user reception and a need to continue improving the accessibility and usability of the platform.
