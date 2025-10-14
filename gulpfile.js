const gulp = require('gulp');
const concat = require('gulp-concat');
const uglify = require('gulp-uglify');
const cleanCSS = require('gulp-clean-css');

// Define paths
const paths = {
  scripts: {
    src: 'static/js/**/*.js',
    dest: 'build/js/'
  },
  styles: {
    src: 'static/css/**/*.css',
    dest: 'build/css/'
  }
};

// Task to minify JavaScript
function scripts() {
  return gulp.src(paths.scripts.src, { sourcemaps: true })
    .pipe(concat('bundle.js'))
    .pipe(uglify())
    .pipe(gulp.dest(paths.scripts.dest));
}

// Task to minify CSS
function styles() {
  return gulp.src(paths.styles.src, { sourcemaps: true })
    .pipe(concat('bundle.css'))
    .pipe(cleanCSS())
    .pipe(gulp.dest(paths.styles.dest));
}

// Watch files for changes
function watch() {
  gulp.watch(paths.scripts.src, scripts);
  gulp.watch(paths.styles.src, styles);
}

// Define complex tasks
const build = gulp.parallel(scripts, styles);
const serve = gulp.series(build, watch);

// Export tasks
exports.scripts = scripts;
exports.styles = styles;
exports.watch = watch;
exports.build = build;
exports.serve = serve;
exports.default = build;
