# Document Analysis Testing Guide

This guide provides detailed instructions for testing the Document Analysis service of the Legal AI application with sample documents.

## Prerequisites
- The Legal AI application is running locally (backend and frontend)
- Sample documents are available in the `/samples/documents/` directory

## Step-by-Step Testing Instructions

### 1. Accessing the Document Analysis Service

1. Open your web browser and navigate to http://localhost:3000
2. Log in with the following credentials:
   - Email: user@example.com
   - Password: password123
3. From the dashboard, click on "Document Analysis" in the left sidebar

### 2. Testing with Employment Contract

#### Upload the Document
1. Click the "Upload Document" button
2. In the file selection dialog, navigate to `/samples/documents/` and select `employment_contract.txt`
3. Enter the following metadata:
   - Title: "Sample Employment Contract"
   - Description: "Standard employment agreement for testing"
4. Click "Upload" to submit the document

#### Analyze the Document
1. Once uploaded, the document should appear in your document list
2. Click on the document to view its details
3. Click the "Analyze Document" button
4. In the analysis options dialog:
   - Select "GPT-4" as the LLM model (or your preferred model)
   - Click "Start Analysis"
5. Wait for the analysis to complete (this may take 15-30 seconds)

#### Expected Results
The analysis should provide:
- **Summary**: A concise overview of the employment agreement
- **Key Points**: Important terms including position, compensation, benefits, and termination
- **Entities**: Identification of parties (ABC Corporation, John Smith), dates (January 15, 2025, February 1, 2025), and monetary values ($120,000)
- **Recommendations**: Suggestions for improving the contract, such as adding more specific performance metrics or clarifying termination conditions

#### Testing Different Models
1. Return to the document view
2. Click "Analyze Document" again
3. Select a different LLM model (e.g., "Gemini Pro" or "DeepSeek")
4. Compare the results with the previous analysis
5. Note differences in:
   - Comprehensiveness of the summary
   - Number and quality of key points identified
   - Accuracy of entity extraction
   - Relevance of recommendations

### 3. Testing with Non-Disclosure Agreement

#### Upload the Document
1. Return to the Document Analysis dashboard
2. Click the "Upload Document" button
3. In the file selection dialog, navigate to `/samples/documents/` and select `nda.txt`
4. Enter the following metadata:
   - Title: "Sample Non-Disclosure Agreement"
   - Description: "Standard NDA for testing"
5. Click "Upload" to submit the document

#### Analyze the Document
1. Once uploaded, click on the document to view its details
2. Click the "Analyze Document" button
3. In the analysis options dialog:
   - Select "GPT-4" as the LLM model (or your preferred model)
   - Click "Start Analysis"
4. Wait for the analysis to complete

#### Expected Results
The analysis should provide:
- **Summary**: A concise overview of the NDA's purpose and scope
- **Key Points**: Important terms including definition of confidential information, obligations of receiving party, term duration, and governing law
- **Entities**: Identification of parties (XYZ Inc., ABC Corporation), dates (March 10, 2025), and duration (24 months)
- **Recommendations**: Suggestions for improving the NDA, such as adding more specific remedies for breach or clarifying the return of confidential information

### 4. Testing Document Comparison

1. From the Document Analysis dashboard, select both documents by checking the boxes next to them
2. Click the "Compare Documents" button
3. In the comparison options dialog:
   - Select "GPT-4" as the LLM model (or your preferred model)
   - Click "Start Comparison"
4. Wait for the comparison to complete

#### Expected Results
The comparison should provide:
- **Similarities**: Common legal structures, governing law provisions, signature blocks
- **Differences**: Purpose of agreements, obligations of parties, term durations, specific clauses
- **Recommendations**: Suggestions for standardizing language across documents or improving specific clauses

### 5. Testing Batch Analysis

1. From the Document Analysis dashboard, select both documents by checking the boxes next to them
2. Click the "Batch Analyze" button
3. In the batch analysis options dialog:
   - Select "GPT-4" as the LLM model (or your preferred model)
   - Click "Start Batch Analysis"
4. Wait for the batch analysis to complete

#### Expected Results
The batch analysis should provide:
- Individual analyses for each document
- A summary of common themes or issues across documents
- Recommendations for document management or standardization

## Troubleshooting Document Analysis

### Common Issues and Solutions

#### Document Upload Fails
- **Issue**: The document fails to upload or returns an error
- **Solution**: 
  - Verify the file format is supported (.txt, .pdf, .docx)
  - Check that the file size is under the limit (typically 10MB)
  - Ensure the document is not corrupted

#### Analysis Takes Too Long
- **Issue**: The document analysis process seems to hang or takes an unusually long time
- **Solution**:
  - For large documents, analysis may take longer
  - Check your internet connection if using cloud-based LLM models
  - Refresh the page and try again with a smaller document

#### Poor Analysis Results
- **Issue**: The analysis results are incomplete or inaccurate
- **Solution**:
  - Try a different LLM model
  - Ensure the document is properly formatted
  - For complex legal documents, try breaking them into smaller sections

## Performance Comparison Table

| Feature | GPT-4 | Gemini Pro | DeepSeek |
|---------|-------|------------|----------|
| Summary Quality | Comprehensive | Good | Good |
| Entity Recognition | Excellent | Very Good | Good |
| Key Points Extraction | Detailed | Concise | Moderate |
| Recommendations | Specific & Relevant | General | Basic |
| Processing Speed | Moderate | Fast | Very Fast |

## Next Steps

After testing the Document Analysis service, you can:
1. Experiment with more complex legal documents
2. Fine-tune the analysis parameters for better results
3. Integrate the analysis results with the other services
4. Proceed to testing the Legal Research service

This completes the testing guide for the Document Analysis service of the Legal AI application.
