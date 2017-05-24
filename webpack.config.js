var webpack = require('webpack');
var path = require('path');

module.exports = {
  context: __dirname,

  entry: {
    'app': './js/app.js',
  },

  output: {
    path: path.join(__dirname, 'lander', 'assets'),
    filename: '[name].bundle.js'
  },

  plugins: [
    new webpack.optimize.UglifyJsPlugin({
      compressor: {
        screw_ie8: true,
        warnings: false
      }
    })
  ]

};
