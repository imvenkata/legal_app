# Legal AI Application - Local Testing Guide with Sample Documents

This guide will walk you through testing all three services of the Legal AI application locally using sample documents. This is perfect for demonstrating the application's capabilities to others.

## Table of Contents
1. [Setup and Installation](#setup-and-installation)
2. [Sample Documents](#sample-documents)
3. [Testing Document Analysis Service](#testing-document-analysis-service)
4. [Testing Legal Research Service](#testing-legal-research-service)
5. [Testing Contract Generation Service](#testing-contract-generation-service)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

## Setup and Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 14 or higher
- npm 6 or higher
- Git

### Clone the Repository
```bash
git clone https://github.com/yourusername/legal_app.git
cd legal_app
```

### Backend Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### Frontend Setup
```bash
# Install dependencies
cd frontend
npm install
cd ..
```

### Start the Application
```bash
# Start the backend
cd backend
python3 app.py &
cd ..

# Start the frontend (in a new terminal)
cd frontend
npm start
```

The application should now be running at:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## Sample Documents

For testing purposes, we've prepared sample documents for each service. Create a `samples` directory in the project root:

```bash
mkdir -p samples/documents samples/research samples/contracts
```

### Document Analysis Samples
Download these sample legal documents to the `samples/documents` directory:

1. **Employment Contract**
   ```bash
   curl -o samples/documents/employment_contract.pdf https://example.com/samples/employment_contract.pdf
   ```
   
   Alternatively, create a simple employment contract using the text below and save it as `employment_contract.txt`:
   
   ```
   EMPLOYMENT AGREEMENT
   
   THIS AGREEMENT is made on January 15, 2025,
   
   BETWEEN:
   ABC Corporation, with an address at 123 Business Ave, Metropolis ("Employer"),
   
   AND:
   John Smith, with an address at 456 Residential St, Metropolis ("Employee").
   
   WHEREAS, the Employer desires to employ the Employee, and the Employee desires to accept employment with the Employer, under the terms and conditions set forth in this Agreement,
   
   NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:
   
   1. POSITION AND DUTIES
   The Employer hereby employs the Employee as Senior Software Developer, and the Employee hereby accepts such employment. The Employee shall perform such duties as are customarily performed by someone in such position and such other duties as may be assigned from time to time by the Employer.
   
   2. TERM
   This Agreement shall commence on February 1, 2025 and continue until terminated by either party in accordance with this Agreement.
   
   3. COMPENSATION
   The Employer shall pay the Employee a salary of $120,000 per year, payable bi-weekly.
   
   4. BENEFITS
   The Employee shall be entitled to the following benefits:
   - Health insurance
   - 401(k) retirement plan
   - 15 days of paid vacation per year
   - 5 days of paid sick leave per year
   
   5. TERMINATION
   Either party may terminate this Agreement by providing the other party with at least 30 days' written notice.
   
   6. GOVERNING LAW
   This Agreement shall be governed by and construed in accordance with the laws of the State of New York.
   
   IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.
   
   ABC Corporation
   
   By: ________________________
   Name: Jane Doe
   Title: CEO
   
   John Smith
   
   By: ________________________
   ```

2. **Non-Disclosure Agreement**
   ```bash
   curl -o samples/documents/nda.pdf https://example.com/samples/nda.pdf
   ```
   
   Alternatively, create a simple NDA using the text below and save it as `nda.txt`:
   
   ```
   NON-DISCLOSURE AGREEMENT
   
   THIS AGREEMENT is made on March 10, 2025,
   
   BETWEEN:
   XYZ Inc., with an address at 789 Corporate Blvd, Metropolis ("Disclosing Party"),
   
   AND:
   ABC Corporation, with an address at 123 Business Ave, Metropolis ("Receiving Party").
   
   WHEREAS, the Disclosing Party possesses certain confidential and proprietary information, and
   
   WHEREAS, the Receiving Party is willing to receive and hold such confidential information in confidence under the terms of this Agreement,
   
   NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:
   
   1. DEFINITION OF CONFIDENTIAL INFORMATION
   "Confidential Information" means any information disclosed by the Disclosing Party to the Receiving Party, either directly or indirectly, in writing, orally or by inspection of tangible objects, which is designated as "Confidential," "Proprietary" or some similar designation, or that should reasonably be understood to be confidential given the nature of the information and the circumstances of disclosure.
   
   2. OBLIGATIONS OF RECEIVING PARTY
   The Receiving Party shall:
   (a) Use the Confidential Information only for the purpose of evaluating potential business and investment relationships with the Disclosing Party;
   (b) Hold the Confidential Information in strict confidence and take reasonable precautions to protect such Confidential Information;
   (c) Not disclose any Confidential Information to any third party without the prior written consent of the Disclosing Party;
   (d) Not copy or reproduce any Confidential Information without the prior written consent of the Disclosing Party.
   
   3. TERM
   This Agreement shall remain in effect for a period of 24 months from the Effective Date.
   
   4. GOVERNING LAW
   This Agreement shall be governed by and construed in accordance with the laws of the State of California.
   
   IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.
   
   XYZ Inc.
   
   By: ________________________
   Name: Robert Johnson
   Title: President
   
   ABC Corporation
   
   By: ________________________
   Name: Jane Doe
   Title: CEO
   ```

### Legal Research Samples
Create sample case briefs in the `samples/research` directory:

1. **Contract Breach Case**
   Create a file named `contract_breach_case.txt` with the following content:
   
   ```
   CASE BRIEF: Smith v. Jones (2023)
   
   FACTS:
   On January 10, 2023, Smith entered into a contract with Jones for the delivery of 1,000 custom widgets by March 15, 2023, for a total price of $50,000. Smith paid a 50% deposit ($25,000) upon signing the contract. The contract specified that time was of the essence and included a clause stating that any delay in delivery would result in liquidated damages of $500 per day. Jones delivered the widgets on April 10, 2023, 26 days late. Smith refused to pay the remaining $25,000 and demanded a refund of $13,000 (26 days × $500) from the initial deposit. Jones argued that the delay was caused by supply chain issues beyond his control and refused to pay the liquidated damages.
   
   LEGAL ISSUES:
   1. Is Jones liable for breach of contract?
   2. Are the liquidated damages enforceable?
   3. Does Jones have a valid defense based on supply chain issues?
   
   RELEVANT LAW:
   - Uniform Commercial Code § 2-615 (Excuse by Failure of Presupposed Conditions)
   - Restatement (Second) of Contracts § 356 (Liquidated Damages and Penalties)
   - Local precedent: Wilson Corp v. Allen Inc (2022) - Court found that supply chain issues during post-pandemic period could constitute force majeure if properly documented
   
   ARGUMENTS:
   Smith argues that the contract terms were clear, time was of the essence, and the liquidated damages are reasonable given the nature of the custom widgets and their importance to Smith's business operations. Jones argues that the supply chain issues were unforeseeable and beyond his control, constituting a force majeure event that should excuse the delay in performance.
   ```

2. **Employment Law Case**
   Create a file named `employment_law_case.txt` with the following content:
   
   ```
   CASE BRIEF: Johnson v. Tech Innovations LLC (2024)
   
   FACTS:
   Sarah Johnson was employed by Tech Innovations LLC as a senior software engineer from May 2020 to December 2023. Her employment contract included a non-compete clause prohibiting her from working for any competing company within a 100-mile radius for 2 years after termination. In January 2024, Johnson accepted a position with DataSoft Inc., a direct competitor located 30 miles away. Tech Innovations filed for an injunction to enforce the non-compete agreement. Johnson argues that the non-compete is overly broad and unenforceable, and that her specialized skills in AI development mean that enforcing the agreement would cause her undue hardship.
   
   LEGAL ISSUES:
   1. Is the non-compete agreement enforceable?
   2. Does the agreement impose undue hardship on Johnson?
   3. Does Tech Innovations have a legitimate business interest to protect?
   
   RELEVANT LAW:
   - State statute on non-compete agreements (varies by jurisdiction)
   - Restatement (Second) of Contracts § 188 (Restraint of Trade)
   - Local precedent: Parker LLC v. Thompson (2021) - Court held that a 2-year, 50-mile radius non-compete for a software developer was reasonable
   
   ARGUMENTS:
   Tech Innovations argues that the non-compete is reasonable in scope and necessary to protect their proprietary AI algorithms and client relationships. Johnson argues that the 100-mile radius is excessive given the nature of remote work in the software industry, and that her specialized skills mean she cannot find comparable employment outside the restricted area without relocating her family.
   ```

### Contract Generation Samples
For contract generation, we'll use templates and parameters rather than sample documents. The application already includes templates for:
- Non-Disclosure Agreement
- Service Agreement
- Employment Contract

## Testing Document Analysis Service

1. **Access the Application**
   Open your browser and navigate to http://localhost:3000

2. **Login**
   Use the following credentials:
   - Email: user@example.com
   - Password: password123

3. **Navigate to Document Analysis**
   Click on "Document Analysis" in the sidebar navigation

4. **Upload a Sample Document**
   - Click "Select File" and choose one of the sample documents from the `samples/documents` directory
   - Enter a title (e.g., "Sample Employment Contract")
   - Enter a description (optional)
   - Click "Upload"

5. **Analyze the Document**
   - Once the document is uploaded, click "Analyze Document"
   - Select your preferred LLM model (e.g., GPT-4, Gemini Pro, or DeepSeek)
   - Wait for the analysis to complete

6. **Review Analysis Results**
   The analysis should provide:
   - Document summary
   - Key points extraction
   - Entity identification (people, organizations, dates)
   - Recommendations

7. **Test with Different Documents**
   Repeat steps 4-6 with different sample documents to compare analysis results

8. **Test with Different LLM Models**
   Analyze the same document with different LLM models to compare their performance

## Testing Legal Research Service

1. **Navigate to Legal Research**
   Click on "Legal Research" in the sidebar navigation

2. **Search for Cases**
   - Enter a search query related to one of your sample cases (e.g., "contract breach supply chain issues")
   - Click "Search"

3. **Review Search Results**
   - The system should return relevant cases
   - Click on a case to view more details

4. **Predict Case Outcome**
   - Select a case from the search results
   - Click "Predict Outcome"
   - Select your preferred LLM model
   - Wait for the prediction to complete

5. **Review Prediction Results**
   The prediction should provide:
   - Outcome prediction
   - Confidence level
   - Influential factors
   - Similar cases

6. **Test with Different Queries**
   Repeat steps 2-5 with different search queries based on your sample cases

7. **Test with Different LLM Models**
   Predict outcomes for the same case using different LLM models to compare their predictions

## Testing Contract Generation Service

1. **Navigate to Contract Generation**
   Click on "Contract Generation" in the sidebar navigation

2. **Select a Contract Template**
   - Choose a template (e.g., "Non-Disclosure Agreement")
   - Review the template description

3. **Fill in Contract Parameters**
   For an NDA template, enter parameters such as:
   - First Party Name: XYZ Inc.
   - First Party Address: 789 Corporate Blvd, Metropolis
   - Second Party Name: ABC Corporation
   - Second Party Address: 123 Business Ave, Metropolis
   - Effective Date: March 10, 2025
   - Term (months): 24
   - Governing Law: California

4. **Generate the Contract**
   - Select your preferred LLM model
   - Click "Generate Contract"
   - Wait for the generation to complete

5. **Review Generated Contract**
   - Review the contract content
   - Check that all parameters were correctly incorporated
   - Verify the legal language and structure

6. **Test with Different Templates**
   Repeat steps 2-5 with different contract templates

7. **Test with Different Parameters**
   Generate multiple versions of the same contract type with different parameters

8. **Test with Different LLM Models**
   Generate the same contract using different LLM models to compare their outputs

## Troubleshooting

### Backend Issues

**Problem**: Backend service doesn't start
**Solution**: 
- Check if another process is using port 8000
- Verify that all dependencies are installed
- Check the console for error messages
```bash
# Check for processes using port 8000
lsof -i :8000
# Kill the process if needed
kill -9 <PID>
```

**Problem**: API endpoints return 500 errors
**Solution**:
- Check the backend logs for error details
- Verify that the database connection is working
- Ensure environment variables are set correctly

### Frontend Issues

**Problem**: Frontend doesn't connect to backend
**Solution**:
- Verify that the backend is running
- Check the API URL in the frontend configuration
- Look for CORS errors in the browser console

**Problem**: File upload doesn't work
**Solution**:
- Check file size limits
- Verify supported file formats
- Ensure the upload directory is writable

### LLM Integration Issues

**Problem**: LLM model doesn't generate results
**Solution**:
- Verify API keys are set correctly
- Check network connectivity to the LLM provider
- Ensure the selected model is available

## Next Steps

After successfully testing the application locally, you might want to:

1. **Customize the LLM Integration**
   - Add your own API keys for production use
   - Adjust model parameters for better results
   - Add support for additional LLM models

2. **Enhance the Sample Documents**
   - Add more diverse document types
   - Create industry-specific templates
   - Develop benchmark documents for performance testing

3. **Deploy to Production**
   - Follow the Azure deployment guide
   - Set up proper authentication
   - Configure production databases

4. **Gather Feedback**
   - Document user experiences with different models
   - Identify areas for improvement
   - Prioritize feature enhancements

By following this guide, you should be able to thoroughly test and demonstrate all three services of the Legal AI application using sample documents. This will provide a comprehensive understanding of the application's capabilities and performance with different types of legal documents and LLM models.
