const fs = require("fs");

const INPUT_FILE = "./extracted_data.json";
const OUTPUT_FILE = "./chunks.json";

const CHUNK_SIZE = 500;
const OVERLAP = 100;

const documents = JSON.parse(fs.readFileSync(INPUT_FILE, "utf8"));

const chunks = [];

// -----------------------------
// Cleaning Function
// -----------------------------

function cleanText(text) {

    return text

        // remove dots used in tables/index
        .replace(/\.{2,}/g, " ")

        // remove long underscores
        .replace(/_{2,}/g, " ")

        // remove multiple spaces
        .replace(/\s+/g, " ")

        // remove page headers
        .replace(/Page\s+\d+/gi, " ")

        // remove weird characters
        .replace(/[^\x20-\x7E\n]/g, " ")

        .trim();

}

// -----------------------------

for (const document of documents) {

    let chunkCounter = 1;

    const words = [];

    for (const page of document.pages) {

        const cleaned = cleanText(page.text);

        const pageWords = cleaned
            .split(/\s+/)
            .filter(word => word.length > 1);

        for (const word of pageWords) {

            words.push({

                word,

                page: page.page_number

            });

        }

    }

    for (

        let start = 0;

        start < words.length;

        start += (CHUNK_SIZE - OVERLAP)

    ) {

        const end = Math.min(start + CHUNK_SIZE, words.length);

        const currentChunk = words.slice(start, end);

        if (!currentChunk.length) continue;

        const chunkText = currentChunk

            .map(item => item.word)

            .join(" ");

        // Skip useless chunks

        if (chunkText.length < 250)

            continue;

        chunks.push({

            chunk_id:

                `${document.doc_id}_chunk_${chunkCounter}`,

            doc_id:

                document.doc_id,

            filename:

                document.filename,

            doc_type:

                document.doc_type,

            page_start:

                currentChunk[0].page,

            page_end:

                currentChunk[currentChunk.length - 1].page,

            text:

`Document Type: ${document.doc_type}

Document Name: ${document.filename}

${chunkText}`

        });

        chunkCounter++;

        if (end === words.length)

            break;

    }

    console.log(`✔ ${document.filename} → ${chunkCounter - 1} chunks`);

}

fs.writeFileSync(

    OUTPUT_FILE,

    JSON.stringify(chunks, null, 2)

);

console.log("\n================================");

console.log("Total Documents :", documents.length);

console.log("Total Chunks :", chunks.length);

console.log("Saved :", OUTPUT_FILE);

console.log("================================");