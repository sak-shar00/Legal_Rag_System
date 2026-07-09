// extract.js
// Reads all PDFs from documents/<category>/ folders,
// extracts text PAGE BY PAGE, and saves everything into one JSON file
// with metadata (doc_id, doc_type, filename, page_number, text).

const fs = require('fs');
const path = require('path');
const pdf = require('pdf-parse');

const CATEGORIES = ['acts', 'judgments', 'pov', 'tax'];
const DOCUMENTS_DIR = './documents';
const OUTPUT_FILE = './extracted_data.json';

async function extractTextFromPDF(filePath) {
  const dataBuffer = fs.readFileSync(filePath);
  const pages = [];
  let pageNum = 0;

  const options = {
    // This function runs once per page while pdf-parse reads the file
    pagerender: async function (pageData) {
      pageNum++;
      const textContent = await pageData.getTextContent();
      const pageText = textContent.items.map(item => item.str).join(' ');
      pages.push({
        page_number: pageNum,
        text: pageText.trim()
      });
      return pageText;
    }
  };

  const data = await pdf(dataBuffer, options);

  return {
    total_pages: data.numpages,
    pages: pages
  };
}

async function processAllDocuments() {
  const allDocuments = [];
  let docCounter = 1;

  for (const category of CATEGORIES) {
    const categoryPath = path.join(DOCUMENTS_DIR, category);

    if (!fs.existsSync(categoryPath)) {
      console.log(`Skipping ${category} - folder not found`);
      continue;
    }

    const files = fs.readdirSync(categoryPath).filter(f => f.endsWith('.pdf'));

    for (const file of files) {
      const filePath = path.join(categoryPath, file);
      console.log(`Processing: ${file}...`);

      try {
        const extracted = await extractTextFromPDF(filePath);

        allDocuments.push({
          doc_id: `${category}_${String(docCounter).padStart(3, '0')}`,
          doc_type: category,
          filename: file,
          total_pages: extracted.total_pages,
          pages: extracted.pages
        });

        docCounter++;
        console.log(`  Done - ${extracted.total_pages} pages extracted`);
      } catch (err) {
        console.log(`  ERROR processing ${file}:`, err.message);
      }
    }
  }

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(allDocuments, null, 2));
  console.log(`\nAll done! Extracted ${allDocuments.length} documents.`);
  console.log(`Saved to ${OUTPUT_FILE}`);
}

processAllDocuments();