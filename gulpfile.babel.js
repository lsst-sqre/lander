import gulp from 'gulp';
import express from 'express';
import browserSync from 'browser-sync';
import sass from 'gulp-sass';
import autoprefixer from 'gulp-autoprefixer';
import minifyCss from 'gulp-minify-css';
import sourcemaps from 'gulp-sourcemaps';
var svgstore = require('gulp-svgstore');
var svgmin = require('gulp-svgmin');
var cheerio = require('gulp-cheerio');
var path = require('path');
var rename = require('gulp-rename');
var gutil = require('gulp-util');
var minimist = require('minimist');
var run = require('gulp-run');

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
const sassIncludes = [
  'node_modules',
];

// force page reload
function reload() {
  if (server) {
    return browserSync.reload({ stream: true });
  }

  return gutil.noop();
}

gulp.task('hello', () => console.log('Hello gulp!'));

gulp.task('environment', () => console.log(`${env}`));

gulp.task('js', () => {
  return run('./node_modules/.bin/webpack').exec()
    .pipe(reload());
});

gulp.task('scss', () => {
  return gulp.src(`${dirs.scss}/app.scss`)
    .pipe(env === 'dev' ? sourcemaps.init() : gutil.noop())
    .pipe(sass.sync({ includePaths: sassIncludes }).on('error', sass.logError))
    .pipe(autoprefixer())
    .pipe(env === 'dev' ? sourcemaps.write() : gutil.noop())
    .pipe(env === 'deploy' ? minifyCss() : gutil.noop())
    .pipe(gulp.dest(dirs.assets))
    .pipe(reload());
});

gulp.task('svg', () => {
  return gulp.src(`${dirs.svg}/lsst_underline_logo.svg`)
    .pipe(gulp.dest(`${dirs.assets}`))
    .pipe(reload());
});

gulp.task('icons', function () {
  return gulp
    .src(`${dirs.icons}/**/*.svg`, { base: dirs.icons })
    .pipe(rename(function (file) {
      var name = file.dirname.split(path.sep);
      name.push(file.basename);
      file.basename = name.join('-');
    }))
    .pipe(cheerio({
      run: function ($) {
        $('[fill]').removeAttr('fill');
        // for JIRA icon
        $('.st0').removeClass('st0');
      },
      parserOptions: { xmlMode: true }
    }))
    .pipe(svgmin())
    .pipe(svgstore({ inlineSvg: true }))
    .pipe(gulp.dest(`${dirs.templates}`));
});

// Runs `lander` render to create development HTML in _build
gulp.task('html', ['icons'], () => {
  return run(`lander --pdf tests/data/LDM-nnn.pdf --lsstdoc tests/data/LDM-nnn.tex --build-dir ${dirs.dev} --ltd-product "ldm-nnn" --repo-branch master --repo-url https://github.com/lsst/ldm-nnn.git --extra-downloads tests/data/LDM-nnn.tex --docushare-url "https://ls.st/ldm-nnn*"`).exec()
    .pipe(gulp.dest(`${dirs.dev}/logs`)) // makes the reload synchronous
    .pipe(reload());
});

gulp.task('server', () => {
  server = express();
  server.use(express.static(dirs.dev));
  server.listen(8000);
  browserSync({ proxy: 'localhost:8000' });
});

gulp.task('watch', () => {
  gulp.watch(`${dirs.js}/**/*.js`, ['js']);
  gulp.watch(`${dirs.squaredScss}/**/*.scss`, ['scss']);
  gulp.watch(`${dirs.scss}/**/*.scss`, ['scss']);
  gulp.watch(`${dirs.templates}/*`, ['html']);
  gulp.watch(`${dirs.assets}/*`, ['html']);
});

// compile a development project
gulp.task('default', ['js', 'scss', 'svg', 'html', 'watch', 'server']);

// make all assets needed deployment
gulp.task('assets', ['js', 'scss', 'svg', 'icons']);
