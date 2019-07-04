const gulp = require('gulp');
const express = require('express');
const browserSync = require('browser-sync');
const sass = require('gulp-sass');
const autoprefixer = require('gulp-autoprefixer');
const cleanCss = require('gulp-clean-css');
const sourcemaps = require('gulp-sourcemaps');
const svgstore = require('gulp-svgstore');
const svgmin = require('gulp-svgmin');
const cheerio = require('gulp-cheerio');
const path = require('path');
const rename = require('gulp-rename');
const noop = require('gulp-noop');
const minimist = require('minimist');
const run = require('gulp-run');

// development express server
var server;

// parse command line options
// --env [dev, deploy]
const options = minimist(process.argv);
const env = options.env || 'dev';

const dirs = {
  scss: 'scss',
  squaredScss: 'node_modules/squared/scss',
  svg: 'node_modules/squared/svg',
  icons: 'node_modules/squared/icons',
  assets: 'lander/assets',
  templates: 'lander/templates',
  dev: '_build',
};

// sass modules installed via npm; these are added to node-sass's search paths.
const sassIncludes = ['node_modules'];

// force page reload
function reload() {
  if (server) {
    return browserSync.reload({ stream: true });
  }

  return noop();
}

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

function js() {
  return run('./node_modules/.bin/webpack')
    .exec()
    .pipe(reload());
}

exports.js = js;

function scss() {
  return gulp
    .src(`${dirs.scss}/app.scss`)
    .pipe(env === 'dev' ? sourcemaps.init() : noop())
    .pipe(sass.sync({ includePaths: sassIncludes }).on('error', sass.logError))
    .pipe(autoprefixer())
    .pipe(env === 'dev' ? sourcemaps.write() : noop())
    .pipe(env === 'deploy' ? cleanCss() : noop())
    .pipe(gulp.dest(dirs.assets))
    .pipe(reload());
}

exports.scss = scss;

function svg() {
  return gulp
    .src(`${dirs.svg}/lsst_underline_logo.svg`)
    .pipe(gulp.dest(`${dirs.assets}`))
    .pipe(reload());
}

exports.svg = svg;

function icons() {
  return gulp
    .src(`${dirs.icons}/**/*.svg`, { base: dirs.icons })
    .pipe(
      rename(function(file) {
        var name = file.dirname.split(path.sep);
        name.push(file.basename);
        file.basename = name.join('-');
      })
    )
    .pipe(
      cheerio({
        run: function($) {
          $('[fill]').removeAttr('fill');
          // for JIRA icon
          $('.st0').removeClass('st0');
        },
        parserOptions: { xmlMode: true },
      })
    )
    .pipe(svgmin())
    .pipe(svgstore({ inlineSvg: true }))
    .pipe(gulp.dest(`${dirs.templates}`));
}

exports.icons = icons;

// make all assets needed deployment
const assets = gulp.parallel(js, scss, svg, icons);
exports.assets = assets;

// Runs `lander` render to create development HTML in _build
function html() {
  return run(
    `lander --pdf tests/data/LDM-nnn.pdf --lsstdoc tests/data/LDM-nnn.tex --build-dir ${
      dirs.dev
    } --ltd-product "ldm-nnn" --repo-branch master --repo-url https://github.com/lsst/ldm-nnn.git --extra-downloads tests/data/LDM-nnn.tex --docushare-url "https://ls.st/ldm-nnn*"`
  )
    .exec()
    .pipe(gulp.dest(dirs.dev + '/logs')) // makes the reload synchronous
    .pipe(reload());
}

exports.html = gulp.series(icons, html);

function server() {
  server = express();
  server.use(express.static(dirs.dev));
  server.listen(8000);
  browserSync({ proxy: 'localhost:8000' });
}

exports.server = server;

function watcher() {
  gulp.watch(
    [
      `${dirs.js}/**/*.js`,
      `${dirs.squaredScss}/**/*.scss`,
      `${dirs.scss}/**/*.scss`,
      `${dirs.templates}/*`,
      `${dirs.assets}/*`,
    ],
    {},
    gulp.series(assets, html)
  );
}

// compile a development project
exports.default = gulp.parallel(server, watcher);
