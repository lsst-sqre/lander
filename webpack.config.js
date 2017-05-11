// Webpack configuration for building pdf.js into a bundle is based on:
// https://github.com/mozilla/pdf.js/blob/master/examples/webpack/webpack.config.js
//
// Method for copying the pdf.worker.js bundle into the assets/ dir is from:
// via https://github.com/mozilla/pdf.js/issues/7612#issuecomment-258827877

var webpack = require('webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');
var path = require('path');

module.exports = {
  context: __dirname,

  entry: {
    'app': './js/app.js',
  },

  output: {
    path: path.join(__dirname, 'assets'),
    filename: '[name].bundle.js'
  },

  plugins: [
    new webpack.optimize.UglifyJsPlugin({
      compressor: {
        screw_ie8: true,
        warnings: false
      }
    }),

    new CopyWebpackPlugin([{
      from: 'node_modules/pdfjs-dist/build/pdf.worker.js',
      to: 'pdf.worker.js'
    }])
  ]

};
