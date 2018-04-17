const gulp = require('gulp');
const bs = require('browser-sync');
const sass = require('gulp-sass');
const cssnano = require('gulp-cssnano');
const sourcemaps = require('gulp-sourcemaps');
const autoprefixer = require('gulp-autoprefixer');
const scsslint = require('gulp-scss-lint');
const rename = require('gulp-rename');

//-- path config
const stylesPath    = 'reddit/static/styles/**/*.scss';

// Sass Workflow
gulp.task('workflow', () => {
	return gulp.src(stylesPath)
    .pipe(scsslint())
		.pipe(sourcemaps.init())
		.pipe(sass().on('error', sass.logError))
		.pipe(autoprefixer({
			browsers: ['last 2 versions'],
			cascade: false
    }))
		.pipe(cssnano())
		.pipe(sourcemaps.write('./'))
		.pipe(rename({
			suffix: '.min'
		}))
	.pipe(gulp.dest('./reddit/static/styles/'))
  .pipe(bs.stream());
});

//-- Static server
gulp.task('dev', () => {
  bs.init({
    proxy: "radio.127.0.0.1.xip.io:8000",
    port: 3020,
    ui: {
      port: 3011
    },
    ghostMode: false
  });

  gulp.watch(stylesPath, ['workflow']).on('change', () => {
    bs.reload();
  });
  
});
