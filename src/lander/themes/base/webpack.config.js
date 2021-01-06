const webpack = require('webpack');
const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {
  context: __dirname,

  mode: 'production',

  entry: {
    app: path.resolve(__dirname, 'js', 'lander.js'),
  },

  output: {
    path: path.join(__dirname, 'site'),
    filename: 'lander.bundle.js',
  },

  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin()],
  },

  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },
    ],
  },
};
