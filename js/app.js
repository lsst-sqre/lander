'use strict';

var PDFObject = require('pdfobject');

var pdfContainer = document.getElementById('pdf-container');
var pdfPath = pdfContainer.dataset.pdfPath;

PDFObject.embed(pdfPath, "#pdf-container");
