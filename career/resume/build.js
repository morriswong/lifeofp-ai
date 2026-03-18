/**
 * build.js — Converts Morris_Wong_Resume_Apple_MLE.md → Morris_Wong_Resume_Apple_MLE.docx
 *
 * Markdown format expected:
 *   # Name
 *   contact line with [link text](url) hyperlinks
 *   ---  (section dividers are ignored)
 *   ## Section Name
 *   ### Job Title | Date
 *   *Company description | Location*
 *   - bullet
 *   **Bold label:** value  (for skills lines)
 */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, ExternalHyperlink, WidthType, BorderStyle, LevelFormat
} = require('docx');
const fs = require('fs');
const path = require('path');

// ── Page geometry (A4, narrow margins matching original) ──────────────────────
const CONTENT_WIDTH = 10886;
const JOB_LEFT      = 7947;
const JOB_RIGHT     = CONTENT_WIDTH - JOB_LEFT;   // 2939
const HEADER_LEFT   = 6532;
const HEADER_RIGHT  = CONTENT_WIDTH - HEADER_LEFT; // 4354

// ── Shared style helpers ──────────────────────────────────────────────────────
const noBorder  = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const noMargins = { top: 0, bottom: 0, left: 0, right: 0 };
const tableBorders = {
  ...noBorders,
  insideH: { style: BorderStyle.SINGLE, size: 4, color: 'auto' },
  insideV: { style: BorderStyle.SINGLE, size: 4, color: 'auto' },
};

function sectionHeader(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: 'Calibri', size: 26, bold: true })],
    spacing: { before: 120, after: 0, line: 276, lineRule: 'auto' },
  });
}

function thinRule() {
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [CONTENT_WIDTH],
    borders: tableBorders,
    rows: [new TableRow({ children: [new TableCell({
      width: { size: CONTENT_WIDTH, type: WidthType.DXA },
      borders: { top: noBorder, left: noBorder, right: noBorder,
                 bottom: { style: BorderStyle.SINGLE, size: 6, color: '000000' } },
      margins: noMargins,
      children: [new Paragraph({
        children: [new TextRun({ text: '', font: 'Calibri', size: 1 })],
        spacing: { before: 0, after: 0, line: 1, lineRule: 'exact' },
      })],
    })] })],
  });
}

function twoColTable(leftText, rightText, leftW, rightW, bold = false, spacingBefore = 80) {
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [leftW, rightW],
    borders: tableBorders,
    rows: [new TableRow({ children: [
      new TableCell({
        width: { size: leftW, type: WidthType.DXA },
        borders: noBorders, margins: noMargins,
        children: [new Paragraph({
          children: [new TextRun({ text: leftText, font: 'Calibri', size: 20, bold })],
          spacing: { before: spacingBefore, after: 0, line: 276, lineRule: 'auto' },
        })],
      }),
      new TableCell({
        width: { size: rightW, type: WidthType.DXA },
        borders: noBorders, margins: noMargins,
        children: [new Paragraph({
          children: [new TextRun({ text: rightText, font: 'Calibri', size: 20 })],
          spacing: { before: spacingBefore, after: 0, line: 276, lineRule: 'auto' },
          alignment: AlignmentType.RIGHT,
        })],
      }),
    ] })],
  });
}

function subRow(descText, locationText) {
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [JOB_LEFT, JOB_RIGHT],
    borders: tableBorders,
    rows: [new TableRow({ children: [
      new TableCell({
        width: { size: JOB_LEFT, type: WidthType.DXA },
        borders: noBorders, margins: noMargins,
        children: [new Paragraph({
          children: [new TextRun({ text: descText, font: 'Calibri', size: 20, italics: true })],
          spacing: { before: 0, after: 60, line: 276, lineRule: 'auto' },
        })],
      }),
      new TableCell({
        width: { size: JOB_RIGHT, type: WidthType.DXA },
        borders: noBorders, margins: noMargins,
        children: [new Paragraph({
          children: [new TextRun({ text: locationText, font: 'Calibri', size: 20, italics: true })],
          spacing: { before: 0, after: 60, line: 276, lineRule: 'auto' },
          alignment: AlignmentType.RIGHT,
        })],
      }),
    ] })],
  });
}

function bulletPara(text) {
  return new Paragraph({
    numbering: { reference: 'bullets', level: 0 },
    children: [new TextRun({ text, font: 'Calibri', size: 20 })],
    spacing: { before: 0, after: 40, line: 276, lineRule: 'auto' },
  });
}

// Parse **Bold:** value into mixed TextRun array
function skillLinePara(rawText) {
  const children = [];
  const regex = /\*\*(.+?)\*\*([^*]*)/g;
  let lastIndex = 0, m;
  while ((m = regex.exec(rawText)) !== null) {
    if (m.index > lastIndex)
      children.push(new TextRun({ text: rawText.slice(lastIndex, m.index), font: 'Calibri', size: 20 }));
    children.push(new TextRun({ text: m[1], font: 'Calibri', size: 20, bold: true }));
    if (m[2]) children.push(new TextRun({ text: m[2], font: 'Calibri', size: 20 }));
    lastIndex = m.index + m[0].length;
  }
  if (lastIndex < rawText.length)
    children.push(new TextRun({ text: rawText.slice(lastIndex), font: 'Calibri', size: 20 }));
  return new Paragraph({
    children,
    spacing: { before: 40, after: 40, line: 276, lineRule: 'auto' },
  });
}

// Parse contact line: text with [label](url) hyperlinks
function contactLinePara(text, align) {
  const children = [];
  const regex = /\[([^\]]+)\]\(([^)]+)\)/g;
  let lastIndex = 0, m;
  while ((m = regex.exec(text)) !== null) {
    if (m.index > lastIndex)
      children.push(new TextRun({ text: text.slice(lastIndex, m.index), font: 'Calibri', size: 20 }));
    children.push(new ExternalHyperlink({
      link: m[2],
      children: [new TextRun({ text: m[1], style: 'Hyperlink', font: 'Calibri', size: 20 })],
    }));
    lastIndex = m.index + m[0].length;
  }
  if (lastIndex < text.length)
    children.push(new TextRun({ text: text.slice(lastIndex), font: 'Calibri', size: 20 }));
  return { children, alignment: align };
}

// ── Markdown parser ───────────────────────────────────────────────────────────
function parseMd(mdText) {
  const lines = mdText.split('\n');
  const docChildren = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // H1 = Name
    if (line.startsWith('# ')) {
      const name = line.slice(2).trim();
      docChildren.push(new Paragraph({
        children: [new TextRun({ text: name, font: 'Calibri', size: 46, bold: true })],
        spacing: { before: 0, after: 0, line: 276, lineRule: 'auto' },
      }));
      i++;
      // Next non-empty line = contact info
      while (i < lines.length && lines[i].trim() === '') i++;
      if (i < lines.length && !lines[i].startsWith('#') && !lines[i].startsWith('-')) {
        const contactLine = lines[i].trim();
        // Split into left (up to first link) and right (links)
        const pipeIdx = contactLine.indexOf('|');
        let leftText = contactLine, rightText = '';
        if (pipeIdx !== -1) {
          // Find where the links start — split at last pipe before first [
          const linkStart = contactLine.indexOf('[');
          if (linkStart !== -1) {
            // Find the pipe just before the first link
            const beforeLinks = contactLine.slice(0, linkStart).trimEnd();
            const lastPipe = beforeLinks.lastIndexOf('|');
            leftText  = contactLine.slice(0, lastPipe).trim();
            rightText = contactLine.slice(lastPipe + 1).trim();
          }
        }
        const left  = contactLinePara(leftText,  AlignmentType.LEFT);
        const right = contactLinePara(rightText, AlignmentType.RIGHT);
        docChildren.push(new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [HEADER_LEFT, HEADER_RIGHT],
          borders: tableBorders,
          rows: [new TableRow({ children: [
            new TableCell({
              width: { size: HEADER_LEFT, type: WidthType.DXA },
              borders: noBorders, margins: noMargins,
              children: [new Paragraph({
                children: left.children,
                spacing: { before: 60, after: 80, line: 276, lineRule: 'auto' },
              })],
            }),
            new TableCell({
              width: { size: HEADER_RIGHT, type: WidthType.DXA },
              borders: noBorders, margins: noMargins,
              children: [new Paragraph({
                children: right.children,
                alignment: AlignmentType.RIGHT,
                spacing: { before: 60, after: 80, line: 276, lineRule: 'auto' },
              })],
            }),
          ] })],
        }));
        i++;
      }
      continue;
    }

    // H2 = Section header + thin rule
    if (line.startsWith('## ')) {
      const title = line.slice(3).trim();
      docChildren.push(sectionHeader(title));
      docChildren.push(thinRule());
      i++;
      continue;
    }

    // H3 = Job/project entry: "### Title | Date"
    if (line.startsWith('### ')) {
      const raw = line.slice(4).trim();
      const pipeIdx = raw.lastIndexOf(' | ');
      let title = raw, date = '';
      if (pipeIdx !== -1) {
        title = raw.slice(0, pipeIdx).trim();
        date  = raw.slice(pipeIdx + 3).trim();
      }
      docChildren.push(twoColTable(title, date, JOB_LEFT, JOB_RIGHT, true, 80));
      i++;

      // Optional italic sub-line: *description | location*
      if (i < lines.length && lines[i].trim().startsWith('*')) {
        const subRaw = lines[i].trim().replace(/^\*|\*$/g, '');
        const subPipe = subRaw.lastIndexOf(' | ');
        if (subPipe !== -1) {
          docChildren.push(subRow(subRaw.slice(0, subPipe).trim(), subRaw.slice(subPipe + 3).trim()));
        } else {
          docChildren.push(subRow(subRaw, ''));
        }
        i++;
      }

      // Optional bold subtitle (project name): **text**
      if (i < lines.length && lines[i].trim().startsWith('**') && lines[i].trim().endsWith('**') && !lines[i].includes(':')) {
        const subtitle = lines[i].trim().replace(/^\*\*|\*\*$/g, '');
        docChildren.push(new Paragraph({
          children: [new TextRun({ text: subtitle, font: 'Calibri', size: 20, bold: true })],
          spacing: { before: 0, after: 40, line: 276, lineRule: 'auto' },
        }));
        i++;
      }
      continue;
    }

    // Bullet point
    if (line.startsWith('- ')) {
      docChildren.push(bulletPara(line.slice(2).trim()));
      i++;
      continue;
    }

    // Skills line: **Bold:** value
    if (line.trim().startsWith('**') && line.includes(':**')) {
      docChildren.push(skillLinePara(line.trim()));
      i++;
      continue;
    }

    // Plain paragraph (summary text, etc.)
    if (line.trim() && !line.startsWith('---')) {
      docChildren.push(new Paragraph({
        children: [new TextRun({ text: line.trim(), font: 'Calibri', size: 20 })],
        spacing: { before: 60, after: 60, line: 276, lineRule: 'auto' },
      }));
    }

    i++;
  }

  return docChildren;
}

// ── Build ─────────────────────────────────────────────────────────────────────
const mdPath   = path.join(__dirname, 'Morris_Wong_Resume_Apple_MLE.md');
const outPath  = path.join(__dirname, 'Morris_Wong_Resume_Apple_MLE.docx');
const mdText   = fs.readFileSync(mdPath, 'utf8');

const doc = new Document({
  numbering: {
    config: [{
      reference: 'bullets',
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: '\u2022',
        alignment: AlignmentType.LEFT,
        style: {
          paragraph: { indent: { left: 360, hanging: 180 } },
          run: { font: 'Symbol', size: 20 },
        },
      }],
    }],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 737, right: 510, bottom: 737, left: 510 },
      },
    },
    children: parseMd(mdText),
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outPath, buf);
  console.log(`✓ Built ${path.basename(outPath)}`);
});
