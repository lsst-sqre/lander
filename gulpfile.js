const gulp = require('gulp');
const run = require('gulp-run');

function hello() {
  console.log('Hello gulp!');
  return Promise.resolve();
}

exports.hello = hello;

function environment() {
  console.log(`${env}`);
  return Promise.resolve();
}

exports.environment = environment;

// Build JS for base theme
function baseJs() {
  return run(
    './node_modules/.bin/webpack --config src/lander/themes/base/webpack.config.js'
  ).exec();
}

exports.baseJs = baseJs;

// Single task to build all assets (for CI)
exports.assets = gulp.parallel(baseJs);

// General live-compile for development
function watcher() {
  gulp.watch(
    `src/lander/themes/base/js/*.js`,
    { ignoreInitial: false },
    baseJs
  );
}

exports.default = watcher;
