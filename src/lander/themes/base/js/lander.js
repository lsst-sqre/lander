/*
 * Core JavaScript applicaiton for Lander landing pages.
 *
 * This script controls PDFObject to embed a PDF on the landing page.
 *
 */

const PDFObject = require('pdfobject');

// ID of div that contains the embedded PDF
const containerId = 'lander-pdf-container';

// PDF URL information embedded as a data attribute
const pdfContainer = document.getElementById(containerId);
const pdfPath = pdfContainer.dataset.pdfPath;

// Try to get the page number from  search parameters
const urlParams = new URLSearchParams(document.location.search.substring(1));
const pageNumber = urlParams.get('page');
const pdfOptions = {};
if (pageNumber) {
  pdfOptions.page = pageNumber;
}

PDFObject.embed(pdfPath, `#${containerId}`, pdfOptions);
