function detectDelimiter(sampleLine) {
  const commaCount = (sampleLine.match(/,/g) || []).length;
  const semicolonCount = (sampleLine.match(/;/g) || []).length;
  return semicolonCount >= commaCount ? ';' : ',';
}

function parseCSVRows(text, delimiter) {
  const rows = [];
  let current = '';
  let row = [];
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];

    if (char === '"') {
      if (inQuotes && text[i + 1] === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === delimiter && !inQuotes) {
      row.push(current.trim());
      current = '';
      continue;
    }

    if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && text[i + 1] === '\n') {
        i += 1;
      }
      row.push(current.trim());
      rows.push(row);
      row = [];
      current = '';
      continue;
    }

    current += char;
  }

  // push the last field
  if (inQuotes) {
    row.push(current.trim());
  } else {
    row.push(current.trim());
  }
  rows.push(row);

  return rows.filter((r) => !(r.length === 1 && r[0] === ''));
}

export async function loadCSV(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Falha ao carregar CSV (${response.status})`);
  }

  const text = await response.text();
  const trimmed = text.trim();
  if (!trimmed) {
    return [];
  }

  const firstLine = trimmed.split(/\r?\n/).find((line) => line.trim().length > 0);
  const delimiter = detectDelimiter(firstLine || ',');
  const rows = parseCSVRows(text, delimiter);
  if (!rows.length) {
    return [];
  }

  const headers = rows[0].map((header) => header.trim());
  const dataRows = rows.slice(1);
  return dataRows.map((entries) => {
    const record = {};
    headers.forEach((header, index) => {
      record[header] = entries[index] ?? '';
    });
    return record;
  });
}
